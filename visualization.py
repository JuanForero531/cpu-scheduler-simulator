"""
Módulo para visualización de algoritmos de planificación con Plotly.
Genera diagramas de Gantt e gráficas comparativas.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
from algorithms import ScheduleResult, ScheduleEventType
from metrics import AlgorithmMetrics
import colorsys


def generate_colors(num_processes: int) -> Dict[str, str]:
    """
    Genera colores distintos para cada proceso usando HSL.
    Evita usar solo colores (diferencia de tonalidad).
    """
    colors = {}
    process_ids = sorted(set())  # Se llena luego
    
    if num_processes == 0:
        return colors
    
    for i in range(num_processes):
        hue = i / num_processes
        saturation = 0.7
        lightness = 0.5
        
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        color = f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})'
        # Almacenar temporalmente, se asigna después
    
    return {f"P{i+1}": f"rgb({int(colorsys.hls_to_rgb(i/num_processes, 0.5, 0.7)[0]*255)}, "
                        f"{int(colorsys.hls_to_rgb(i/num_processes, 0.5, 0.7)[1]*255)}, "
                        f"{int(colorsys.hls_to_rgb(i/num_processes, 0.5, 0.7)[2]*255)})"
            for i in range(num_processes)}


def get_color_for_process(process_id: str, total_processes: int) -> str:
    """Obtiene un color para un proceso específico"""
    # Extraer número del ID (P1 -> 1, P2 -> 2, etc.)
    try:
        process_num = int(process_id.replace('P', '').replace('p', ''))
        # Ajustar a base 0
        idx = process_num - 1
    except:
        idx = hash(process_id) % total_processes
    
    hue = idx / max(total_processes, 1)
    saturation = 0.75
    lightness = 0.5
    
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    return f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})'


def create_gantt_chart(schedule_result: ScheduleResult, 
                       metrics: AlgorithmMetrics) -> go.Figure:
    """
    Crea un diagrama de Gantt interactivo con Plotly.
    """
    
    # Preparar datos para Plotly
    gantt_data = []
    total_processes = len(schedule_result.processes)
    
    for event in schedule_result.events:
        gantt_data.append({
            'Task': event.process_id,
            'Start': event.start_time,
            'Finish': event.end_time,
            'Duration': event.end_time - event.start_time,
            'Resource': event.process_id
        })
    
    if not gantt_data:
        # Si no hay eventos, retornar gráfica vacía
        fig = go.Figure()
        fig.add_annotation(text="No hay eventos para mostrar", showarrow=False)
        return fig
    
    df = pd.DataFrame(gantt_data)
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar barras del diagrama de Gantt
    for process_id in df['Task'].unique():
        process_data = df[df['Task'] == process_id]
        color = get_color_for_process(process_id, total_processes)
        
        for idx, row in process_data.iterrows():
            # Obtener información de métricas
            proc_metrics = metrics.individual_metrics.get(process_id)
            
            hover_text = (f"<b>Proceso: {process_id}</b><br>"
                         f"Inicio: {row['Start']:.2f}<br>"
                         f"Fin: {row['Finish']:.2f}<br>"
                         f"Duración: {row['Duration']:.2f}")
            
            if proc_metrics:
                hover_text += (f"<br>Llegada: {proc_metrics.arrival_time:.2f}<br>"
                              f"Prioridad: {proc_metrics.priority}<br>"
                              f"Espera: {proc_metrics.waiting_time:.2f}")
            
            fig.add_trace(go.Bar(
                x=[row['Duration']],
                y=[process_id],
                base=row['Start'],
                orientation='h',
                marker=dict(color=color, line=dict(color='black', width=1)),
                name=process_id,
                hovertext=hover_text,
                hoverinfo='text',
                legendgroup=process_id,
                showlegend=(idx == 0),  # Solo mostrar en leyenda una vez
                text=f"{process_id}<br>{row['Duration']:.1f}",
                textposition="inside",
                textfont=dict(size=10, color="white"),
            ))
    
    # Layout
    fig.update_layout(
        title=f"Diagrama de Gantt - {metrics.algorithm_name}",
        xaxis_title="Tiempo",
        yaxis_title="Proceso",
        barmode='overlay',
        height=400 + len(schedule_result.processes) * 20,
        hovermode='closest',
        template='plotly_white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=False
        ),
        yaxis=dict(
            autorange="reversed",
            categoryorder="total ascending"
        ),
        margin=dict(l=100, r=50, t=80, b=50),
    )
    
    # Agregar líneas verticales en puntos de llegada (opcional, para referencia)
    for process in schedule_result.processes:
        if process.arrival_time > 0:
            fig.add_vline(
                x=process.arrival_time,
                line_dash="dash",
                line_color="gray",
                opacity=0.3,
                annotation_text=f"Llegada {process.id}",
                annotation_position="top"
            )
    
    return fig


def create_comparison_chart(algorithms_metrics: Dict[str, AlgorithmMetrics],
                           metric_type: str = "avg_waiting_time") -> go.Figure:
    """
    Crea un gráfico de comparación entre algoritmos.
    
    metric_type puede ser:
    - avg_waiting_time
    - avg_turnaround_time
    - avg_response_time
    - cpu_utilization
    - throughput
    - context_switches
    """
    
    algo_names = []
    values = []
    
    metric_labels = {
        'avg_waiting_time': 'Tiempo Medio de Espera',
        'avg_turnaround_time': 'Tiempo Medio de Retorno',
        'avg_response_time': 'Tiempo Medio de Respuesta',
        'cpu_utilization': 'Utilización de CPU (%)',
        'throughput': 'Rendimiento (procs/unidad)',
        'context_switches': 'Cambios de Contexto'
    }
    
    for algo_name, metrics in algorithms_metrics.items():
        algo_names.append(algo_name)
        
        if metric_type == 'avg_waiting_time':
            values.append(metrics.avg_waiting_time)
        elif metric_type == 'avg_turnaround_time':
            values.append(metrics.avg_turnaround_time)
        elif metric_type == 'avg_response_time':
            values.append(metrics.avg_response_time)
        elif metric_type == 'cpu_utilization':
            values.append(metrics.cpu_utilization)
        elif metric_type == 'throughput':
            values.append(metrics.throughput)
        elif metric_type == 'context_switches':
            values.append(metrics.context_switches)
    
    # Crear gráfico de barras
    fig = go.Figure(data=[
        go.Bar(
            x=algo_names,
            y=values,
            marker=dict(
                color=values,
                colorscale='Viridis',
                showscale=False
            ),
            text=[f"{v:.2f}" if isinstance(v, float) else str(v) for v in values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' + 
                         metric_labels.get(metric_type, metric_type) + ': %{y:.2f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=f"Comparación de Algoritmos - {metric_labels.get(metric_type, metric_type)}",
        xaxis_title="Algoritmo",
        yaxis_title=metric_labels.get(metric_type, metric_type),
        height=500,
        template='plotly_white',
        hovermode='x unified',
        showlegend=False,
        margin=dict(l=80, r=50, t=80, b=80)
    )
    
    return fig


def create_multi_metrics_chart(algorithms_metrics: Dict[str, AlgorithmMetrics]) -> go.Figure:
    """
    Crea un gráfico radar (spider) comparando múltiples métricas.
    """
    
    metrics_to_compare = ['avg_waiting_time', 'avg_turnaround_time', 
                         'avg_response_time', 'cpu_utilization']
    
    categories = ['Espera Media', 'Retorno Medio', 'Respuesta Media', 'Utilización CPU']
    
    fig = go.Figure()
    
    for algo_name, metrics in algorithms_metrics.items():
        values = [
            metrics.avg_waiting_time,
            metrics.avg_turnaround_time,
            metrics.avg_response_time,
            metrics.cpu_utilization / 100  # Normalizar a 0-1
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=algo_name,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         '%{theta}: %{r:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(
                    max(m.avg_waiting_time, m.avg_turnaround_time, m.avg_response_time)
                    for m in algorithms_metrics.values()
                )]
            )
        ),
        title="Comparación de Múltiples Métricas",
        height=600,
        template='plotly_white',
        showlegend=True,
        hovermode='closest'
    )
    
    return fig


def create_process_timeline(algorithms_metrics: Dict[str, AlgorithmMetrics]) -> go.Figure:
    """
    Crea un gráfico comparativo del ciclo de vida de procesos
    """
    
    metrics_list = []
    
    for algo_name, metrics in algorithms_metrics.items():
        for proc_id, proc_metrics in metrics.individual_metrics.items():
            metrics_list.append({
                'Algoritmo': algo_name,
                'Proceso': proc_id,
                'Llegada': proc_metrics.arrival_time,
                'Inicio': proc_metrics.first_response_time,
                'Final': proc_metrics.completion_time,
                'Espera': proc_metrics.waiting_time,
                'Retorno': proc_metrics.turnaround_time
            })
    
    if not metrics_list:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos para mostrar", showarrow=False)
        return fig
    
    df = pd.DataFrame(metrics_list)
    
    fig = px.box(df, x='Algoritmo', y='Espera', color='Algoritmo',
                points='all', height=500,
                title='Distribución de Tiempos de Espera por Algoritmo')
    
    fig.update_layout(
        hovermode='closest',
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def create_metrics_table_figure(metrics: AlgorithmMetrics) -> go.Figure:
    """
    Crea una tabla de métricas individuales como figura de Plotly.
    """
    
    rows = []
    for proc_id in sorted(metrics.individual_metrics.keys()):
        m = metrics.individual_metrics[proc_id]
        rows.append([
            m.process_id,
            f"{m.arrival_time:.2f}",
            f"{m.burst_time:.2f}",
            m.priority,
            f"{m.response_time:.2f}",
            f"{m.completion_time:.2f}",
            f"{m.turnaround_time:.2f}",
            f"{m.waiting_time:.2f}"
        ])
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Proceso</b>', '<b>Llegada</b>', '<b>Ejecución</b>', 
                   '<b>Prioridad</b>', '<b>Respuesta</b>', '<b>Final</b>',
                   '<b>Retorno</b>', '<b>Espera</b>'],
            fill_color='paleturquoise',
            align='center',
            font=dict(size=11, color='black')
        ),
        cells=dict(
            values=list(zip(*rows)) if rows else [],
            fill_color='lavender',
            align='center',
            font=dict(size=10),
            height=25
        )
    )])
    
    fig.update_layout(
        title=f"Métricas Individuales - {metrics.algorithm_name}",
        height=300 + len(rows) * 25,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig


def create_summary_metrics_figure(metrics: AlgorithmMetrics) -> go.Figure:
    """
    Crea una figura con las métricas agregadas en formato visual.
    """
    
    metrics_data = {
        'Métrica': [
            'Espera Media',
            'Retorno Medio',
            'Respuesta Media',
            'Utilización CPU',
            'Rendimiento',
            'Cambios Contexto'
        ],
        'Valor': [
            f"{metrics.avg_waiting_time:.2f}",
            f"{metrics.avg_turnaround_time:.2f}",
            f"{metrics.avg_response_time:.2f}",
            f"{metrics.cpu_utilization:.2f}%",
            f"{metrics.throughput:.4f}",
            str(metrics.context_switches)
        ]
    }
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Métrica</b>', '<b>Valor</b>'],
            fill_color='lightblue',
            align='left',
            font=dict(size=12, color='black')
        ),
        cells=dict(
            values=[metrics_data['Métrica'], metrics_data['Valor']],
            fill_color='aliceblue',
            align='left',
            font=dict(size=11),
            height=30
        )
    )])
    
    fig.update_layout(
        title=f"Métricas Agregadas - {metrics.algorithm_name}",
        height=350,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig
