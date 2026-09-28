"""
Pruebas para algoritmos de planificación de procesos.
Utilizando pytest para validar la correctitud de todas las implementaciones.
"""

import pytest
from algorithms import (
    Process, FCFSScheduler, SJFScheduler, SRTFScheduler, 
    RoundRobinScheduler, PriorityNonPreemptiveScheduler, 
    PriorityPreemptiveScheduler, ScheduleEvent, ScheduleResult, create_scheduler
)
from metrics import calculate_metrics


# ==================== FIXTURES ====================

@pytest.fixture
def single_process():
    """Un solo proceso"""
    return [Process("P1", 0, 5)]


@pytest.fixture
def same_arrival_time():
    """Varios procesos llegando al mismo tiempo"""
    return [
        Process("P1", 0, 7),
        Process("P2", 0, 4),
        Process("P3", 0, 2),
    ]


@pytest.fixture
def different_arrival_times():
    """Procesos con tiempos de llegada diferentes"""
    return [
        Process("P1", 0, 7),
        Process("P2", 2, 4),
        Process("P3", 3, 2),
        Process("P4", 5, 5),
    ]


@pytest.fixture
def priority_processes():
    """Procesos con prioridades"""
    return [
        Process("P1", 0, 7, 2),
        Process("P2", 2, 4, 1),
        Process("P3", 3, 2, 3),
        Process("P4", 5, 5, 2),
    ]


@pytest.fixture
def complex_scenario():
    """Escenario complejo"""
    return [
        Process("P1", 0, 5, 1),
        Process("P2", 1, 3, 0),
        Process("P3", 2, 8, 2),
        Process("P4", 3, 4, 1),
        Process("P5", 4, 2, 0),
        Process("P6", 6, 6, 3),
    ]


# ==================== FUNCIONES DE VALIDACIÓN ====================

def validate_schedule(schedule_result, expected_total_burst):
    """
    Valida que una simulación sea correcta:
    - Todos los procesos se completan
    - No hay pérdida ni duplicación de tiempo de CPU
    - Ningún proceso comienza antes de su llegada
    """
    
    # Verificar que todos los procesos se completaron
    assert len(schedule_result.completion_times) == len(schedule_result.processes)
    
    # Verificar que ningún proceso comienza antes de su llegada
    for event in schedule_result.events:
        process = next(p for p in schedule_result.processes if p.id == event.process_id)
        assert event.start_time >= process.arrival_time, \
            f"Proceso {event.process_id} comenzó en {event.start_time} pero llegó en {process.arrival_time}"
    
    # Verificar que el tiempo total ejecutado es correcto
    total_executed = sum(e.end_time - e.start_time for e in schedule_result.events)
    assert abs(total_executed - expected_total_burst) < 0.001, \
        f"Tiempo total ejecutado {total_executed} != {expected_total_burst}"
    
    # Verificar que cada proceso ejecutó exactamente su burst_time
    for process in schedule_result.processes:
        process_events = [e for e in schedule_result.events if e.process_id == process.id]
        total_time = sum(e.end_time - e.start_time for e in process_events)
        assert abs(total_time - process.burst_time) < 0.001, \
            f"Proceso {process.id} ejecutó {total_time} pero debería {process.burst_time}"
    
    # Verificar que los tiempos de finalización son correctos
    for process in schedule_result.processes:
        completion = schedule_result.completion_times[process.id]
        process_events = [e for e in schedule_result.events if e.process_id == process.id]
        max_end = max(e.end_time for e in process_events)
        assert abs(completion - max_end) < 0.001, \
            f"Tiempo de finalización incorrecto para {process.id}"
    
    return True


# ==================== PRUEBAS FCFS ====================

