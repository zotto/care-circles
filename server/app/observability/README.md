# Observability Module

This module provides comprehensive observability and evaluation for the Care Circles AI agent pipeline using Comet Opik.

## Overview

The observability module instruments the 5-agent pipeline (A1-A5) with:
- **Distributed Tracing**: Full execution traces with Opik
- **Automated Evaluation**: 5 custom evaluators for quality assessment
- **Real-time Metrics**: Performance and quality metrics collection
- **Experiment Tracking**: A/B testing and optimization support

## Module Structure

```
observability/
├── __init__.py                    # Module exports
├── opik_client.py                 # Opik integration client
├── evaluators.py                  # Custom evaluators (5)
├── metrics.py                     # Metrics collection and aggregation
└── instrumented_orchestrator.py   # Instrumented agent pipeline
```

## Components

### OpikClient (`opik_client.py`)

Centralized Opik integration client.

**Features**:
- Automatic trace creation with context managers
- Experiment logging and tracking
- Metrics logging
- Graceful degradation when Opik unavailable

**Usage**:
```python
from app.observability import opik_client

# Check if enabled
if opik_client.is_enabled():
    print("Opik is ready!")

# Trace an agent execution
with opik_client.trace_agent(
    agent_name="A1_intake_analyst",
    task_name="analyze_needs",
    input_data=care_request.narrative
) as trace:
    result = agent.execute()
    trace.log_output(result)
    trace.log_metric("confidence", 0.95)
```

### Evaluators (`evaluators.py`)

Five custom evaluators for care plan quality assessment.

#### 1. TaskQualityEvaluator

Evaluates individual tasks and task lists for:
- **Actionability**: Specific, actionable tasks
- **Clarity**: Clear descriptions
- **Appropriateness**: Suitable for volunteers
- **Context**: Sufficient background

**Usage**:
```python
from app.observability import TaskQualityEvaluator

evaluator = TaskQualityEvaluator()
result = evaluator.evaluate_tasks(tasks, care_request.narrative)
print(f"Quality Score: {result.score:.3f}")
print(f"Reason: {result.reason}")
```

#### 2. BoundaryComplianceEvaluator

Validates safety and boundary adherence:
- Medical overreach detection
- Financial risk identification
- Stated boundary compliance

**Usage**:
```python
from app.observability import BoundaryComplianceEvaluator

evaluator = BoundaryComplianceEvaluator()
result = evaluator.evaluate(
    tasks,
    care_request.narrative,
    care_request.constraints,
    care_request.boundaries
)
print(f"Compliance Score: {result.score:.3f}")
if result.metadata.get("violations"):
    print(f"Violations: {result.metadata['violations']}")
```

#### 3. CompletenessEvaluator

Assesses comprehensive need coverage:
- Category diversity
- Priority distribution
- Need matching

**Usage**:
```python
from app.observability import CompletenessEvaluator

evaluator = CompletenessEvaluator()
result = evaluator.evaluate(tasks, needs_map)
print(f"Completeness Score: {result.score:.3f}")
```

#### 4. ClarityEvaluator

Evaluates communication quality:
- Language simplicity
- Structure and organization
- Documentation completeness

**Usage**:
```python
from app.observability import ClarityEvaluator

evaluator = ClarityEvaluator()
result = evaluator.evaluate_review_packet(review_packet)
print(f"Clarity Score: {result.score:.3f}")
```

#### 5. PipelinePerformanceEvaluator

Tracks system efficiency:
- Execution time
- Success rates
- Resource balance

**Usage**:
```python
from app.observability import PipelinePerformanceEvaluator

evaluator = PipelinePerformanceEvaluator()
evaluator.record_agent_execution("A1", 15.2, True)
result = evaluator.evaluate_pipeline(total_duration)
print(f"Performance Score: {result.score:.3f}")
```

### MetricsCollector (`metrics.py`)

Collects and aggregates metrics from agent executions.

**Features**:
- Real-time metrics collection
- Statistical summaries (avg, min, max)
- Historical tracking
- Export capabilities

**Usage**:
```python
from app.observability import MetricsCollector, AgentMetrics, PipelineMetrics

collector = MetricsCollector()

# Record agent metrics
agent_metrics = AgentMetrics(
    agent_name="A1_intake_analyst",
    task_name="analyze_needs",
    duration_seconds=15.2,
    success=True,
    input_length=500,
    output_length=1200
)
collector.record_agent_metrics(agent_metrics)

# Get statistics
stats = collector.get_agent_statistics("A1_intake_analyst")
print(f"Average Duration: {stats['avg_duration']:.2f}s")
print(f"Success Rate: {stats['success_rate'] * 100:.1f}%")
```

### InstrumentedOrchestrator (`instrumented_orchestrator.py`)

Wraps the standard orchestrator with full observability.

