"""
Módulo de algoritmos de planificación de procesos.
Implementa los algoritmos: FCFS, SJF, SRTF, Round Robin, Priority (preemptive y no-preemptive)
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class ScheduleEventType(Enum):
    """Tipos de eventos en la simulación"""
    START = "start"
    END = "end"
    PREEMPT = "preempt"
    RESUME = "resume"


@dataclass
class Process:
    """Representa un proceso a ser planificado"""
    id: str
    arrival_time: float
    burst_time: float
    priority: int = 0
    remaining_time: float = field(init=False)
    
    def __post_init__(self):
        self.remaining_time = self.burst_time


@dataclass
class ScheduleEvent:
    """Representa un evento en el diagrama de Gantt"""
    process_id: str
    start_time: float
    end_time: float
    event_type: ScheduleEventType = ScheduleEventType.START


@dataclass
class ScheduleResult:
    """Resultado de la simulación de un algoritmo"""
    algorithm_name: str
    events: List[ScheduleEvent]
    completion_times: dict  # {process_id: completion_time}
    start_times: dict  # {process_id: first_start_time}
    processes: List[Process]
    total_time: float
    context_switches: int


class ProcessScheduler:
    """Clase base para planificadores de procesos"""
    
    def __init__(self, processes: List[Process]):
        self.processes = [Process(p.id, p.arrival_time, p.burst_time, p.priority)
                          for p in processes]
        self.processes.sort(key=lambda p: p.arrival_time)
        self.current_time = 0.0
        self.events: List[ScheduleEvent] = []
        self.completion_times = {}
        self.start_times = {}
        self.last_process_id = None
        self.context_switches = 0
    
    def _add_event(self, process_id: str, start: float, end: float, 
                   event_type: ScheduleEventType = ScheduleEventType.START):
        """Añade un evento al diagrama de Gantt"""
        self.events.append(ScheduleEvent(process_id, start, end, event_type))
    
    def _record_start_time(self, process_id: str, time: float):
        """Registra el tiempo de primera ejecución de un proceso"""
        if process_id not in self.start_times:
            self.start_times[process_id] = time
    
    def _record_completion_time(self, process_id: str, time: float):
        """Registra el tiempo de finalización de un proceso"""
        self.completion_times[process_id] = time
    
    def _check_context_switch(self, new_process_id: Optional[str]):
        """Verifica y cuenta un cambio de contexto"""
        if new_process_id is not None and self.last_process_id != new_process_id:
            self.context_switches += 1
            self.last_process_id = new_process_id
    
    def schedule(self) -> ScheduleResult:
        """Ejecuta la simulación - debe ser implementado por subclases"""
        raise NotImplementedError


class FCFSScheduler(ProcessScheduler):
    """First Come First Served - Planificador no expulsivo"""
    
    def schedule(self) -> ScheduleResult:
        """
        Ejecuta FCFS: los procesos se ejecutan en orden de llegada.
        Si varios procesos llegan al mismo tiempo, usa el orden de la lista.
        """
        self.current_time = 0.0
        ready_queue = []
        next_arrival_idx = 0
        
        while next_arrival_idx < len(self.processes) or ready_queue:
            # Agregar procesos que han llegado al tiempo actual
            while (next_arrival_idx < len(self.processes) and 
                   self.processes[next_arrival_idx].arrival_time <= self.current_time):
                ready_queue.append(self.processes[next_arrival_idx])
                next_arrival_idx += 1
            
            if not ready_queue:
                # Si no hay procesos listos, avanzar al próximo tiempo de llegada
                if next_arrival_idx < len(self.processes):
                    self.current_time = self.processes[next_arrival_idx].arrival_time
                    continue
                else:
                    break
            
            # Seleccionar el primer proceso de la cola
            process = ready_queue.pop(0)
            start_time = max(self.current_time, process.arrival_time)
            end_time = start_time + process.burst_time
            
            self._check_context_switch(process.id)
            self._record_start_time(process.id, start_time)
            self._add_event(process.id, start_time, end_time)
            self._record_completion_time(process.id, end_time)
            
            self.current_time = end_time
        
        return ScheduleResult(
            algorithm_name="FCFS",
            events=self.events,
            completion_times=self.completion_times,
            start_times=self.start_times,
            processes=self.processes,
            total_time=self.current_time,
            context_switches=max(0, self.context_switches - 1)
        )


class SJFScheduler(ProcessScheduler):
    """Shortest Job First - Planificador no expulsivo"""
    
    def schedule(self) -> ScheduleResult:
        """
        Ejecuta SJF: selecciona el proceso disponible con menor tiempo de ejecución.
        Desempates: primero por tiempo de llegada, luego por orden de entrada.
        """
        self.current_time = 0.0
        ready_queue = []
        next_arrival_idx = 0
        processed = set()
        
        while len(processed) < len(self.processes):
            # Agregar procesos que han llegado al tiempo actual
            while (next_arrival_idx < len(self.processes) and 
                   self.processes[next_arrival_idx].arrival_time <= self.current_time):
                if self.processes[next_arrival_idx].id not in processed:
                    ready_queue.append(self.processes[next_arrival_idx])
                next_arrival_idx += 1
            
            if not ready_queue:
                # Si no hay procesos listos, avanzar al próximo tiempo de llegada
                if next_arrival_idx < len(self.processes):
                    self.current_time = self.processes[next_arrival_idx].arrival_time
                    continue
                else:
                    break
            
            # Seleccionar el proceso con menor burst_time
            # Desempate por arrival_time, luego por orden de entrada (índice)
            ready_queue.sort(key=lambda p: (p.burst_time, p.arrival_time, 
                                           self.processes.index(p)))
            process = ready_queue.pop(0)
            
            start_time = max(self.current_time, process.arrival_time)
            end_time = start_time + process.burst_time
            
            self._check_context_switch(process.id)
            self._record_start_time(process.id, start_time)
            self._add_event(process.id, start_time, end_time)
            self._record_completion_time(process.id, end_time)
            
            processed.add(process.id)
            self.current_time = end_time
        
        return ScheduleResult(
            algorithm_name="SJF",
            events=self.events,
            completion_times=self.completion_times,
            start_times=self.start_times,
            processes=self.processes,
            total_time=self.current_time,
            context_switches=max(0, self.context_switches - 1)
        )


class SRTFScheduler(ProcessScheduler):
    """Shortest Remaining Time First - Planificador expulsivo"""
    
    def schedule(self) -> ScheduleResult:
        """
        Ejecuta SRTF: selecciona siempre el proceso con menor tiempo restante.
        Es expulsivo: puede interrumpir procesos en ejecución.
        """
        completed = set()
        current_process = None
        segment_start = None
        
        while len(completed) < len(self.processes):
            # Procesos disponibles
            available = [p for p in self.processes 
                        if p.id not in completed and p.arrival_time <= self.current_time]
            
            if not available:
                # Avanzar al próximo
                next_arrival = min((p.arrival_time for p in self.processes 
                                   if p.id not in completed and p.arrival_time > self.current_time),
                                  default=float('inf'))
                if next_arrival < float('inf'):
                    self.current_time = next_arrival
                continue
            
            # Seleccionar mejor (menor tiempo restante)
            available.sort(key=lambda p: (p.remaining_time, p.arrival_time,
                                         self.processes.index(p)))
            best = available[0]
            
            # Cambio de proceso
            if current_process and current_process.id != best.id:
                # Terminar evento anterior
                self._add_event(current_process.id, segment_start, self.current_time,
                               ScheduleEventType.PREEMPT)
                segment_start = self.current_time
            
            # Nuevo proceso
            if not current_process:
                current_process = best
                segment_start = self.current_time
                self._record_start_time(current_process.id, segment_start)
                self._check_context_switch(current_process.id)
            elif current_process.id != best.id:
                current_process = best
                self._record_start_time(current_process.id, self.current_time)
                self._check_context_switch(current_process.id)
            
            # Próximas llegadas
            next_arrivals = [p.arrival_time for p in self.processes 
                           if p.id not in completed and p.arrival_time > self.current_time]
            next_arrival = min(next_arrivals, default=float('inf'))
            
            # Ejecutar hasta próxima llegada o finalización
            time_to_next = next_arrival - self.current_time if next_arrival < float('inf') else current_process.remaining_time
            exec_time = min(current_process.remaining_time, time_to_next)
            
            if exec_time <= 0:
                if next_arrival < float('inf'):
                    self.current_time = next_arrival
                continue
            
            self.current_time += exec_time
            current_process.remaining_time -= exec_time
            
            # Finalización
            if current_process.remaining_time <= 0.0001:
                self._add_event(current_process.id, segment_start, self.current_time,
                               ScheduleEventType.END)
                self._record_completion_time(current_process.id, self.current_time)
                completed.add(current_process.id)
                current_process = None
                segment_start = None
        
        return ScheduleResult(
            algorithm_name="SRTF",
            events=self.events,
            completion_times=self.completion_times,
            start_times=self.start_times,
            processes=self.processes,
            total_time=self.current_time,
            context_switches=max(0, self.context_switches - 1)
        )


class RoundRobinScheduler(ProcessScheduler):
    """Round Robin - Planificador con quantum configurable"""
    
    def __init__(self, processes: List[Process], quantum: float = 2.0):
        super().__init__(processes)
        self.quantum = quantum
    
    def schedule(self) -> ScheduleResult:
        """
        Ejecuta Round Robin: cada proceso se ejecuta hasta quantum o hasta terminar.
        Los procesos no terminados vuelven al final de la cola.
        """
        self.current_time = 0.0
        ready_queue = []
        next_arrival_idx = 0
        completed = set()
        
        while len(completed) < len(self.processes):
            # Agregar procesos que han llegado al tiempo actual
            while (next_arrival_idx < len(self.processes) and 
                   self.processes[next_arrival_idx].arrival_time <= self.current_time):
                if self.processes[next_arrival_idx].id not in completed:
                    ready_queue.append(self.processes[next_arrival_idx])
                next_arrival_idx += 1
            
            if not ready_queue:
                if next_arrival_idx < len(self.processes):
                    self.current_time = self.processes[next_arrival_idx].arrival_time
                    continue
                else:
                    break
            
            # Obtener el próximo proceso de la cola FIFO
            current_process = ready_queue.pop(0)
            self._check_context_switch(current_process.id)
            self._record_start_time(current_process.id, self.current_time)
            
            # Calcular el tiempo de ejecución en este quantum
            execution_time = min(self.quantum, current_process.remaining_time)
            
            # Ejecutar hasta el próximo evento (próxima llegada o siguiente quantum)
            time_until_next_arrival = float('inf')
            if next_arrival_idx < len(self.processes):
                time_until_next_arrival = self.processes[next_arrival_idx].arrival_time - self.current_time
                if time_until_next_arrival < execution_time:
                    execution_time = time_until_next_arrival
            
            start_time = self.current_time
            self.current_time += execution_time
            current_process.remaining_time -= execution_time
            
            # Agregar procesos que llegan durante esta ejecución
            while (next_arrival_idx < len(self.processes) and 
                   self.processes[next_arrival_idx].arrival_time <= self.current_time):
                if self.processes[next_arrival_idx].id not in completed:
                    ready_queue.append(self.processes[next_arrival_idx])
                next_arrival_idx += 1
            
            # Registrar el evento
            if current_process.remaining_time <= 0:
                self._add_event(current_process.id, start_time, self.current_time)
                self._record_completion_time(current_process.id, self.current_time)
                completed.add(current_process.id)
            else:
                self._add_event(current_process.id, start_time, self.current_time)
                ready_queue.append(current_process)  # Volver a la cola
        
        return ScheduleResult(
            algorithm_name=f"Round Robin (Q={self.quantum})",
            events=self.events,
            completion_times=self.completion_times,
            start_times=self.start_times,
            processes=self.processes,
            total_time=self.current_time,
            context_switches=max(0, self.context_switches - 1)
        )


class PriorityNonPreemptiveScheduler(ProcessScheduler):
    """Planificación por prioridad no expulsiva"""
    
    def schedule(self) -> ScheduleResult:
        """
        Ejecuta Priority (no expulsivo): selecciona el proceso con mayor prioridad.
        Menor número = mayor prioridad.
        Desempates: por arrival_time, luego por orden de entrada.
        """
        self.current_time = 0.0
        ready_queue = []
        next_arrival_idx = 0
        processed = set()
        
        while len(processed) < len(self.processes):
            # Agregar procesos que han llegado al tiempo actual
            while (next_arrival_idx < len(self.processes) and 
                   self.processes[next_arrival_idx].arrival_time <= self.current_time):
                if self.processes[next_arrival_idx].id not in processed:
                    ready_queue.append(self.processes[next_arrival_idx])
                next_arrival_idx += 1
            
            if not ready_queue:
                if next_arrival_idx < len(self.processes):
                    self.current_time = self.processes[next_arrival_idx].arrival_time
                    continue
                else:
                    break
            
            # Seleccionar por prioridad (menor número = mayor prioridad)
            # Desempates: por arrival_time, luego por índice
            ready_queue.sort(key=lambda p: (p.priority, p.arrival_time,
                                           self.processes.index(p)))
            process = ready_queue.pop(0)
            
            start_time = max(self.current_time, process.arrival_time)
            end_time = start_time + process.burst_time
            
            self._check_context_switch(process.id)
            self._record_start_time(process.id, start_time)
            self._add_event(process.id, start_time, end_time)
            self._record_completion_time(process.id, end_time)
            
            processed.add(process.id)
            self.current_time = end_time
        
        return ScheduleResult(
            algorithm_name="Priority (Non-Preemptive)",
            events=self.events,
            completion_times=self.completion_times,
            start_times=self.start_times,
            processes=self.processes,
            total_time=self.current_time,
            context_switches=max(0, self.context_switches - 1)
        )


class PriorityPreemptiveScheduler(ProcessScheduler):
    """Planificación por prioridad expulsiva"""
    
    def schedule(self) -> ScheduleResult:
        """
        Ejecuta Priority (expulsivo): selecciona el proceso con mayor prioridad disponible.
        Si llega un proceso con mayor prioridad, se interrumpe el actual.
        Menor número = mayor prioridad.
        """
        completed = set()
        current_process = None
        segment_start = None
        
        while len(completed) < len(self.processes):
            # Procesos disponibles
            available = [p for p in self.processes 
                        if p.id not in completed and p.arrival_time <= self.current_time]
            
            if not available:
                # Avanzar al próximo
                next_arrival = min((p.arrival_time for p in self.processes 
                                   if p.id not in completed and p.arrival_time > self.current_time),
                                  default=float('inf'))
                if next_arrival < float('inf'):
                    self.current_time = next_arrival
                continue
            
            # Seleccionar mejor (mayor prioridad = menor número)
            available.sort(key=lambda p: (p.priority, p.arrival_time,
                                         self.processes.index(p)))
            best = available[0]
            
            # Cambio de proceso
            if current_process and current_process.id != best.id:
                if best.priority >= current_process.priority:
                    best = current_process
                else:
                    self._add_event(current_process.id, segment_start, self.current_time,
                                   ScheduleEventType.PREEMPT)
                    segment_start = self.current_time
            
            # Nuevo proceso
            if not current_process:
                current_process = best
                segment_start = self.current_time
                self._record_start_time(current_process.id, segment_start)
                self._check_context_switch(current_process.id)
            elif current_process.id != best.id:
                current_process = best
                self._record_start_time(current_process.id, self.current_time)
                self._check_context_switch(current_process.id)
            
            # Próximas llegadas
            next_arrivals = [p.arrival_time for p in self.processes 
                           if p.id not in completed and p.arrival_time > self.current_time]
            next_arrival = min(next_arrivals, default=float('inf'))
            
            # Ejecutar hasta próxima llegada o finalización
            time_to_next = next_arrival - self.current_time if next_arrival < float('inf') else current_process.remaining_time
            exec_time = min(current_process.remaining_time, time_to_next)
            
            if exec_time <= 0:
                if next_arrival < float('inf'):
                    self.current_time = next_arrival
                continue
            
            self.current_time += exec_time
            current_process.remaining_time -= exec_time
            
            # Finalización
            if current_process.remaining_time <= 0.0001:
                self._add_event(current_process.id, segment_start, self.current_time,
                               ScheduleEventType.END)
                self._record_completion_time(current_process.id, self.current_time)
                completed.add(current_process.id)
                current_process = None
                segment_start = None
        
        return ScheduleResult(
            algorithm_name="Priority (Preemptive)",
            events=self.events,
            completion_times=self.completion_times,
            start_times=self.start_times,
            processes=self.processes,
            total_time=self.current_time,
            context_switches=max(0, self.context_switches - 1)
        )


def create_scheduler(algorithm_name: str, processes: List[Process], 
                    quantum: float = 2.0) -> ProcessScheduler:
    """Factory para crear el planificador apropiado"""
    if algorithm_name == "FCFS":
        return FCFSScheduler(processes)
    elif algorithm_name == "SJF":
        return SJFScheduler(processes)
    elif algorithm_name == "SRTF":
        return SRTFScheduler(processes)
    elif algorithm_name == "Round Robin":
        return RoundRobinScheduler(processes, quantum)
    elif algorithm_name == "Priority (Non-Preemptive)":
        return PriorityNonPreemptiveScheduler(processes)
    elif algorithm_name == "Priority (Preemptive)":
        return PriorityPreemptiveScheduler(processes)
    else:
        raise ValueError(f"Algoritmo desconocido: {algorithm_name}")