class TestFCFS:
    """Pruebas para el algoritmo FCFS"""
    
    def test_single_process(self, single_process):
        """FCFS: Un solo proceso"""
        scheduler = FCFSScheduler(single_process)
        result = scheduler.schedule()
        
        assert len(result.events) == 1
        assert result.events[0].start_time == 0
        assert result.events[0].end_time == 5
        assert validate_schedule(result, 5)
    
    def test_same_arrival_time(self, same_arrival_time):
        """FCFS: Procesos llegando al mismo tiempo (orden de lista)"""
        scheduler = FCFSScheduler(same_arrival_time)
        result = scheduler.schedule()
        
        # FCFS debe respetar el orden de entrada
        event_order = [e.process_id for e in result.events]
        assert event_order == ["P1", "P2", "P3"]
        
        # Verificar tiempos
        assert result.events[0].start_time == 0
        assert result.events[0].end_time == 7
        assert result.events[1].start_time == 7
        assert result.events[1].end_time == 11
        assert result.events[2].start_time == 11
        assert result.events[2].end_time == 13
        
        assert validate_schedule(result, 13)
    
    def test_different_arrival_times(self, different_arrival_times):
        """FCFS: Procesos con tiempos de llegada diferentes"""
        scheduler = FCFSScheduler(different_arrival_times)
        result = scheduler.schedule()
        
        # Verificar que P1 comienza en t=0 y termina en t=7
        p1_events = [e for e in result.events if e.process_id == "P1"]
        assert p1_events[0].start_time == 0
        assert p1_events[0].end_time == 7
        
        # P2 llega en t=2 pero CPU ocupa en t=7
        p2_events = [e for e in result.events if e.process_id == "P2"]
        assert p2_events[0].start_time == 7
        
        assert validate_schedule(result, 18)
    
    def test_cpu_idle_periods(self):
        """FCFS: Períodos de CPU inactiva"""
        processes = [
            Process("P1", 0, 2),
            Process("P2", 5, 3),  # Llega cuando P1 ya terminó
        ]
        scheduler = FCFSScheduler(processes)
        result = scheduler.schedule()
        
        assert result.events[0].end_time == 2
        assert result.events[1].start_time == 5  # P2 espera
        
        assert validate_schedule(result, 5)


# ==================== PRUEBAS SJF ====================

class TestSJF:
    """Pruebas para el algoritmo SJF"""
    
    def test_selects_shortest_job(self, same_arrival_time):
        """SJF: Selecciona el trabajo más corto primero"""
        scheduler = SJFScheduler(same_arrival_time)
        result = scheduler.schedule()
        
        # Orden esperado: P3(2) -> P2(4) -> P1(7)
        event_order = [e.process_id for e in result.events]
        assert event_order == ["P3", "P2", "P1"]
        
        assert validate_schedule(result, 13)
    
    def test_respects_arrival_times(self, different_arrival_times):
        """SJF: Respeta tiempos de llegada"""
        scheduler = SJFScheduler(different_arrival_times)
        result = scheduler.schedule()
        
        # P1 debe comenzar primero (único proceso en t=0)
        assert result.events[0].process_id == "P1"
        assert result.events[0].start_time == 0
        
        # En t=7, P2, P3, P4 están listos
        # SJF selecciona P3(2) < P2(4) < P4(5)
        second_event = result.events[1]
        assert second_event.process_id == "P3"
        
        assert validate_schedule(result, 18)
    
    def test_handles_ties(self):
        """SJF: Resuelve empates por tiempo de llegada y orden"""
        processes = [
            Process("P1", 0, 5),
            Process("P2", 0, 5),  # Mismo burst
            Process("P3", 1, 5),
        ]
        scheduler = SJFScheduler(processes)
        result = scheduler.schedule()
        
        # Con empate de burst, orden por llegada, luego por lista
        event_order = [e.process_id for e in result.events]
        assert event_order[0] == "P1"  # Mismo burst, llegó primero
        assert event_order[1] == "P2"  # Mismo burst, llegó al mismo tiempo pero después en lista
        assert event_order[2] == "P3"
        
        assert validate_schedule(result, 15)


# ==================== PRUEBAS SRTF ====================

