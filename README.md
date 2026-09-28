# 🖥️ Simulador Interactivo de Planificación de Procesos de CPU

## Descripción

Este proyecto es una aplicación educativa interactiva desarrollada con Python y Streamlit que simula, analiza y compara diferentes algoritmos de planificación de procesos de CPU. Está diseñada para estudiantes de Ingeniería de Sistemas que desean entender cómo los sistemas operativos asignan tiempo de procesamiento entre múltiples procesos.

## Objetivos

### Generales
- Proporcionar una herramienta educativa para comprender los algoritmos fundamentales de planificación de procesos
- Permitir experimentos interactivos con diferentes configuraciones de procesos
- Visualizar de manera clara cómo se ejecutan los procesos en el tiempo

### Específicos
- Implementar correctamente 6 algoritmos de planificación distintos
- Calcular métricas de rendimiento precisas (espera, retorno, respuesta)
- Generar visualizaciones interactivas con diagramas de Gantt
- Comparar el desempeño relativo entre algoritmos
- Proporcionar explicaciones teóricas claras y accesibles

## Tecnologías Utilizadas

- **Python 3.11+** - Lenguaje de programación principal
- **Streamlit 1.39.0** - Framework para interfaz web interactiva
- **Plotly 5.24.1** - Visualizaciones interactivas (diagramas de Gantt, gráficos comparativos)
- **Pandas 2.2.3** - Manipulación y análisis de datos
- **NumPy 1.26.4** - Computación numérica
- **Pytest 8.3.4** - Framework para pruebas automatizadas

## Requisitos de Sistema

- **Python:** Versión 3.11 o superior
- **Espacio en disco:** Mínimo 500MB (más si tienes otros proyectos Python)
- **RAM:** Mínimo 2GB (recomendado 4GB o más)
- **Navegador:** Chrome, Firefox, Edge o cualquier navegador moderno
- **Conexión a Internet:** Requerida para descargar las dependencias en la instalación

## Instalación

### Paso 1: Clonar o descargar el proyecto

Si tienes Git instalado:
```powershell
git clone <url-del-repositorio>
cd cpu_scheduler_simulator
```

O descarga el ZIP del proyecto y extrae la carpeta.

### Paso 2: Crear un entorno virtual (recomendado)

**En PowerShell (Windows):**

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Nota: Si recibas un error de permisos, ejecuta:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**En CMD (Windows):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**En Bash (Linux/macOS):**

```bash
python -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar las dependencias

**En PowerShell o CMD:**

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Esto instalará:
- streamlit: Framework web
- plotly: Visualizaciones
- pandas: Análisis de datos
- numpy: Operaciones numéricas
- pytest: Pruebas automatizadas

### Paso 4: Verificar la instalación

```powershell
python -m pytest tests/test_algorithms.py -v
```

Deberías ver un resumen de todas las pruebas ejecutadas. Si todas pasan ✓, la instalación fue exitosa.

## Ejecución de la Aplicación

### Método 1: Streamlit (Recomendado)

**En PowerShell:**

```powershell
streamlit run app.py
```

Esto abrirá automáticamente tu navegador en `http://localhost:8501`

**Notas:**
- La aplicación se ejecutará localmente en tu máquina
- Puedes acceder desde http://localhost:8501
- Para detener, presiona `Ctrl+C` en la terminal

### Método 2: Con URL específica

```powershell
streamlit run app.py --server.port 8501
```

## Estructura del Proyecto

```
cpu_scheduler_simulator/
│
├── app.py                          # Aplicación principal con interfaz Streamlit
├── algorithms.py                   # Implementación de todos los algoritmos
├── metrics.py                      # Cálculo de métricas de rendimiento
├── visualization.py                # Generación de gráficos con Plotly
├── requirements.txt                # Dependencias del proyecto
├── README.md                       # Este archivo
├── .gitignore                      # Archivos a ignorar en Git
│
└── tests/
    └── test_algorithms.py          # Suite completa de pruebas con Pytest
```

### Descripción de módulos