**Features**:
- Automatic tracing for all agents
- Real-time metrics collection
- Automated evaluation
- Experiment tracking

**Usage**:
```python
from app.observability import InstrumentedOrchestrator

orchestrator = InstrumentedOrchestrator()

# Run with full observability
review_packet = orchestrator.run_pipeline_sync(
    care_request=care_request,
    experiment_name="gpt4_baseline",
    experiment_params={
        "model": "gpt-4",
        "temperature": 0.7
    }
)

# Metrics are automatically collected and logged
```

## Configuration

Set environment variables in `.env`:

```bash
# Opik Configuration
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=care-circles
OPIK_PROJECT_NAME=care-circles-hackathon
```

## Metrics Tracked

### Agent-Level Metrics
- Execution duration
- Success/failure status
- Input/output sizes
- Custom metrics

### Pipeline-Level Metrics
- Total execution time
- Task count
- Overall success
- Evaluation scores

### Evaluation Scores (0.0-1.0)
- Task Quality (target: ≥ 0.75)
- Boundary Compliance (target: 1.0)
- Completeness (target: ≥ 0.80)
- Clarity (target: ≥ 0.75)
- Performance (target: ≥ 0.85)
- Overall (weighted average, target: ≥ 0.80)

## API Integration

The observability module is exposed via REST API at `/api/observability/*`:

- `GET /api/observability/metrics/summary` - Comprehensive overview
- `GET /api/observability/metrics/pipeline` - Pipeline statistics
- `GET /api/observability/metrics/agent/{name}` - Agent-specific metrics
- `GET /api/observability/metrics/evaluations` - Evaluation scores
- `GET /api/observability/dashboard/judge` - Judge dashboard
- `GET /api/observability/report/comprehensive` - Full report

## Testing

### Test Evaluators

```bash
cd server
python test_evaluators.py
```

### Run Demo

```bash
cd server
python demo_observability.py
```

## Extending

### Add a Custom Evaluator

1. Create evaluator class in `evaluators.py`:

```python
class MyCustomEvaluator:
    def evaluate(self, data) -> EvaluationResult:
        score = 0.0
        # Your evaluation logic
        return EvaluationResult(
            score=score,
            reason="Your reasoning",
            metadata={"key": "value"}
        )
```

2. Add to `InstrumentedOrchestrator`:

```python
self.custom_evaluator = MyCustomEvaluator()

# In run_pipeline_sync:
custom_eval = self.custom_evaluator.evaluate(data)
trace.log_metric("custom_score", custom_eval.score)
```

### Add Custom Metrics

```python
# In agent execution
trace.log_metric("custom_metric", value)

# Or via metrics collector
agent_metrics.custom_metrics["my_metric"] = value
```

## Best Practices

1. **Always use context managers** for tracing:
   ```python
   with opik_client.trace_agent(...) as trace:
       # Your code
       trace.log_output(result)
   ```

2. **Record metrics immediately** after execution:
   ```python
   collector.record_agent_metrics(metrics)
   ```

3. **Provide detailed metadata**:
   ```python
   trace = opik_client.trace_agent(
       agent_name="A1",
       task_name="analyze",
       input_data=data,
       metadata={
           "care_request_id": request.id,
           "experiment_id": exp_id,
           "custom_field": "value"
       }
   )
   ```

4. **Handle errors gracefully**:
   ```python
   try:
       result = agent.execute()
       trace.log_output(result)
   except Exception as e:
       trace.log_error(e)
       raise
   ```

## Performance Considerations

- **Tracing overhead**: ~50-100ms per trace
- **Evaluation overhead**: ~10-50ms per evaluator
- **Total overhead**: ~5-10% of pipeline execution time
- **Graceful degradation**: Minimal impact if Opik unavailable

## Troubleshooting

### Opik Not Enabled

**Symptom**: "Opik observability is DISABLED"

**Solutions**:
1. Check `OPIK_API_KEY` is set in `.env`
2. Verify API key is valid
3. Ensure `opik` package is installed: `pip install opik>=0.2.0`

### No Traces in Dashboard

**Symptom**: Traces not appearing in Opik dashboard

**Solutions**:
1. Verify API key is correct
2. Check workspace name matches
3. Ensure at least one care request has been processed
4. Check logs for Opik errors

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'opik'`

**Solution**:
```bash
pip install opik>=0.2.0
```

## Documentation

- **Full Documentation**: `../../../OBSERVABILITY.md`
- **Setup Guide**: `../../../OPIK_SETUP.md`
- **Judge Guide**: `../../../JUDGE_EVALUATION.md`
- **Architecture**: `../../../ARCHITECTURE_DIAGRAM.md`

## Support

For issues or questions:
1. Check the documentation files
2. Review the demo scripts
3. Examine the test scripts
4. Consult Opik documentation: https://www.comet.com/docs/opik/