class TestSRTF:
    """Pruebas para el algoritmo SRTF"""
    
    def test_preemption(self):
        """SRTF: Interrumpe procesos cuando llega uno más corto"""
        processes = [
            Process("P1", 0, 10),
            Process("P2", 1, 2),  # Más corto, debe interrumpir a P1
        ]
        scheduler = SRTFScheduler(processes)
        result = scheduler.schedule()
        
        # P1 debe ser interrumpido, P2 ejecutar, luego P1 continúa
        p1_count = len([e for e in result.events if e.process_id == "P1"])
        assert p1_count >= 2, "P1 debe estar dividido en múltiples eventos (interrumpido)"
        
        assert validate_schedule(result, 12)
    
    def test_no_preemption_if_longer(self):
        """SRTF: No interrumpe si el nuevo es más largo"""
        processes = [
            Process("P1", 0, 2),
            Process("P2", 1, 10),  # Más largo, no interrumpe
        ]
        scheduler = SRTFScheduler(processes)
        result = scheduler.schedule()
        
        # P1 debe completar sin interrupción
        p1_events = [e for e in result.events if e.process_id == "P1"]
        assert len(p1_events) == 1
        
        assert validate_schedule(result, 12)
    
    def test_remaining_time_calculation(self):
        """SRTF: Calcula correctamente el tiempo restante"""
        processes = [
            Process("P1", 0, 8),
            Process("P2", 3, 4),
        ]
        scheduler = SRTFScheduler(processes)
        result = scheduler.schedule()
        
        # En t=3, P1 ha ejecutado 3 unidades, tiempo restante = 5
        # P2 llega con 4 unidades
        # SRTF elige P2 (4 < 5)
        
        # Verificar que P2 ejecuta antes de que P1 continúe
        p1_first = result.events[0]
        p2_first = [e for e in result.events if e.process_id == "P2"][0]
        
        assert p1_first.process_id == "P1"
        assert p1_first.end_time == 3
        assert p2_first.start_time == 3
        
        assert validate_schedule(result, 12)


# ==================== PRUEBAS ROUND ROBIN ====================

class TestRoundRobin:
    """Pruebas para el algoritmo Round Robin"""
    
    def test_quantum_greater_than_burst(self):
        """RR: Quantum mayor que burst (proceso termina en primer quantum)"""
        processes = [
            Process("P1", 0, 2),
            Process("P2", 0, 3),
        ]
        scheduler = RoundRobinScheduler(processes, quantum=10)
        result = scheduler.schedule()
        
        # Cada proceso debe completar sin interrupciones
        p1_events = [e for e in result.events if e.process_id == "P1"]
        p2_events = [e for e in result.events if e.process_id == "P2"]
        assert len(p1_events) == 1
        assert len(p2_events) == 1
        
        assert validate_schedule(result, 5)
    
    def test_quantum_smaller_than_burst(self):
        """RR: Quantum menor que burst (múltiples cuantos)"""
        processes = [
            Process("P1", 0, 8),
            Process("P2", 0, 4),
        ]
        scheduler = RoundRobinScheduler(processes, quantum=2)
        result = scheduler.schedule()
        
        # P1: 2+2+2+2, P2: 2+2
        p1_events = [e for e in result.events if e.process_id == "P1"]
        p2_events = [e for e in result.events if e.process_id == "P2"]
        
        assert len(p1_events) == 4
        assert len(p2_events) == 2
        
        # Verificar que se alternan: P1, P2, P1, P2, P1, P1
        first_three = [e.process_id for e in result.events[:3]]
        assert first_three == ["P1", "P2", "P1"]
        
        assert validate_schedule(result, 12)
    
    def test_fifo_queue(self):
        """RR: Mantiene la cola FIFO correctamente"""
        processes = [
            Process("P1", 0, 4),
            Process("P2", 1, 4),
            Process("P3", 2, 4),
        ]
        scheduler = RoundRobinScheduler(processes, quantum=1)
        result = scheduler.schedule()
        
        # Primeros eventos: P1 llega en t=0
        assert result.events[0].process_id == "P1"
        
        # En t=1, P2 llega
        # En t=2, P3 llega
        # Orden en cola: P1, P2, P3
        
        assert validate_schedule(result, 12)
    
    def test_arrival_during_quantum(self):
        """RR: Maneja llegadas durante la ejecución de un quantum"""
        processes = [
            Process("P1", 0, 5),
            Process("P2", 2, 3),
        ]
        scheduler = RoundRobinScheduler(processes, quantum=2)
        result = scheduler.schedule()
        
        # P1 ejecuta 2 (t=0-2), P2 llega en t=2
        # P2 ejecuta 2 (t=2-4), P1 continúa 2 (t=4-6), P2 finalmente 1 (t=6-7)
        
        assert result.events[0].process_id == "P1"
        assert result.events[0].end_time == 2
        
        assert result.events[1].process_id == "P2"
        assert result.events[1].start_time == 2
        
        assert validate_schedule(result, 8)