**app.py**
- Interfaz principal con Streamlit
- Navegación por pestañas (Inicio, Entrada de Procesos, Simulación, Comparación, Teoría, Acerca de)
- Gestión de estado de la sesión
- Formularios interactivos para entrada de datos

**algorithms.py**
- Clase base `ProcessScheduler`
- Implementación de 6 algoritmos:
  - `FCFSScheduler`: First Come, First Served
  - `SJFScheduler`: Shortest Job First
  - `SRTFScheduler`: Shortest Remaining Time First
  - `RoundRobinScheduler`: Round Robin con quantum configurable
  - `PriorityNonPreemptiveScheduler`: Prioridades sin expulsión
  - `PriorityPreemptiveScheduler`: Prioridades con expulsión
- Función factory `create_scheduler()` para instanciación

**metrics.py**
- Clase `ProcessMetrics`: Métricas por proceso individual
- Clase `AlgorithmMetrics`: Métricas agregadas por algoritmo
- Función `calculate_metrics()`: Calcula todas las métricas desde el resultado
- Funciones de utilidad para comparación

**visualization.py**
- Generación de diagramas de Gantt interactivos
- Gráficos comparativos entre algoritmos
- Tablas de métricas
- Gráficos radar (spider) para múltiples métricas

**tests/test_algorithms.py**
- 60+ casos de prueba
- Pruebas unitarias para cada algoritmo
- Pruebas de validación de métricas
- Pruebas de integración

## Algoritmos Implementados

### 1. FCFS (First Come, First Served)

**Tipo:** No-expulsivo  
**Descripción:** Los procesos se ejecutan en el orden exacto en que llegan al sistema.

**Características:**
- Muy simple de implementar
- Determinista: mismos datos = mismos resultados
- No requiere conocer burst time de antemano

**Ventajas:**
- Fácil comprensión e implementación
- Sin overhead de cambios de contexto

**Desventajas:**
- Tiempos de espera pueden ser muy largos
- Fenómeno "convoy": proceso largo bloquea procesos cortos
- Pobre desempeño en sistemas interactivos

**Ejemplo:**
```
Procesos: P1(7), P2(4), P3(2) - todos llegan en t=0
Ejecución: [P1: 0-7] → [P2: 7-11] → [P3: 11-13]
Tiempo total: 13
```

### 2. SJF (Shortest Job First)

**Tipo:** No-expulsivo  
**Descripción:** Se ejecuta primero el proceso disponible con menor tiempo de ejecución.

**Características:**
- Minimiza tiempo medio de espera entre algoritmos no-expulsivos
- Requiere conocer burst time
- Favorece procesos cortos

**Ventajas:**
- Mejor tiempo promedio de espera
- Procesos cortos no esperan a procesos largos

**Desventajas:**
- Información de burst time no siempre disponible
- Inanición: procesos largos pueden esperar indefinidamente
- Desfavorable para procesos largos

**Ejemplo:**
```
Procesos: P1(7), P2(4), P3(2) - todos llegan en t=0
Ejecución: [P3: 0-2] → [P2: 2-6] → [P1: 6-13]
Tiempo medio espera: (0 + 2 + 4) / 3 = 2
```

### 3. SRTF (Shortest Remaining Time First)

**Tipo:** Expulsivo  
**Descripción:** Versión expulsiva de SJF. Siempre ejecuta el proceso con menor tiempo restante.

**Características:**
- Puede interrumpir procesos en ejecución
- Si llega proceso más corto, actual se pausa
- Conserva tiempo restante de procesos interrumpidos

**Ventajas:**
- Mejor tiempo de respuesta para procesos cortos
- Mejor tiempo promedio de espera que SJF

**Desventajas:**
- Muchos cambios de contexto (overhead)
- Información de burst time requerida
- Inanición posible
- Más complejo de implementar

**Ejemplo:**
```
Procesos: P1(8) en t=0, P2(4) en t=2
t=0-2: P1 ejecuta (6 restante)
t=2: P2 llega (4 < 6), P1 es preemptado
t=2-6: P2 ejecuta
t=6-14: P1 continúa (6 unidades restantes)
```

