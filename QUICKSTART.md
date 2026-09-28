# 🚀 GUÍA DE INICIO RÁPIDO

## Requisitos Previos
- Python 3.10 o superior (verificado con Python 3.13.2)
- pip (gestor de paquetes de Python)

## Instalación (3 pasos)

### Paso 1: Instalar Dependencias
```bash
cd /workspace/cpu_scheduler_simulator
pip install -r requirements.txt
```

Esto instala:
- streamlit (interfaz web)
- plotly (gráficos interactivos)
- pandas (análisis de datos)
- pytest (pruebas automatizadas)

**Tiempo estimado:** 2-3 minutos

### Paso 2: Verificar Instalación
```bash
python -m pytest tests/test_algorithms.py -v
```

Deberías ver: **33 passed** ✅

### Paso 3: Ejecutar el Simulador

#### Opción A: Interfaz Web (RECOMENDADO)
```bash
streamlit run app.py
```

Se abrirá automáticamente en `http://localhost:8501`

#### Opción B: Línea de Comandos
```bash
python -c "from algorithms import Process, create_scheduler; from metrics import calculate_metrics; p=[Process('P1',0,8),Process('P2',1,4)]; r=create_scheduler('FCFS',p).schedule(); m=calculate_metrics(r); print(f'Avg WT: {m.avg_waiting_time:.2f}')"
```

---

## 📚 Estructura del Proyecto

| Archivo | Propósito |
|---------|-----------|
| `algorithms.py` | 6 algoritmos de planificación (FCFS, SJF, SRTF, RR, Priority-NonPreempt, Priority-Preempt) |
| `metrics.py` | Cálculo de turnaround time, waiting time, response time, utilización, etc. |
| `visualization.py` | Gráficos Gantt, comparativos y radar charts |
| `app.py` | Interfaz Streamlit con 6 páginas interactivas |
| `tests/test_algorithms.py` | 33 tests de verificación |
| `README.md` | Documentación completa (600+ líneas) |
| `SUMMARY.md` | Resumen ejecutivo del proyecto |

---

## 🎮 USO DE LA INTERFAZ WEB

### 1️⃣ Crear Procesos
- Ve a **Input**
- Ingresa: Nombre, Arrival Time, Burst Time, Priority
- Click **Add Process**

### 2️⃣ Ejecutar Simulación
- Ve a **Simulation**
- Selecciona algoritmo (FCFS, SJF, SRTF, RR, Priority, etc.)
- Para Round Robin, ajusta el quantum (default: 2.0)
- El diagrama de Gantt aparece automáticamente

### 3️⃣ Comparar Algoritmos
- Ve a **Comparison**
- Selecciona métrica (Waiting Time, Turnaround Time, etc.)
- Compara resultados entre los 6 algoritmos

### 4️⃣ Aprender
- Ve a **Theory** para explicaciones detalladas de cada algoritmo
- Ejemplos paso a paso de ejecución

---

## 📊 EJEMPLO RÁPIDO

```python
from algorithms import Process, create_scheduler
from metrics import calculate_metrics

# Crear 3 procesos
procesos = [
    Process("P1", arrival_time=0, burst_time=8),
    Process("P2", arrival_time=1, burst_time=4),
    Process("P3", arrival_time=2, burst_time=2),
]

# Ejecutar FCFS
scheduler = create_scheduler("FCFS", procesos)
resultado = scheduler.schedule()

# Mostrar resultados
print(f"Tiempo total: {resultado.total_time}")
print(f"Cambios de contexto: {resultado.context_switches}")

# Calcular métricas
metricas = calculate_metrics(resultado)
print(f"Avg Waiting Time: {metricas.avg_waiting_time:.2f}")
print(f"Avg Turnaround Time: {metricas.avg_turnaround_time:.2f}")
print(f"CPU Utilization: {metricas.cpu_utilization:.1f}%")
```

---

## 🔧 PROBLEMAS COMUNES

### ❌ "No module named 'streamlit'"
```bash
pip install streamlit
```

### ❌ "ModuleNotFoundError: No module named 'plotly'"
```bash
pip install -r requirements.txt
```

### ❌ "Port 8501 already in use"
```bash
streamlit run app.py --server.port 8502
```

### ❌ Tests fallando
Asegúrate de que todas las dependencias están instaladas:
```bash
pip install -r requirements.txt --upgrade
python -m pytest tests/test_algorithms.py -v
```

---

## ✅ VERIFICACIÓN FINAL

Todos estos comandos deberían funcionar:

```bash
# Test 1: Algoritmos funcionan
python -c "from algorithms import Process, SRTFScheduler; print('✓ SRTF importado')"

# Test 2: Métricas funcionan
python -c "from metrics import calculate_metrics; print('✓ Métricas importadas')"

# Test 3: Visualización funciona
python -c "from visualization import create_gantt_chart; print('✓ Visualización importada')"

# Test 4: UI funciona
python -c "import streamlit; print('✓ Streamlit disponible')"

# Test 5: Suite de pruebas
python -m pytest tests/test_algorithms.py -q
# Deberías ver: 33 passed in 0.05s
```

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [ ] Python 3.10+ instalado: `python --version`
- [ ] Dependencias instaladas: `pip list | grep streamlit`
- [ ] Tests pasando: `pytest tests/test_algorithms.py --tb=short`
- [ ] Streamlit funciona: `streamlit run app.py`
- [ ] Puedes crear procesos en la UI
- [ ] Los gráficos se generan correctamente
- [ ] Puedes comparar algoritmos

---

## 🎯 COMANDOS CLAVE

```bash
# Instalar todo
pip install -r requirements.txt

# Ejecutar tests
pytest tests/test_algorithms.py -v

# Ejecutar interfaz web
streamlit run app.py

# Test rápido
python -c "from algorithms import *; print('✓ OK')"

# Ver versiones
python --version
pip show streamlit plotly pytest
```

---

## 📞 SOPORTE

Si algo no funciona:

1. **Verifica Python:** `python --version` (debe ser 3.10+)
2. **Verifica pip:** `pip --version`
3. **Reinstala dependencias:** `pip install -r requirements.txt --force-reinstall`
4. **Lee README.md:** Tiene sección de troubleshooting
5. **Revisa SUMMARY.md:** Documentación técnica completa

---

## 🎉 ¡LISTO!

Ya está todo configurado. Ejecuta:

```bash
streamlit run app.py
```

Y comienza a usar el simulador. 🚀