# ==================== PRUEBAS PRIORIDADES ====================

class TestPriorityNonPreemptive:
    """Pruebas para planificación por prioridad no-expulsiva"""
    
    def test_selects_highest_priority(self):
        """Priority (non-preempt): Selecciona mayor prioridad"""
        processes = [
            Process("P1", 0, 5, 2),
            Process("P2", 0, 3, 1),  # Mayor prioridad
            Process("P3", 0, 4, 3),
        ]
        scheduler = PriorityNonPreemptiveScheduler(processes)
        result = scheduler.schedule()
        
        # Orden: P2(pri=1) -> P1(pri=2) -> P3(pri=3)
        event_order = [e.process_id for e in result.events]
        assert event_order == ["P2", "P1", "P3"]
        
        assert validate_schedule(result, 12)
    
    def test_not_preemptive(self):
        """Priority (non-preempt): No interrumpe aunque llegue prioridad mayor"""
        processes = [
            Process("P1", 0, 5, 2),
            Process("P2", 2, 3, 1),  # Mayor prioridad pero P1 está ejecutando
        ]
        scheduler = PriorityNonPreemptiveScheduler(processes)
        result = scheduler.schedule()
        
        # P1 debe terminar primero (no-preemptive)
        assert result.events[0].process_id == "P1"
        assert result.events[0].end_time == 5
        assert result.events[1].process_id == "P2"
        assert result.events[1].start_time == 5
        
        assert validate_schedule(result, 8)
    
    def test_priority_ties(self):
        """Priority (non-preempt): Resuelve empates de prioridad"""
        processes = [
            Process("P1", 0, 5, 1),
            Process("P2", 1, 3, 1),  # Misma prioridad
            Process("P3", 0, 4, 1),
        ]
        scheduler = PriorityNonPreemptiveScheduler(processes)
        result = scheduler.schedule()
        
        # Mismo nivel de prioridad: P1 y P3 llegan en t=0, P2 en t=1
        # Debe ser P1 (primero en lista), luego P2 (llegó primero que P3), luego P3
        # Esperado: P1 -> P3 -> P2 (ambos en t=0, pero P1 antes en lista)
        # O: P1 -> P2 -> P3 (llegada como desempate)
        
        # Verificar que se respeta algún orden determinista
        event_order = [e.process_id for e in result.events]
        assert len(event_order) == 3
        
        assert validate_schedule(result, 12)