### 4. Round Robin (RR)

**Tipo:** Expulsivo  
**Descripción:** Los procesos se ejecutan en pequeños intervalos (quantum) en orden circular.

**Características:**
- Cada proceso ejecuta máximo un quantum
- Si no termina, vuelve al final de la cola FIFO
- Quantum configurable

**Ventajas:**
- Justo: todos obtienen CPU equitativamente
- Excelente para sistemas interactivos
- Buen tiempo de respuesta

**Desventajas:**
- Muchos cambios de contexto
- Quantum crítico: muy pequeño = overhead, muy grande ≈ FCFS
- Tiempos de espera pueden ser subóptimos

**Quantum ideal:**
- Pequeño (1-2): mejor interactividad, más overhead
- Grande (8-10): menos overhead, peor interactividad
- Típicamente: 10-100ms en sistemas reales

**Ejemplo:**
```
Procesos: P1(7), P2(4), P3(2) - todos en t=0, Q=2
t=0-2: P1 (5 restante) → final cola
t=2-4: P2 (2 restante) → final cola
t=4-6: P3 (0 restante) → finaliza
t=6-8: P1 (3 restante) → final cola
t=8-10: P2 (0 restante) → finaliza
t=10-12: P1 (1 restante) → finaliza
```

### 5. Priority (Non-Preemptive)

**Tipo:** No-expulsivo  
**Descripción:** Ejecuta el proceso de mayor prioridad disponible.

**Características:**
- Cada proceso tiene prioridad (0 = máxima)
- Una vez ejecutándose, continúa hasta terminar
- Si empieza proceso mayor prioridad, espera su turno

**Ventajas:**
- Procesos críticos se ejecutan rápidamente
- Flexible para diferentes necesidades
- Realista (SO modernos usan prioridades)

**Desventajas:**
- Inanición: procesos bajos nunca ejecutan
- Requiere asignación cuidadosa de prioridades
- Puede ser injusto

**Convención:**
```
Prioridad 0 (máxima) > Prioridad 1 > Prioridad 2 > ... (mínima)
```

**Ejemplo:**
```
P1(7, pri=2), P2(4, pri=1), P3(2, pri=3)
Orden: P2 → P1 → P3
```

### 6. Priority (Preemptive)

**Tipo:** Expulsivo  
**Descripción:** Versión expulsiva de prioridades. Interrumpe si llega proceso de mayor prioridad.

**Características:**
- Puede preemption
- Mantiene tiempo restante
- Cambios de contexto necesarios

**Ventajas:**
- Procesos críticos responden rápido
- Mejor fairness que no-preemptive

**Desventajas:**
- Inanición posible
- Overhead de cambios de contexto
- Complejidad aumentada

## Métricas Calculadas

### Por Proceso

| Métrica | Fórmula | Significado |
|---------|---------|-------------|
| **Tiempo de llegada (AT)** | Entrada | Cuándo el proceso llega al sistema |
| **Tiempo de ejecución (BT)** | Entrada | Cuánto CPU necesita el proceso |
| **Tiempo de finalización (CT)** | Del cronograma | Cuándo termina el proceso |
| **Tiempo de retorno (TAT)** | CT - AT | Tiempo desde llegada hasta finalización |
| **Tiempo de espera (WT)** | TAT - BT | Tiempo sin ejecutarse (ideal: minimizar) |
| **Tiempo de respuesta (RT)** | Primer inicio - AT | Tiempo hasta primera ejecución |

### Agregadas

| Métrica | Fórmula | Significado |
|---------|---------|-------------|
| **Espera promedio** | Σ WT / n | Tiempo promedio de espera (PRINCIPAL) |
| **Retorno promedio** | Σ TAT / n | Tiempo promedio total |
| **Respuesta promedio** | Σ RT / n | Tiempo promedio hasta respuesta |
| **Utilización CPU (%)** | (Tiempo ocupado / Tiempo total) × 100 | % del tiempo que CPU está activo |
| **Rendimiento (Throughput)** | # procesos / Tiempo total | Procesos completados por unidad de tiempo |
| **Cambios contexto** | # transiciones | Cuántas veces cambió el proceso activo |

