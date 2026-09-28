"""
Módulo para calcular las métricas de rendimiento de los algoritmos de planificación.
"""

from typing import Dict, Tuple
from dataclasses import dataclass
from algorithms import ScheduleResult, Process


@dataclass
class ProcessMetrics:
    """Métricas para un proceso individual"""
    process_id: str
    arrival_time: float
    burst_time: float
    priority: int
    first_response_time: float  # Tiempo de primera respuesta
    completion_time: float
    turnaround_time: float
    waiting_time: float
    response_time: float


@dataclass
class AlgorithmMetrics:
    """Métricas agregadas para un algoritmo"""
    algorithm_name: str
    individual_metrics: Dict[str, ProcessMetrics]
    avg_waiting_time: float
    avg_turnaround_time: float
    avg_response_time: float
    total_execution_time: float
    cpu_utilization: float
    throughput: float
    context_switches: int
    
    @property
    def process_count(self) -> int:
        return len(self.individual_metrics)


def calculate_metrics(schedule_result: ScheduleResult) -> AlgorithmMetrics:
    """
    Calcula todas las métricas basadas en el resultado de la simulación.
    
    Métricas por proceso:
    - Tiempo de llegada: arrival_time
    - Tiempo de ejecución: burst_time
    - Prioridad: priority
    - Primera respuesta: time when process first starts
    - Tiempo de finalización: completion_time
    - Turnaround Time = completion_time - arrival_time
    - Waiting Time = turnaround_time - burst_time
    - Response Time = first_response_time - arrival_time
    
    Métricas agregadas:
    - Tiempo medio de espera
    - Tiempo medio de retorno
    - Tiempo medio de respuesta
    - Tiempo total de ejecución
    - Utilización de CPU
    - Rendimiento (throughput)
    """
    
    individual_metrics = {}
    processes_by_id = {process.id: process for process in schedule_result.processes}
    if len(processes_by_id) != len(schedule_result.processes):
        raise ValueError("El resultado contiene IDs de procesos duplicados.")

    tolerance = 0.0001
    if not schedule_result.processes:
        return AlgorithmMetrics(
            algorithm_name=schedule_result.algorithm_name,
            individual_metrics={},
            avg_waiting_time=0,
            avg_turnaround_time=0,
            avg_response_time=0,
            total_execution_time=0,
            cpu_utilization=0,
            throughput=0,
            context_switches=0
        )

    for event in schedule_result.events:
        if event.process_id not in processes_by_id:
            raise ValueError(f"El evento referencia un proceso desconocido: {event.process_id}.")
        if event.end_time <= event.start_time:
            raise ValueError(f"El evento de {event.process_id} tiene una duración no positiva.")
        if event.start_time < processes_by_id[event.process_id].arrival_time - tolerance:
            raise ValueError(f"El proceso {event.process_id} comienza antes de su llegada.")

    ordered_events = sorted(schedule_result.events, key=lambda event: event.start_time)
    for previous, current in zip(ordered_events, ordered_events[1:]):
        if current.start_time < previous.end_time - tolerance:
            raise ValueError("El cronograma contiene eventos de CPU superpuestos.")
    if ordered_events and schedule_result.total_time < ordered_events[-1].end_time - tolerance:
        raise ValueError("El tiempo total no cubre el final del cronograma.")

    missing_completions = set(processes_by_id) - set(schedule_result.completion_times)
    missing_starts = set(processes_by_id) - set(schedule_result.start_times)
    if missing_completions:
        raise ValueError(f"Faltan tiempos de finalización para: {', '.join(sorted(missing_completions))}.")
    if missing_starts:
        raise ValueError(f"Faltan tiempos de inicio para: {', '.join(sorted(missing_starts))}.")
    
    for process in schedule_result.processes:
        arrival_time = process.arrival_time
        burst_time = process.burst_time
        priority = process.priority
        
        # Tiempo de finalización
        completion_time = schedule_result.completion_times[process.id]
        
        # Tiempo de primera respuesta (primera vez que empieza a ejecutarse)
        first_response_time = schedule_result.start_times[process.id]
        
        # Cálculos
        turnaround_time = completion_time - arrival_time
        waiting_time = turnaround_time - burst_time
        response_time = first_response_time - arrival_time
        
        process_events = [event for event in schedule_result.events if event.process_id == process.id]
        executed_time = sum(event.end_time - event.start_time for event in process_events)
        if abs(executed_time - burst_time) > tolerance:
            raise ValueError(
                f"El proceso {process.id} ejecutó {executed_time:.4f} unidades; "
                f"se esperaban {burst_time:.4f}."
            )
        if abs(completion_time - max(event.end_time for event in process_events)) > tolerance:
            raise ValueError(f"El tiempo de finalización de {process.id} no coincide con su cronograma.")
        if abs(first_response_time - min(event.start_time for event in process_events)) > tolerance:
            raise ValueError(f"El tiempo de respuesta inicial de {process.id} no coincide con su cronograma.")
        if waiting_time < -tolerance or response_time < -tolerance or turnaround_time < -tolerance:
            raise ValueError(
                f"Métrica negativa para {process.id}: espera={waiting_time:.4f}, "
                f"retorno={turnaround_time:.4f}, respuesta={response_time:.4f}."
            )
        
        individual_metrics[process.id] = ProcessMetrics(
            process_id=process.id,
            arrival_time=arrival_time,
            burst_time=burst_time,
            priority=priority,
            first_response_time=first_response_time,
            completion_time=completion_time,
            turnaround_time=turnaround_time,
            waiting_time=waiting_time,
            response_time=response_time
        )
    
    # Calcular métricas agregadas
    if not individual_metrics:
        return AlgorithmMetrics(
            algorithm_name=schedule_result.algorithm_name,
            individual_metrics={},
            avg_waiting_time=0,
            avg_turnaround_time=0,
            avg_response_time=0,
            total_execution_time=0,
            cpu_utilization=0,
            throughput=0,
            context_switches=0
        )
    
    # Promedios
    avg_waiting_time = sum(m.waiting_time for m in individual_metrics.values()) / len(individual_metrics)
    avg_turnaround_time = sum(m.turnaround_time for m in individual_metrics.values()) / len(individual_metrics)
    avg_response_time = sum(m.response_time for m in individual_metrics.values()) / len(individual_metrics)
    
    total_execution_time = schedule_result.total_time
    
    # Calcular tiempo total de CPU ocupada (sin idle)
    total_busy_time = sum(p.burst_time for p in schedule_result.processes)
    
    # Utilización de CPU = tiempo ocupado / tiempo total (incluyendo idle)
    if total_execution_time > 0:
        cpu_utilization = (total_busy_time / total_execution_time) * 100
    else:
        cpu_utilization = 0
    if cpu_utilization > 100 + tolerance:
        raise ValueError("La utilización de CPU supera el 100%; el cronograma es incoherente.")
    
    # Throughput = número de procesos completados / tiempo total
    if total_execution_time > 0:
        throughput = len(individual_metrics) / total_execution_time
    else:
        throughput = 0
    
    return AlgorithmMetrics(
        algorithm_name=schedule_result.algorithm_name,
        individual_metrics=individual_metrics,
        avg_waiting_time=avg_waiting_time,
        avg_turnaround_time=avg_turnaround_time,
        avg_response_time=avg_response_time,
        total_execution_time=total_execution_time,
        cpu_utilization=cpu_utilization,
        throughput=throughput,
        context_switches=schedule_result.context_switches
    )