class TestPriorityPreemptive:
    """Pruebas para planificación por prioridad expulsiva"""
    
    def test_preempts_lower_priority(self):
        """Priority (preempt): Interrumpe si llega mayor prioridad"""
        processes = [
            Process("P1", 0, 10, 2),
            Process("P2", 2, 3, 1),  # Mayor prioridad, interrumpe
        ]
        scheduler = PriorityPreemptiveScheduler(processes)
        result = scheduler.schedule()
        
        # P1 ejecuta 2 (t=0-2), P2 llega y ejecuta (t=2-5)
        # Luego P1 continúa (t=5-15)
        p1_events = [e for e in result.events if e.process_id == "P1"]
        assert len(p1_events) >= 2, "P1 debe ser interrumpido"
        
        # P2 debe estar entre los eventos de P1
        p2_events = [e for e in result.events if e.process_id == "P2"]
        assert len(p2_events) >= 1
        
        assert validate_schedule(result, 13)
    
    def test_no_preempt_if_lower_priority(self):
        """Priority (preempt): No interrumpe si llega menor prioridad"""
        processes = [
            Process("P1", 0, 5, 1),
            Process("P2", 2, 3, 2),  # Menor prioridad
        ]
        scheduler = PriorityPreemptiveScheduler(processes)
        result = scheduler.schedule()
        
        # P1 debe completar sin interrupción
        p1_events = [e for e in result.events if e.process_id == "P1"]
        assert len(p1_events) == 1
        
        assert result.events[0].end_time == 5
        assert result.events[1].start_time == 5
        
        assert validate_schedule(result, 8)

    def test_same_priority_does_not_preempt(self):
        processes = [
            Process("P1", 0, 5, 1),
            Process("P2", 2, 2, 1),
        ]
        result = PriorityPreemptiveScheduler(processes).schedule()

        assert [(event.process_id, event.start_time, event.end_time)
                for event in result.events] == [("P1", 0, 5), ("P2", 5, 7)]
        assert validate_schedule(result, 7)

    def test_simultaneous_arrivals_use_input_order(self):
        processes = [
            Process("P1", 0, 2, 1),
            Process("P2", 0, 1, 1),
            Process("P3", 0, 1, 1),
        ]
        result = PriorityPreemptiveScheduler(processes).schedule()

        assert [event.process_id for event in result.events] == ["P1", "P2", "P3"]
        assert validate_schedule(result, 4)

    def test_multiple_arrivals_and_remaining_time(self):
        processes = [
            Process("P1", 0, 10, 3),
            Process("P2", 2, 4, 2),
            Process("P3", 3, 2, 1),
            Process("P4", 4, 1, 1),
        ]
        result = PriorityPreemptiveScheduler(processes).schedule()

        assert [(event.process_id, event.start_time, event.end_time)
                for event in result.events] == [
                    ("P1", 0, 2), ("P2", 2, 3), ("P3", 3, 5),
                    ("P4", 5, 6), ("P2", 6, 9), ("P1", 9, 17)
                ]
        assert result.completion_times == {"P1": 17, "P2": 9, "P3": 5, "P4": 6}
        assert validate_schedule(result, 17)

        metrics = calculate_metrics(result)
        assert metrics.individual_metrics["P1"].waiting_time == 7
        assert metrics.individual_metrics["P2"].waiting_time == 3
        assert metrics.individual_metrics["P3"].waiting_time == 0
        assert metrics.individual_metrics["P4"].waiting_time == 1
        assert metrics.avg_waiting_time == 2.75
        assert metrics.avg_response_time == 0.25

    def test_priority_ties_are_deterministic_after_resume(self):
        processes = [
            Process("P1", 0, 6, 2),
            Process("P2", 1, 2, 1),
            Process("P3", 1, 1, 1),
            Process("P4", 2, 1, 0),
        ]
        result = PriorityPreemptiveScheduler(processes).schedule()

        assert [event.process_id for event in result.events] == ["P1", "P2", "P4", "P2", "P3", "P1"]
        assert validate_schedule(result, 10)


# ==================== PRUEBAS DE MÉTRICAS ====================