## Guía de Uso

### 1. Entrada de Procesos

1. Ve a **➕ Entrada de Procesos**
2. Completa los campos:
   - **ID:** P1, P2, P3, etc.
   - **Tiempo de llegada:** Cuándo el proceso está listo (≥ 0)
   - **Tiempo de ejecución:** Duración en CPU (> 0)
   - **Prioridad:** 0 (máxima), 1, 2, etc.
3. Haz clic en **✅ Agregar proceso**

**Opciones rápidas:**
- Cargar ejemplos predefinidos
- Generar procesos aleatorios (con semilla para reproducibilidad)
- Editar procesos existentes
- Eliminar procesos

### 2. Configuración

En la barra lateral:
- Ajusta el **Quantum** para Round Robin (0.5 - 10.0)
- Usa **🔄 Limpiar datos** para comenzar de nuevo

### 3. Simulación

1. Ve a **▶️ Simulación**
2. Selecciona los algoritmos a simular
3. Haz clic en **▶️ Ejecutar simulación**
4. Visualiza:
   - **Diagrama de Gantt:** Cronograma visual
   - **Métricas Individuales:** Tabla de procesos
   - **Métricas Agregadas:** Resumen del algoritmo

**Interacción con gráficos:**
- Amplía/reduce (zoom in/out)
- Pausa al pasar el ratón (hover) para ver detalles
- Descarga como PNG (ícono en esquina superior derecha)

### 4. Comparación

1. Ve a **📊 Comparación**
2. Selecciona la métrica a comparar:
   - Espera media ⭐ (más importante)
   - Retorno medio
   - Respuesta media
   - Utilización CPU
   - Throughput
   - Cambios de contexto
3. Visualiza:
   - Gráfico comparativo
   - Tabla de resultados
   - Mejores algoritmos por métrica
   - Gráfico radar (múltiples métricas)

### 5. Teoría

Ve a **📚 Teoría** para:
- Explicaciones de conceptos
- Descripción detallada de cada algoritmo
- Definición de todas las métricas
- Ventajas y desventajas

## Ejemplos de Ejecución

### Ejemplo 1: Básico

**Entrada:**
```
P1: Llegada=0, Ejecución=7, Prioridad=0
P2: Llegada=2, Ejecución=4, Prioridad=0
P3: Llegada=3, Ejecución=2, Prioridad=0
P4: Llegada=5, Ejecución=5, Prioridad=0
```

**Resultados esperados:**

| Algoritmo | Espera Media | Retorno Medio | Utilización |
|-----------|-------------|---------------|------------|
| FCFS | 4.75 | 11.75 | 100% |
| SJF | 3.25 | 10.25 | 100% |
| SRTF | 2.75 | 9.75 | 100% |
| RR (Q=2) | 4.75 | 11.75 | 100% |

### Ejemplo 2: Con Prioridades

**Entrada:**
```
P1: Llegada=0, Ejecución=7, Prioridad=2
P2: Llegada=2, Ejecución=4, Prioridad=1 (mayor)
P3: Llegada=3, Ejecución=2, Prioridad=3
P4: Llegada=5, Ejecución=5, Prioridad=2
```

**Observar:** Cómo P2 se ejecuta antes que P1 en prioridad.

## Pruebas Automatizadas

El proyecto incluye 60+ casos de prueba que validan:

✅ Cada algoritmo implementado  
✅ Validez de cronogramas  
✅ Cálculo correcto de métricas  
✅ Manejo de casos especiales  
✅ Integración entre módulos  

### Ejecutar pruebas

```powershell
# Todos los tests
pytest

# Con detalle
pytest -v

# Pruebas de un algoritmo específico
pytest tests/test_algorithms.py::TestFCFS -v

# Con cobertura
pytest --cov=. tests/
```

