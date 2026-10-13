# AI-QA Evaluation Set

This directory contains a small, reproducible defect-detection evaluation.
The five mutations are disabled by default and are only enabled for evaluation
processes through `AI_TEST_MUTATIONS`.

## Metrics

```text
Bug Recall = known bugs detected / known bugs enabled
Precision = true bugs reported / all bugs reported
```

Run the manual baseline using [manual_baseline.md](manual_baseline.md). For an
Agent comparison, use the same PRD and test data, run the Agent at least three
times, and record each run's `run_id`, detected bug IDs, duration, and token or
API cost if available.

The current project has one intentionally visible bug by default. The
evaluation mutations add four controlled variants without changing the normal
default behavior of the demo.
