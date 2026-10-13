# Agent Evaluation Summary

Date: 2026-10-13

The Agent was run three times against each of five controlled defect variants.
The run produced 15 trials in total.

| Bug | Detected | Trials | Detection rate | Average duration |
|---|---:|---:|---:|---:|
| B1 username minimum length | 3 | 3 | 100% | 15.74s |
| B2 password minimum length | 3 | 3 | 100% | 16.56s |
| B3 duplicate username | 2 | 3 | 66.67% | 17.36s |
| B4 incorrect password accepted | 3 | 3 | 100% | 14.70s |
| B5 nonexistent user accepted | 2 | 3 | 66.67% | 15.44s |
| **Total** | **13** | **15** | **86.67%** | **15.96s average** |

All five defect types were detected at least once. The 86.67% figure is
trial-level detection recall, not a claim that every run is deterministic.
Manual baseline, precision, and cost were not measured in this run.