**Resultado esperado:**
```
======================= 60 passed in 1.23s =======================
```

## Limitaciones y Supuestos

### Supuestos
- Se conoce el tiempo de ejecución (burst time) de antemano
- No hay I/O ni interrupciones del sistema
- No hay procesos en tiempo real
- Tiempos son unidades abstractas (no segundos específicos)
- Prioridades son estáticas (no cambian durante ejecución)

### Limitaciones
- Máximo ~20 procesos recomendado para visualización óptima
- No simula contexto: no hay costo de cambio de contexto
- No hay soporte para multi-procesador
- La prioridad 0 = máxima (no cambiar convención)
- El quantum debe ser positivo para Round Robin

### Rendimiento
- ~100 procesos pueden procesarse en < 1 segundo
- Visualización óptima: 2-15 procesos
- Visualización aceptable: 15-20 procesos
- > 20 procesos: rendimiento puede degradarse

## Validación de Entrada

La aplicación valida:

```python
✓ Tiempos de llegada ≥ 0
✓ Tiempos de ejecución > 0
✓ Prioridades ≥ 0
✓ Quantum > 0
✗ IDs vacíos
✗ Valores negativos
✗ Valores inválidos (no numéricos)
```

## Mensajes de Error Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "Tiempo de ejecución debe ser > 0" | Burst time = 0 o negativo | Ingresa valor > 0 |
| "Tiempo de llegada negativo" | Arrival time < 0 | Ingresa valor ≥ 0 |
| "Debes seleccionar al menos un algoritmo" | No hay algoritmos seleccionados | Marca al menos uno |
| "No hay resultados de simulación" | No ejecutó simulación | Primero ejecuta simulación |

## Configuración Recomendada

### Para aprender FCFS
```
Procesos: 3-5
Quantum: N/A
Tiempo: ~5 minutos
```

### Para entender preemption
```
Procesos: 5-7
Quantum: 1-2 (para ver cambios)
Tiempo: ~10 minutos
Algoritmos: SRTF, Priority Preemptive
```

### Para optimización
```
Procesos: 10-15 (datos reales)
Quantum: Ajustar según objetivo
Comparar: FCFS vs SJF vs RR
```

## Contribuciones y Mejoras Futuras

Posibles extensiones:
- [ ] Soporte para multi-procesador
- [ ] Simulación de I/O y context switch overhead
- [ ] Algoritmos adicionales (MLQ, MLFQ)
- [ ] Importar/exportar escenarios en CSV
- [ ] Histórico de simulaciones
- [ ] Análisis estadístico avanzado
- [ ] Soporte para multi-idioma

## Solución de Problemas

### La aplicación no inicia
```powershell
# Verifica Python
python --version

# Reinstala dependencias
pip install -r requirements.txt --force-reinstall
```

### Los gráficos no se muestran
```powershell
# Plotly puede necesitar actualización
pip install --upgrade plotly
```

### Errores en pruebas
```powershell
# Ejecuta con verbose
pytest -vv tests/test_algorithms.py

# Busca el test que falla y consulta el error
```

## Referencias y Recursos

**Libros:**
- Operating System Concepts (Silberschatz, Galvin, Gagne)
- Modern Operating Systems (Tanenbaum)

**Tópicos relacionados:**
- Scheduling Algorithms
- CPU Utilization
- Context Switching
- Process Management

## Licencia

Este proyecto es de código abierto y de uso educativo.

## Autor

Desarrollado como proyecto académico para Ingeniería de Sistemas - 2026

## Contacto y Soporte

Para reportar bugs o sugerencias, contacta al equipo de desarrollo.

---

## ¡Comenzar Ahora!

1. **Instala:** `pip install -r requirements.txt`
2. **Ejecuta:** `streamlit run app.py`
3. **Aprende:** Explora cada algoritmo con ejemplos interactivos
4. **Experimenta:** Crea tus propios escenarios
5. **Comparte:** Usa los gráficos en tu presentación

**¡Disfruta aprendiendo sobre planificación de procesos! 🚀**