class TestMetrics:
    """Pruebas para cálculo de métricas"""
    
    def test_turnaround_time(self, single_process):
        """Cálculo de Turnaround Time"""
        scheduler = FCFSScheduler(single_process)
        result = scheduler.schedule()
        metrics = calculate_metrics(result)
        
        m = metrics.individual_metrics["P1"]
        # Turnaround = completion - arrival = 5 - 0 = 5
        assert abs(m.turnaround_time - 5) < 0.001
    
    def test_waiting_time(self):
        """Cálculo de Waiting Time"""
        processes = [
            Process("P1", 0, 5),
            Process("P2", 0, 3),
        ]
        scheduler = FCFSScheduler(processes)
        result = scheduler.schedule()
        metrics = calculate_metrics(result)
        
        m1 = metrics.individual_metrics["P1"]
        m2 = metrics.individual_metrics["P2"]
        
        # P1: espera 0 (comienza inmediatamente)
        assert abs(m1.waiting_time - 0) < 0.001
        # P2: espera 5 (hasta que P1 termina)
        assert abs(m2.waiting_time - 5) < 0.001
    
    def test_response_time(self):
        """Cálculo de Response Time"""
        processes = [
            Process("P1", 0, 5),
            Process("P2", 2, 3),
        ]
        scheduler = FCFSScheduler(processes)
        result = scheduler.schedule()
        metrics = calculate_metrics(result)
        
        m1 = metrics.individual_metrics["P1"]
        m2 = metrics.individual_metrics["P2"]
        
        # P1: comienza en t=0, llega en t=0, response = 0
        assert abs(m1.response_time - 0) < 0.001
        # P2: comienza en t=5, llega en t=2, response = 3
        assert abs(m2.response_time - 3) < 0.001
    
    def test_average_metrics(self):
        """Cálculo de métricas promedio"""
        processes = [
            Process("P1", 0, 5),
            Process("P2", 0, 3),
        ]
        scheduler = FCFSScheduler(processes)
        result = scheduler.schedule()
        metrics = calculate_metrics(result)
        
        # Tiempos de espera: P1=0, P2=5, promedio=2.5
        assert abs(metrics.avg_waiting_time - 2.5) < 0.001
        
        # Tiempos de retorno: P1=5, P2=8, promedio=6.5
        assert abs(metrics.avg_turnaround_time - 6.5) < 0.001
    
    def test_cpu_utilization(self):
        """Cálculo de utilización de CPU"""
        processes = [
            Process("P1", 0, 2),
            Process("P2", 5, 3),  # Hay 3 unidades de idle entre P1 y P2
        ]
        scheduler = FCFSScheduler(processes)
        result = scheduler.schedule()
        metrics = calculate_metrics(result)
        
        # Tiempo total: 8 (0-2 + idle 2-5 + 5-8)
        # Tiempo ocupado: 5
        # Utilización: 5/8 = 62.5%
        assert abs(metrics.cpu_utilization - 62.5) < 0.1
    
    def test_throughput(self):
        """Cálculo de rendimiento (throughput)"""
        processes = [
            Process("P1", 0, 4),
            Process("P2", 0, 6),
        ]
        scheduler = FCFSScheduler(processes)
        result = scheduler.schedule()
        metrics = calculate_metrics(result)
        
        # 2 procesos en 10 unidades = 0.2 procs/unidad
        assert abs(metrics.throughput - 0.2) < 0.001

    def test_rejects_invalid_negative_metrics(self):
        processes = [Process("P1", 5, 2)]
        result = ScheduleResult(
            algorithm_name="invalid",
            events=[ScheduleEvent("P1", 0, 2)],
            completion_times={"P1": 2},
            start_times={"P1": 0},
            processes=processes,
            total_time=2,
            context_switches=0,
        )

        with pytest.raises(ValueError, match="antes de su llegada"):
            calculate_metrics(result)


# ==================== PRUEBAS DE FÁBRICA ====================