def format_metrics_table(metrics: AlgorithmMetrics) -> str:
    """Retorna una representación formateada de las métricas"""
    result = f"\n{'='*80}\n"
    result += f"Algoritmo: {metrics.algorithm_name}\n"
    result += f"{'='*80}\n\n"
    
    # Métricas individuales
    result += "Métricas por proceso:\n"
    result += f"{'PID':<6} {'Llegada':<10} {'Ejecución':<12} {'Prior':<8} "
    result += f"{'Respuesta':<12} {'Final':<10} {'Retorno':<10} {'Espera':<10}\n"
    result += "-" * 90 + "\n"
    
    for pid in sorted(metrics.individual_metrics.keys()):
        m = metrics.individual_metrics[pid]
        result += f"{m.process_id:<6} {m.arrival_time:<10.2f} {m.burst_time:<12.2f} "
        result += f"{m.priority:<8} {m.response_time:<12.2f} {m.completion_time:<10.2f} "
        result += f"{m.turnaround_time:<10.2f} {m.waiting_time:<10.2f}\n"
    
    result += "\nMétricas agregadas:\n"
    result += f"  Tiempo medio de espera:      {metrics.avg_waiting_time:.2f}\n"
    result += f"  Tiempo medio de retorno:     {metrics.avg_turnaround_time:.2f}\n"
    result += f"  Tiempo medio de respuesta:   {metrics.avg_response_time:.2f}\n"
    result += f"  Tiempo total de ejecución:   {metrics.total_execution_time:.2f}\n"
    result += f"  Utilización de CPU:          {metrics.cpu_utilization:.2f}%\n"
    result += f"  Rendimiento (throughput):    {metrics.throughput:.4f} procs/unidad\n"
    result += f"  Cambios de contexto:         {metrics.context_switches}\n"
    result += f"{'='*80}\n"
    
    return result


