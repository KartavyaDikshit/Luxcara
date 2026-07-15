# E2E Test Infra: AI Concepts Interactive Demo

## Test Philosophy
- Opaque-box, requirement-driven. No internal design dependencies.
- Methodologies: Category-Partition, Boundary Value Analysis, Pairwise Combinatorial, Real-World Scenarios.

## Feature Inventory
| # | Feature | Source | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|--------|:------:|:------:|:------:|:------:|
| 1 | Directory Scaffolding | R1 | 5 | 5 | ✓ | ✓ |
| 2 | Interactive Notebooks (JSON & Execution) | R2 | 5 | 5 | ✓ | ✓ |
| 3 | Verification Script `verify_project.py` | R3 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test runner: pytest / python script
- Verification channels: Directory checks, JSON structure parsing, python execution verification, exit code verification.
