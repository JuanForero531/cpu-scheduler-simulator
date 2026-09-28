"""
Aplicación Streamlit para simular y analizar algoritmos de planificación de procesos de CPU.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict
import random
from datetime import datetime

from algorithms import Process, create_scheduler, ScheduleResult
from metrics import calculate_metrics, AlgorithmMetrics, get_comparison_table, get_best_algorithms
from visualization import (
    create_gantt_chart, create_comparison_chart, create_multi_metrics_chart,
    create_process_timeline, create_metrics_table_figure, create_summary_metrics_figure
)


# Configuración de la página
st.set_page_config(
    page_title="CPU Scheduler Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': 'Simulador de planificación de CPU'
    }
)

# Estilos CSS personalizados
st.markdown("""
<style>
    :root {
        --bg: #eef4ff;
        --panel: rgba(255,255,255,0.78);
        --panel-strong: #ffffff;
        --surface: #f5f8ff;
        --primary: #2f5bff;
        --primary-strong: #1c3edb;
        --primary-soft: #ebf0ff;
        --text: #11213d;
        --muted: #58657d;
        --line: #dfe7f6;
        --success: #2b8a5b;
        --warning: #d97706;
        --shadow: 0 18px 40px rgba(24, 38, 80, 0.12);
    }

    .stApp {
        background: linear-gradient(180deg, #edf4ff 0%, #f8fbff 100%);
        color: var(--text);
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .main-header {
        font-size: 4rem;
        line-height: 1.05;
        letter-spacing: -0.06em;
        color: var(--text);
        font-weight: 700;
        margin: 0.5rem 0 1.2rem 0;
    }

    .section-header {
        font-size: 2.2rem;
        line-height: 1.2;
        color: var(--text);
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.65rem;
        margin-top: 1.4rem;
        margin-bottom: 1rem;
        font-weight: 700;
        letter-spacing: -0.04em;
    }

    .section-tag {
        display: inline-block;
        background: linear-gradient(135deg, #f2efff, #edf5ff);
        border: 1px solid #dfe7ff;
        color: var(--primary-strong);
        border-radius: 999px;
        padding: 0.35rem 0.9rem;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .info-box, .success-box, .warning-box {
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        background: rgba(255,255,255,0.65);
    }

    .info-box {
        border-left: 4px solid var(--primary);
        background: linear-gradient(135deg, #f6f9ff, #eff4ff);
    }

    .success-box {
        border-left: 4px solid var(--success);
        background: linear-gradient(135deg, #f4fff8, #effaf3);
    }

    .warning-box {
        border-left: 4px solid var(--warning);
        background: linear-gradient(135deg, #fffaf3, #fff3e7);
    }

    .glass-panel {
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(169,184,217,0.8);
        border-radius: 20px;
        box-shadow: var(--shadow);
        padding: 1.25rem;
        backdrop-filter: blur(6px);
    }

    .nav-chip {
        display: inline-block;
        border-radius: 999px;
        border: 1px solid var(--line);
        background: rgba(255,255,255,0.65);
        padding: 0.5rem 0.8rem;
        font-weight: 600;
        color: var(--text);
    }

    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f4f7ff);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: var(--shadow);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101d35 0%, #172b4d 52%, #10213d 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.25rem 1rem 1.5rem;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.35rem 0.35rem 1.4rem;
        color: #ffffff;
    }

    .sidebar-brand-mark {
        display: grid;
        place-items: center;
        width: 2.45rem;
        height: 2.45rem;
        border-radius: 11px;
        background: #f2c14e;
        color: #10213d;
        font-size: 1.25rem;
        box-shadow: 0 8px 20px rgba(242,193,78,0.25);
    }

    .sidebar-brand-title {
        font-size: 1rem;
        font-weight: 750;
        letter-spacing: 0.01em;
        line-height: 1.1;
    }

    .sidebar-brand-subtitle {
        margin-top: 0.22rem;
        color: #9fb0c9;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .sidebar-label {
        margin: 0.4rem 0 0.55rem 0.35rem;
        color: #8ea5c4;
        font-size: 0.68rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .sidebar-status {
        margin: 1.4rem 0 1rem;
        padding: 0.7rem 0.8rem;
        border: 1px solid rgba(159,176,201,0.2);
        border-radius: 10px;
        background: rgba(255,255,255,0.06);
        color: #dbe5f3;
        font-size: 0.78rem;
    }

    .sidebar-status strong {
        color: #ffffff;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        min-height: 2.35rem;
        padding: 0.38rem 0.65rem;
        border-radius: 9px;
        color: #c7d4e7;
        transition: background 0.18s ease, color 0.18s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,0.08);
        color: #ffffff;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #f2c14e;
        color: #10213d;
        font-weight: 750;
        box-shadow: 0 7px 18px rgba(0,0,0,0.16);
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) > div:first-child {
        background: #10213d;
        border-color: #10213d;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
        border-color: #8ea5c4;
    }

    [data-testid="stSidebar"] [data-testid="stSlider"] {
        padding: 0.35rem 0.35rem 0.8rem;
    }

    [data-testid="stSidebar"] .stButton > button {
        border: 1px solid rgba(255,255,255,0.16);
        background: rgba(255,255,255,0.08);
        color: #e8eef7;
        box-shadow: none;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: #f2c14e;
        background: rgba(242,193,78,0.12);
        color: #ffffff;
        box-shadow: none;
    }

    [data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(47,91,255,0.18);
        background: linear-gradient(135deg, #ffffff, #eef3ff);
        color: var(--text);
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(47,91,255,0.3);
        box-shadow: 0 8px 18px rgba(47,91,255,0.18);
        transform: translateY(-1px);
    }

    .stRadio > div {
        gap: 0.5rem;
    }

    .stSelectbox, .stNumberInput, .stTextInput {
        background: rgba(255,255,255,0.55);
        border-radius: 12px;
    }

    div[data-testid="stSlider"] {
        border-radius: 12px;
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Inicializa el estado de la sesión"""
    if 'processes' not in st.session_state:
        st.session_state.processes = []
    
    if 'execution_results' not in st.session_state:
        st.session_state.execution_results = {}
    
    if 'last_seed' not in st.session_state:
        st.session_state.last_seed = 42


def validate_process(process_id: str, arrival: float, burst: float, 
                     priority: int) -> tuple[bool, str]:
    """Valida un proceso y retorna (es_válido, mensaje_error)"""
    
    if not process_id.strip():
        return False, "El ID del proceso no puede estar vacío"
    
    if arrival < 0:
        return False, f"Tiempo de llegada no puede ser negativo: {arrival}"
    
    if burst <= 0:
        return False, f"Tiempo de ejecución debe ser mayor a 0: {burst}"
    
    if priority < 0:
        return False, f"Prioridad no puede ser negativa: {priority}"
    
    return True, ""


def render_header():
    """Renderiza el encabezado de la aplicación"""
    st.markdown('<div class="section-tag">Scheduler Studio</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Simulador de Planificación de CPU</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    <b>Modela, compara y analiza algoritmos de planificación de procesos de CPU.</b><br>
    Explora diagramas de Gantt, métricas de rendimiento y el comportamiento de cada política de planificación.
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Renderiza la barra lateral con navegación"""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark">CPU</div>
            <div>
                <div class="sidebar-brand-title">Scheduler Studio</div>
                <div class="sidebar-brand-subtitle">Laboratorio de planificación</div>
            </div>
        </div>
        <div class="sidebar-label">Espacios de trabajo</div>
        """, unsafe_allow_html=True)
        page = st.radio(
            "Selecciona una sección:",
            ["Inicio", "Entrada de procesos", "Simulación", "Comparación", "Teoría", "Acerca de"],
            label_visibility="collapsed"
        )

        process_count = len(st.session_state.processes)
        result_count = len(st.session_state.execution_results)
        st.markdown(
            f'<div class="sidebar-status"><strong>{process_count}</strong> procesos cargados'
            f'<br><span>{result_count} resultados disponibles</span></div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="sidebar-label">Configuración de simulación</div>', unsafe_allow_html=True)

        quantum = st.slider(
            "Quantum de Round Robin",
            min_value=0.5,
            max_value=10.0,
            value=2.0,
            step=0.5
        )

        if st.button("Limpiar datos", use_container_width=True):
            st.session_state.processes = []
            st.session_state.execution_results = {}
            st.rerun()

        return page, quantum


def render_home_page():
    """Página de inicio"""
    st.markdown('<h2 class="section-header">Resumen</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="glass-panel">
        Este simulador implementa los principales algoritmos de planificación de CPU utilizados en sistemas operativos. Permite:
        <ul>
            <li>Crear procesos con tiempos de llegada, ejecución y prioridad personalizados</li>
            <li>Ejecutar simulaciones con distintas políticas</li>
            <li>Visualizar diagramas de Gantt interactivos</li>
            <li>Comparar el rendimiento entre algoritmos con métricas reales</li>
            <li>Analizar tiempos de espera, retorno y respuesta</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<h3 class="section-header" style="font-size: 1.5rem; margin-top: 0;">Algoritmos disponibles</h3>', unsafe_allow_html=True)

        algorithms_info = {
            "FCFS": "First Come, First Served — no expulsivo, orden de llegada",
            "SJF": "Shortest Job First — no expulsivo, menor ráfaga primero",
            "SRTF": "Shortest Remaining Time First — expulsivo, menor tiempo restante",
            "RR": "Round Robin — quantum configurable y rotación circular",
            "Priority": "Planificación por prioridad — expulsiva y no expulsiva"
        }

        algorithms_info = {
            "FCFS": "Primero en llegar, primero en salir — sin expulsión, orden de llegada",
            "SJF": "Trabajo más corto primero — sin expulsión, menor ráfaga primero",
            "SRTF": "Tiempo restante más corto primero — expulsivo, menor tiempo restante",
            "RR": "Round Robin — quantum configurable y rotación circular",
            "Priority": "Planificación por prioridad — expulsiva y no expulsiva"
        }

        for algo, desc in algorithms_info.items():
            st.markdown(f"<div class='metric-card' style='margin-bottom: 0.7rem;'><strong>{algo}</strong><br>{desc}</div>", unsafe_allow_html=True)


def render_input_page():
    """Página de entrada de procesos"""
    st.markdown('<h2 class="section-header">Entrada de procesos</h2>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Agregar nuevo proceso")
        
        new_pid = st.text_input("ID del proceso (ej: P1, P2)", value="P" + str(len(st.session_state.processes) + 1))
        new_arrival = st.number_input("Tiempo de llegada", value=0.0, step=0.5)
        new_burst = st.number_input("Tiempo de ejecución", value=1.0, step=0.5)
        new_priority = st.number_input("Prioridad (0 = mayor)", value=0, step=1)
        
        if st.button("Agregar proceso", use_container_width=True):
            is_valid, error_msg = validate_process(new_pid, new_arrival, new_burst, new_priority)
            
            if is_valid:
                process = Process(new_pid, new_arrival, new_burst, new_priority)
                st.session_state.processes.append(process)
                st.success(f"Proceso {new_pid} agregado")
                st.rerun()
            else:
                st.error(f"Error: {error_msg}")
    
    with col2:
        st.markdown("#### Cargar datos de ejemplo")
        
        example_choice = st.selectbox(
            "Selecciona un conjunto de ejemplo:",
            ["Personalizado", "Ejemplo 1 (Básico)", "Ejemplo 2 (Prioridades)", 
             "Ejemplo 3 (Complejo)", "Generar aleatorio"]
        )
        
        if example_choice == "Ejemplo 1 (Básico)":
            if st.button("Cargar Ejemplo 1", use_container_width=True):
                st.session_state.processes = [
                    Process("P1", 0, 7, 0),
                    Process("P2", 2, 4, 0),
                    Process("P3", 3, 2, 0),
                    Process("P4", 5, 5, 0),
                ]
                st.success("Ejemplo 1 cargado")
                st.rerun()
        
        elif example_choice == "Ejemplo 2 (Prioridades)":
            if st.button("Cargar Ejemplo 2", use_container_width=True):
                st.session_state.processes = [
                    Process("P1", 0, 7, 2),
                    Process("P2", 2, 4, 1),
                    Process("P3", 3, 2, 3),
                    Process("P4", 5, 5, 2),
                ]
                st.success("Ejemplo 2 cargado")
                st.rerun()
        
        elif example_choice == "Ejemplo 3 (Complejo)":
            if st.button("Cargar Ejemplo 3", use_container_width=True):
                st.session_state.processes = [
                    Process("P1", 0, 5, 1),
                    Process("P2", 1, 3, 0),
                    Process("P3", 2, 8, 2),
                    Process("P4", 3, 4, 1),
                    Process("P5", 4, 2, 0),
                    Process("P6", 6, 6, 3),
                ]
                st.success("Ejemplo 3 cargado")
                st.rerun()
        
        elif example_choice == "Generar aleatorio":
            col_seed, col_count = st.columns(2)
            with col_seed:
                seed = st.number_input("Semilla", min_value=0, value=42)
            with col_count:
                count = st.number_input("Cantidad de procesos", min_value=1, max_value=20, value=5)
            
            if st.button("Generar", use_container_width=True):
                random.seed(seed)
                st.session_state.processes = []
                arrival = 0
                for i in range(count):
                    st.session_state.processes.append(
                        Process(
                            f"P{i+1}",
                            float(arrival),
                            float(random.uniform(1, 10)),
                            random.randint(0, 3)
                        )
                    )
                    arrival += random.uniform(0, 3)
                st.success(f"{count} procesos aleatorios generados")
                st.session_state.last_seed = seed
                st.rerun()
    
    # Mostrar procesos actuales
    st.markdown("#### Procesos actuales")
    
    if st.session_state.processes:
        processes_data = []
        for p in st.session_state.processes:
            processes_data.append({
                "ID": p.id,
                "Llegada": p.arrival_time,
                "Ejecución": p.burst_time,
                "Prioridad": p.priority
            })
        
        df = pd.DataFrame(processes_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Opciones de edición
        col1, col2 = st.columns(2)
        with col1:
            edit_idx = st.number_input("Índice del proceso a editar", 
                                      min_value=0, max_value=len(st.session_state.processes)-1)
            
            if edit_idx < len(st.session_state.processes):
                p = st.session_state.processes[edit_idx]
                st.write(f"Editando: {p.id}")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    new_arrival = st.number_input(
                        f"Nueva llegada para {p.id}",
                        value=float(p.arrival_time),
                        step=0.5
                    )
                with col_b:
                    new_burst = st.number_input(
                        f"Nueva ejecución para {p.id}",
                        value=float(p.burst_time),
                        step=0.5
                    )
                with col_c:
                    new_priority = st.number_input(f"Nueva prioridad para {p.id}", 
                                                  value=int(p.priority),
                                                  step=1)
                
                if st.button("Guardar cambios"):
                    p.arrival_time = new_arrival
                    p.burst_time = new_burst
                    p.remaining_time = new_burst
                    p.priority = new_priority
                    st.success("Cambios guardados")
                    st.rerun()
        
        with col2:
            delete_idx = st.number_input("Índice del proceso a eliminar", 
                                        min_value=0, max_value=len(st.session_state.processes)-1)
            
            if st.button("Eliminar proceso", use_container_width=True):
                deleted = st.session_state.processes.pop(delete_idx)
                st.success(f"Proceso {deleted.id} eliminado")
                st.rerun()
    
    else:
        st.info("Aún no hay procesos. Agrega uno o carga un ejemplo.")


def render_simulation_page(quantum: float):
    """Página de simulación"""
    st.markdown('<h2 class="section-header">Simulación</h2>', 
                unsafe_allow_html=True)
    
    if not st.session_state.processes:
        st.warning("Aún no hay procesos definidos. Ve a 'Entrada de procesos' para agregarlos.")
        return
    
    # Seleccionar algoritmos
    col1, col2 = st.columns(2)
    
    with col1:
        selected_algorithms = st.multiselect(
            "Selecciona los algoritmos a simular:",
            ["FCFS", "SJF", "SRTF", "Round Robin", "Priority (Non-Preemptive)", "Priority (Preemptive)"],
            default=["FCFS", "SJF"]
        )
    
    with col2:
        if st.button("Ejecutar simulación", use_container_width=True, type="primary"):
            if not selected_algorithms:
                st.error("Debes seleccionar al menos un algoritmo.")
            else:
                with st.spinner("Ejecutando simulación..."):
                    st.session_state.execution_results = {}
                    
                    for algo in selected_algorithms:
                        try:
                            scheduler = create_scheduler(
                                algo if algo != "Round Robin" else "Round Robin",
                                st.session_state.processes,
                                quantum=quantum
                            )
                            schedule_result = scheduler.schedule()
                            metrics = calculate_metrics(schedule_result)
                            st.session_state.execution_results[algo] = {
                                'schedule': schedule_result,
                                'metrics': metrics
                            }
                        except Exception as e:
                            st.error(f"Error al ejecutar {algo}: {str(e)}")
                
                st.success("Simulación completada")
    
    # Mostrar resultados
    if st.session_state.execution_results:
        st.markdown("#### Resultados de la simulación")
        
        # Selector de algoritmo para ver detalles
        algo_select = st.selectbox(
            "Selecciona un algoritmo para ver detalles:",
            list(st.session_state.execution_results.keys())
        )
        
        if algo_select:
            result = st.session_state.execution_results[algo_select]
            schedule = result['schedule']
            metrics = result['metrics']
            
            # Diagrama de Gantt
            st.markdown("##### Diagrama de Gantt")
            gantt_fig = create_gantt_chart(schedule, metrics)
            st.plotly_chart(gantt_fig, use_container_width=True)
            
            # Métricas
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Métricas individuales")
                metrics_table = create_metrics_table_figure(metrics)
                st.plotly_chart(metrics_table, use_container_width=True)
            
            with col2:
                st.markdown("##### Métricas agregadas")
                summary_fig = create_summary_metrics_figure(metrics)
                st.plotly_chart(summary_fig, use_container_width=True)


def render_comparison_page():
    """Página de comparación de algoritmos"""
    st.markdown('<h2 class="section-header">Comparación de algoritmos</h2>', 
                unsafe_allow_html=True)
    
    if not st.session_state.execution_results:
        st.warning("Aún no hay resultados de simulación. Ejecuta primero una simulación.")
        return
    
    # Seleccionar métrica a comparar
    col1, col2 = st.columns([2, 1])
    
    with col1:
        metric_choice = st.selectbox(
            "Métrica a comparar:",
            ["avg_waiting_time", "avg_turnaround_time", "avg_response_time", 
             "cpu_utilization", "throughput", "context_switches"],
            format_func=lambda x: {
                "avg_waiting_time": "Tiempo medio de espera",
                "avg_turnaround_time": "Tiempo medio de retorno",
                "avg_response_time": "Tiempo medio de respuesta",
                "cpu_utilization": "Utilización de CPU",
                "throughput": "Rendimiento (Throughput)",
                "context_switches": "Cambios de contexto"
            }[x]
        )
    
    with col2:
        st.empty()
    
    # Gráfico comparativo
    algorithms_metrics = {algo: result['metrics'] 
                         for algo, result in st.session_state.execution_results.items()}
    
    comparison_fig = create_comparison_chart(algorithms_metrics, metric_choice)
    st.plotly_chart(comparison_fig, use_container_width=True)
    
    # Tabla de comparación
    st.markdown("#### Tabla comparativa")
    comparison_table = get_comparison_table(algorithms_metrics)
    comparison_df = pd.DataFrame(comparison_table)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Resumen de mejores
    st.markdown("#### Resumen de mejores algoritmos")
    best_algorithms = get_best_algorithms(algorithms_metrics)
    
    for metric_name, winner in best_algorithms.items():
        st.markdown(f"**{metric_name}:** {winner}")
    
    # Gráfico de radar (múltiples métricas)
    st.markdown("#### Comparación multi-métrica")
    radar_fig = create_multi_metrics_chart(algorithms_metrics)
    st.plotly_chart(radar_fig, use_container_width=True)
    
    # Análisis de distribución
    st.markdown("#### Distribución de tiempos de espera")
    timeline_fig = create_process_timeline(algorithms_metrics)
    st.plotly_chart(timeline_fig, use_container_width=True)


def render_theory_page():
    """Página de teoría y explicaciones"""
    st.markdown('<h2 class="section-header">Teoría de planificación de procesos</h2>', 
                unsafe_allow_html=True)
    
    tabs = st.tabs(["Conceptos Básicos", "FCFS", "SJF", "SRTF", "Round Robin", "Prioridades", "Métricas"])
    
    with tabs[0]:
        st.markdown("""
        ### Conceptos Básicos
        
        **¿Qué es un proceso?**
        
        Un proceso es un programa en ejecución. Cada proceso tiene:
        - Tiempo de llegada (Arrival Time): cuándo está listo para ejecutarse
        - Tiempo de ejecución (Burst Time): cuánto tiempo necesita en CPU
        - Prioridad: importancia relativa del proceso
        
        **¿Qué es un planificador?**
        
        El planificador de CPU es la parte del sistema operativo que decide qué proceso 
        ejecutar en cada momento. Objetivo: hacer el mejor uso del CPU.
        
        **Algoritmos expulsivos vs no-expulsivos**
        
        - **No-expulsivo (Non-preemptive):** Una vez que un proceso comienza a ejecutarse, 
          continúa hasta terminar.
        - **Expulsivo (Preemptive):** El planificador puede interrumpir un proceso en ejecución 
          y ejecutar otro, guardando el estado del proceso interrumpido.
        """)
    
    with tabs[1]:
        st.markdown("""
        ### FCFS (First Come, First Served)
        
        **Descripción:**
        Los procesos se ejecutan en el orden exacto en que llegan.
        
        **Características:**
        - No-expulsivo
        - Muy simple de implementar
        - Determinista (resultados reproducibles)
        
        **Ventajas:**
        - Simple y fácil de entender
        - Sin overhead de cambios de contexto
        
        **Desventajas:**
        - Tiempos de espera pueden ser muy largos
        - Fenómeno "convoy": un proceso largo bloquea a muchos cortos
        - Pobre para sistemas interactivos
        
        **Ejemplo:**
        Procesos: P1(7), P2(4), P3(2)
        Orden: P1 → P2 → P3
        """)
    
    with tabs[2]:
        st.markdown("""
        ### SJF (Shortest Job First)
        
        **Descripción:**
        Se ejecuta primero el proceso disponible con menor tiempo de ejecución.
        
        **Características:**
        - No-expulsivo
        - Selecciona el proceso más "corto" entre los listos
        - Los empates se resuelven por orden de llegada
        
        **Ventajas:**
        - Minimiza el tiempo medio de espera entre todos los algoritmos no-expulsivos
        - Menos tiempo de espera total para los procesos cortos
        
        **Desventajas:**
        - Requiere conocer de antemano el tiempo de ejecución (a menudo no disponible)
        - Favorece los procesos cortos, puede dejar los largos esperando
        - Inanición posible: si siempre llegan procesos cortos, los largos nunca se ejecutan
        
        **Ejemplo:**
        Procesos: P1(7), P2(4), P3(2) (todos llegan al t=0)
        Orden: P3(2) → P2(4) → P1(7)
        """)
    
    with tabs[3]:
        st.markdown("""
        ### SRTF (Shortest Remaining Time First)
        
        **Descripción:**
        Versión expulsiva de SJF. Siempre se ejecuta el proceso con menor tiempo restante.
        
        **Características:**
        - Expulsivo: puede interrumpir un proceso en ejecución
        - Si llega un proceso más corto, el actual se interrumpe
        - Conserva el tiempo restante de procesos interrumpidos
        
        **Ventajas:**
        - Mejor tiempo de respuesta para procesos cortos
        - Minimiza el tiempo medio de espera incluso mejor que SJF
        
        **Desventajas:**
        - Muchos cambios de contexto (overhead)
        - Información de burst time no siempre disponible
        - Inanición posible para procesos largos
        - Más complejo de implementar
        
        **Ejemplo:**
        Si P1(7) se ejecuta y llega P2(4), P2 interrumpe a P1.
        """)
    
    with tabs[4]:
        st.markdown("""
        ### Round Robin (RR)
        
        **Descripción:**
        Los procesos se ejecutan en un quantum fijo de tiempo de manera circular.
        
        **Características:**
        - Expulsivo: cada proceso ejecuta máximo un quantum
        - Si no termina, vuelve al final de la cola
        - La cola es FIFO (First In First Out)
        
        **Ventajas:**
        - Justo: todos los procesos obtienen CPU equitativamente
        - Excelente para sistemas interactivos
        - Buen tiempo de respuesta para procesos cortos
        
        **Desventajas:**
        - Muchos cambios de contexto (overhead)
        - Quantum muy pequeño: overhead; muy grande: similar a FCFS
        - Tiempos de espera pueden ser buenos o malos según el quantum
        
        **Parámetro crítico:**
        El quantum (time slice) es fundamental:
        - Quantum pequeño: más cambios de contexto, mejor tiempo de respuesta
        - Quantum grande: menos overhead, peor tiempo de respuesta
        
        **Ejemplo:**
        Q=2: [P1(7), P2(4), P3(2)]
        t=0-2: P1(2), t=2-4: P2(2), t=4-6: P3(2), t=6-8: P1(2), ...
        """)
    
    with tabs[5]:
        st.markdown("""
        ### Planificación por Prioridades
        
        **Descripción:**
        Cada proceso tiene una prioridad. Se ejecuta primero el de mayor prioridad.
        
        **Características:**
        - Prioridad 0 = máxima prioridad
        - No-expulsivo: el proceso continúa hasta terminar
        - Expulsivo: puede interrumpirse si llega uno de mayor prioridad
        
        **Convención de prioridades:**
        - Número MENOR = MAYOR prioridad
        - Ejemplo: Prioridad 0 > Prioridad 1 > Prioridad 2
        
        **Ventajas:**
        - Flexible: permite dar importancia a procesos críticos
        - Realista: los SO modernos usan prioridades
        
        **Desventajas:**
        - Inanición: procesos de baja prioridad pueden nunca ejecutarse
        - Complejidad de asignar prioridades
        - Overhead adicional de cambios de contexto (versión expulsiva)
        
        **Desempates:**
        Cuando hay empate de prioridad:
        1. Se usa el tiempo de llegada (primero quien llegó)
        2. Luego el orden en la lista original
        """)
    
    with tabs[6]:
        st.markdown("""
        ### Métricas de Rendimiento
        
        **Por proceso:**
        
        - **Tiempo de llegada (Arrival Time):** Cuándo está listo el proceso
        
        - **Tiempo de ejecución (Burst Time):** Cuánto CPU necesita
        
        - **Tiempo de finalización (Completion Time):** Cuándo termina el proceso
        
        - **Tiempo de retorno (Turnaround Time):** Completion Time - Arrival Time
          - Mide cuánto tarda desde que llega hasta que termina
        
        - **Tiempo de espera (Waiting Time):** Turnaround Time - Burst Time
          - Cuánto tiempo espera sin ejecutarse
          - MÁS BAJA es mejor
        
        - **Tiempo de respuesta (Response Time):** First Start Time - Arrival Time
          - Cuánto tarda desde la llegada hasta la primera ejecución
          - Importante para interactividad
        
        **Agregadas:**
        
        - **Tiempo medio de espera:** Promedio de tiempos de espera de todos los procesos
          - La métrica más importante para comparar algoritmos
        
        - **Tiempo medio de retorno:** Promedio de tiempos de retorno
        
        - **Tiempo medio de respuesta:** Promedio de tiempos de respuesta
        
        - **Utilización de CPU (%):** (Tiempo ocupado / Tiempo total) × 100
          - Qué porcentaje está el CPU ejecutando vs idle
        
        - **Rendimiento (Throughput):** Procesos completados / Tiempo total
          - Cuántos procesos se completan por unidad de tiempo
        
        - **Cambios de contexto:** Número de veces que cambió el proceso en ejecución
          - Relacionado con overhead del sistema
        """)


def render_about_page():
    """Página de información del proyecto"""
    st.markdown('<h2 class="section-header">Acerca de este proyecto</h2>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-panel">
        <h3 style="margin-top:0;">Información del proyecto</h3>
        <p><strong>Nombre:</strong> Simulador Interactivo de Planificación de Procesos</p>
        <p><strong>Versión:</strong> 1.0.0</p>
        <p><strong>Fecha:</strong> 2026</p>
        <p><strong>Propósito:</strong> Aplicación educativa para Ingeniería de Sistemas</p>
        
        <h3>Objetivos</h3>
        <ul>
            <li>Enseñar los algoritmos fundamentales de planificación de CPU</li>
            <li>Permitir experimentos interactivos con diferentes configuraciones</li>
            <li>Visualizar y comparar el impacto de diferentes algoritmos</li>
            <li>Calcular métricas de rendimiento de manera precisa</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-panel">
        <h3 style="margin-top:0;">Tecnologías utilizadas</h3>
        <ul>
            <li><strong>Python 3.11+</strong> — Lenguaje de programación</li>
            <li><strong>Streamlit</strong> — Framework para interfaz web</li>
            <li><strong>Plotly</strong> — Visualizaciones interactivas</li>
            <li><strong>Pandas</strong> — Análisis de datos</li>
            <li><strong>Pytest</strong> — Framework de pruebas</li>
        </ul>
        
        <h3>Requisitos del sistema</h3>
        <ul>
            <li>Python 3.11 o superior</li>
            <li>Conexión a Internet para descargar dependencias</li>
            <li>Navegador moderno</li>
            <li>Mínimo 500 MB de espacio en disco</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div class="glass-panel">
    <h3 style="margin-top:0;">Documentación</h3>
    <p>Para más información y documentación completa, consulta el archivo README.md incluido en el proyecto.</p>
    
    <h3>Limitaciones</h3>
    <ul>
        <li>La simulación asume que se conoce el tiempo de ejecución (burst time) de los procesos</li>
        <li>No simula I/O ni interrupciones del sistema</li>
        <li>Los tiempos son unidades abstractas y no segundos reales</li>
        <li>La capacidad de visualización depende del número de procesos (máximo recomendado: 20)</li>
    </ul>
    
    <h3>Uso académico</h3>
    <p>Este proyecto es apropiado para:</p>
    <ul>
        <li>Cursos de Sistemas Operativos</li>
        <li>Demostraciones en clase</li>
        <li>Proyectos estudiantiles</li>
        <li>Investigación educativa</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Función principal"""
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Sidebar y selección de página
    page, quantum = render_sidebar()
    
    # Renderizar página seleccionada
    if page == "Inicio":
        render_home_page()
    
    elif page == "Entrada de procesos":
        render_input_page()
    
    elif page == "Simulación":
        render_simulation_page(quantum)
    
    elif page == "Comparación":
        render_comparison_page()
    
    elif page == "Teoría":
        render_theory_page()
    
    elif page == "Acerca de":
        render_about_page()


if __name__ == "__main__":
    main()