def get_comparison_table(algorithms_metrics: Dict[str, AlgorithmMetrics]) -> Dict:
    """
    Prepara una tabla de comparación entre algoritmos.
    Retorna un diccionario con datos para la visualización.
    """
    comparison_data = {
        'Algoritmo': [],
        'Espera Media': [],
        'Retorno Medio': [],
        'Respuesta Media': [],
        'Utilización CPU': [],
        'Throughput': [],
        'Cambios de Contexto': []
    }
    
    for algo_name, metrics in algorithms_metrics.items():
        comparison_data['Algoritmo'].append(algo_name)
        comparison_data['Espera Media'].append(f"{metrics.avg_waiting_time:.2f}")
        comparison_data['Retorno Medio'].append(f"{metrics.avg_turnaround_time:.2f}")
        comparison_data['Respuesta Media'].append(f"{metrics.avg_response_time:.2f}")
        comparison_data['Utilización CPU'].append(f"{metrics.cpu_utilization:.2f}%")
        comparison_data['Throughput'].append(f"{metrics.throughput:.4f}")
        comparison_data['Cambios de Contexto'].append(str(metrics.context_switches))
    
    return comparison_data


def get_best_algorithms(algorithms_metrics: Dict[str, AlgorithmMetrics]) -> Dict[str, str]:
    """
    Identifica los mejores algoritmos para cada métrica.
    Retorna un diccionario con la métrica y el algoritmo ganador.
    """
    if not algorithms_metrics:
        return {}
    
    best = {}
    
    # Menor tiempo de espera
    min_waiting = min(algorithms_metrics.items(), 
                      key=lambda x: x[1].avg_waiting_time)
    best['Menor espera media'] = f"{min_waiting[0]} ({min_waiting[1].avg_waiting_time:.2f})"
    
    # Menor tiempo de retorno
    min_turnaround = min(algorithms_metrics.items(),
                        key=lambda x: x[1].avg_turnaround_time)
    best['Menor retorno medio'] = f"{min_turnaround[0]} ({min_turnaround[1].avg_turnaround_time:.2f})"
    
    # Menor tiempo de respuesta
    min_response = min(algorithms_metrics.items(),
                      key=lambda x: x[1].avg_response_time)
    best['Menor respuesta media'] = f"{min_response[0]} ({min_response[1].avg_response_time:.2f})"
    
    # Mayor utilización de CPU
    max_utilization = max(algorithms_metrics.items(),
                         key=lambda x: x[1].cpu_utilization)
    best['Mayor utilización CPU'] = f"{max_utilization[0]} ({max_utilization[1].cpu_utilization:.2f}%)"
    
    # Mayor throughput
    max_throughput = max(algorithms_metrics.items(),
                        key=lambda x: x[1].throughput)
    best['Mayor throughput'] = f"{max_throughput[0]} ({max_throughput[1].throughput:.4f})"
    
    return best
