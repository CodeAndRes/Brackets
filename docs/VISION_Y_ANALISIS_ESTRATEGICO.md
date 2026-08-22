# 🧠 Visión Estratégica: Arquitectura de Trazabilidad Total e Interoperabilidad con IA

> **Documento de Análisis y Propuesta para el Sistema Brackets**
> **Fecha:** 22 de Agosto, 2026

---

## 1. El Dilema del "Arrastre de Tareas" (Rollover): ¿Vale la pena guardarlas semana tras semana?

### El problema del modelo antiguo (Markdown puro)
* Si una tarea estaba 4 semanas sin hacerse, se copiaba 4 veces en 4 archivos semanales distintos.
* Al hacer la **consolidación mensual**, aparecía 4 veces repetida.
* **Consecuencia:** Ruido visual extremo, archivos pesados y una IA confundida pensando que hiciste o planificaste 4 tareas distintas.

### La solución con el Motor Relacional YAML-First
* **La tarea vive UNA SOLA VEZ en la base de datos (`tasks.yaml`)**.
* En lugar de duplicar texto, la tarea almacena su ciclo de vida real:
  ```yaml
  - id: TSK-0120
    title: "Documentar proyecto Koerber End2End"
    project_id: KOERBER_E2E
    status: done
    created_at: "2026-08-03"      # Nació en Semana 32
    completed_at: "2026-08-20"    # Se resolvió en Semana 34
    rollover_count: 2             # Estuvo viva 2 semanas antes de cerrarse
  ```

### ¿Cómo debe ser la Consolidación Mensual? (Limpia y con Alto Valor)
En los archivos mensuales (`[2026][08]MonthTopics.md`), **NO debemos repetir tareas arrastradas**. La consolidación debe ser una **foto ejecutiva de alto impacto**:
1. 🏆 **Logros del Mes:** Tareas con `completed_at` en ese mes (agrupadas por Proyecto).
2. 📝 **Decisiones y Notas Clave:** Extraídas de `notes.yaml` filtradas por el mes.
3. ⏳ **Backlog Abierto:** Tareas que siguen `pending` al finalizar el mes (sin duplicados).

---

## 2. Diseñado para Humanos y Optimizado para Inteligencia Artificial (M365 Copilot / Rovo)

Para que una IA (como Microsoft 365 Copilot o un Agente de Jira/Rovo) entienda perfectamente tu trabajo, necesita **estructura sin ruido**:

```
                  ┌───────────────────────────────┐
                  │    FUENTES ESTRUCTURADAS      │
                  │ (tasks.yaml, notes, projects) │
                  └──────────────┬────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
     ┌───────────────────────┐       ┌───────────────────────┐
     │  VISTA HUMANA (CLI)   │       │ VISTA IA / COPILOT    │
     │ • Hub Diario interact │       │ • Resumen por Proyecto│
     │ • Bitácora Markdown   │       │ • Tareas resueltas    │
     │ • Navegación rápida   │       │ • Contexto para OneNot│
     └───────────────────────┘       └───────────────────────┘
```

### ¿Por qué este modelo es perfecto para una IA?
1. **Contexto por Proyecto instantáneo:**
   Si le preguntas a la IA: *"¿Qué avances hemos hecho en Koerber este mes?"*, la IA no tiene que leer 20 archivos sueltos; simplemente consulta `project_id: KOERBER_E2E` y tiene todas las tareas resueltas y notas asociadas en 1 segundo.
2. **Cálculo de Tiempos y Carga de Trabajo (Lead Time):**
   La IA puede decirte: *"Tienes 3 tareas en InfluxDB que llevan más de 15 días pendientes, ¿quieres que bloqueemos tiempo en tu calendario de Outlook para abordarlas?"*.
3. **Exportación limpia a OneNote:**
   Podemos generar un volcado automático y sintético a una carpeta de OneNote sincronizada con tu cuenta corporativa para que tu agente de M365 Copilot trabaje directamente con tus datos de Brackets.

---

## 3. Las 3 Mejoras Clave que proponemos para mañana

### 1️⃣ Vista por Proyecto (Project Hub)
Poder consultar en consola o generar un resumen Markdown agrupado por proyecto:
* `AMR_LOGISTICS`: 26 tareas hechas, 4 pendientes.
* `ROVO_AI`: 5 tareas hechas, 3 pendientes.

### 2️⃣ Exportador "AI-Context Pack"
Un comando `python run_brackets.py --export-ai` (o dentro de Tools) que genere un único documento Markdown limpio y sin ruido con:
* Proyectos activos.
* Tareas terminadas en los últimos 7/30 días.
* Decisiones técnicas tomadas.
*(Ideal para pegárselo a ChatGPT, Claude, Rovo o sincronizarlo con OneNote/Copilot).*

### 3️⃣ Rollover Inteligente
Al crear la Semana 36, el sistema mira las tareas que quedaron `pending` en la Semana 35 y las propone en el Hub Diario sin duplicar un solo byte de texto en la base de datos.