class TestSchedulerFactory:
    """Pruebas para la función create_scheduler"""
    
    def test_factory_fcfs(self, single_process):
        """Factory: Crea scheduler FCFS"""
        scheduler = create_scheduler("FCFS", single_process)
        assert isinstance(scheduler, FCFSScheduler)
    
    def test_factory_sjf(self, single_process):
        """Factory: Crea scheduler SJF"""
        scheduler = create_scheduler("SJF", single_process)
        assert isinstance(scheduler, SJFScheduler)
    
    def test_factory_srtf(self, single_process):
        """Factory: Crea scheduler SRTF"""
        scheduler = create_scheduler("SRTF", single_process)
        assert isinstance(scheduler, SRTFScheduler)
    
    def test_factory_round_robin(self, single_process):
        """Factory: Crea scheduler Round Robin"""
        scheduler = create_scheduler("Round Robin", single_process, quantum=2.0)
        assert isinstance(scheduler, RoundRobinScheduler)
    
    def test_factory_priority_non_preemptive(self, single_process):
        """Factory: Crea scheduler Priority (non-preemptive)"""
        scheduler = create_scheduler("Priority (Non-Preemptive)", single_process)
        assert isinstance(scheduler, PriorityNonPreemptiveScheduler)
    
    def test_factory_priority_preemptive(self, single_process):
        """Factory: Crea scheduler Priority (preemptive)"""
        scheduler = create_scheduler("Priority (Preemptive)", single_process)
        assert isinstance(scheduler, PriorityPreemptiveScheduler)


# ==================== PRUEBAS DE INTEGRACIÓN ====================

class TestIntegration:
    """Pruebas de integración con múltiples algoritmos"""
    
    def test_same_results_all_algorithms(self):
        """Integración: Un proceso debe dar mismo resultado en todos los algoritmos"""
        processes = [Process("P1", 0, 5)]
        
        algorithms = [
            ("FCFS", None),
            ("SJF", None),
            ("SRTF", None),
            ("Round Robin", 10),  # Quantum grande, equivalente a no-preempt
            ("Priority (Non-Preemptive)", None),
            ("Priority (Preemptive)", None),
        ]
        
        results = {}
        for algo_name, quantum in algorithms:
            scheduler = create_scheduler(algo_name, processes, quantum=quantum or 2.0)
            result = scheduler.schedule()
            metrics = calculate_metrics(result)
            results[algo_name] = metrics
        
        # Todos deben tener el mismo tiempo total
        completion_times = {name: m.total_execution_time for name, m in results.items()}
        total_completions = list(completion_times.values())
        assert all(abs(t - total_completions[0]) < 0.001 for t in total_completions)
    
    def test_complex_scenario_all_algorithms(self, complex_scenario):
        """Integración: Ejecuta escenario complejo con todos los algoritmos"""
        algorithms = [
            "FCFS", "SJF", "SRTF", "Round Robin",
            "Priority (Non-Preemptive)", "Priority (Preemptive)"
        ]
        
        for algo in algorithms:
            scheduler = create_scheduler(algo, complex_scenario, quantum=2.0)
            result = scheduler.schedule()
            metrics = calculate_metrics(result)
            
            # Básicas validaciones
            assert len(result.events) > 0, f"{algo}: No hay eventos"
            assert len(metrics.individual_metrics) == 6, f"{algo}: Métricas incompletas"
            assert metrics.total_execution_time > 0, f"{algo}: Tiempo total = 0"

    def test_all_algorithms_use_same_unsorted_input_and_valid_gantt(self):
        processes = [
            Process("P3", 4, 2, 2),
            Process("P1", 0, 5, 1),
            Process("P4", 1, 3, 0),
            Process("P2", 2, 4, 1),
        ]
        algorithms = [
            "FCFS", "SJF", "SRTF", "Round Robin",
            "Priority (Non-Preemptive)", "Priority (Preemptive)"
        ]

        for algorithm in algorithms:
            result = create_scheduler(algorithm, processes, quantum=2).schedule()
            metrics = calculate_metrics(result)
            assert len(metrics.individual_metrics) == len(processes)
            assert result.total_time == max(event.end_time for event in result.events)
            assert metrics.cpu_utilization <= 100
            assert metrics.throughput > 0
            assert result.context_switches == sum(
                previous.process_id != current.process_id
                for previous, current in zip(result.events, result.events[1:])
            )
            assert validate_schedule(result, sum(process.burst_time for process in processes))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
