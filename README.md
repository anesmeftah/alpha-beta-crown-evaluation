# Reproducibility Evaluation of α,β-CROWN on VNN-COMP Benchmarks

## Objective

The goal of this project is to evaluate the **reproducibility** and **performance** of the **α,β-CROWN** neural network verifier by reproducing official **VNN-COMP** benchmark results and comparing them with locally generated results.

The study aims to determine how closely an independent execution of α,β-CROWN matches the official competition results and to investigate the factors that may lead to discrepancies.

---

## Research Questions

- **RQ1:** Can the official VNN-COMP results be reproduced using the public α,β-CROWN implementation?
- **RQ2:** What level of agreement exists between reproduced and official verification outcomes?
- **RQ3:** What factors contribute to differences between reproduced and official results?

---

## Evaluation Metrics

The evaluation focuses on the following aspects:

### Verification Result Agreement

Measure the consistency of verification outcomes between local and official executions.

Possible outcomes include:

- `SAT`
- `UNSAT`
- `TIMEOUT`
- `UNKNOWN` (if applicable)

Metrics:
- Number of matching results
- Number of mismatches
- Overall agreement percentage
- Confusion matrix

---

### Runtime Performance

Compare execution times for each verification instance.

Metrics:
- Average runtime
- Median runtime
- Runtime distribution
- Runtime ratio (Local / Official)

---

### Resource Utilization

Measure the computational resources required during verification.

Metrics may include:

- GPU memory usage
- CPU utilization
- Number of Branch-and-Bound (BaB) nodes explored
- Peak memory consumption (when available)

---

### Numerical Differences

Analyze differences in numerical behavior that may affect verification results.

Examples include:

- Lower and upper bound variations
- Branch-and-Bound node counts
- Floating-point precision effects
- Solver statistics

---

### Causes of Divergence

Investigate mismatches between official and reproduced results.

Potential causes include:

- Different α,β-CROWN versions or commits
- CUDA, PyTorch, or dependency versions
- Hardware differences
- Configuration parameters
- Timeout settings
- Branching heuristics
- Numerical precision
- Non-deterministic GPU operations

---

## Experimental Workflow

1. Reproduce an official VNN-COMP benchmark using the released α,β-CROWN implementation.
2. Collect structured verification results.
3. Compare reproduced results with the official benchmark results.
4. Compute agreement and performance metrics.
5. Analyze discrepancies and identify their possible causes.
6. Document observations and conclusions.

---

## Expected Outcome

The final outcome of this evaluation is a quantitative assessment of the reproducibility of α,β-CROWN on VNN-COMP benchmarks, including:

- Verification result agreement
- Performance comparison
- Analysis of numerical differences
- Identification of reproducibility challenges
- Recommendations for improving reproducibility in neural network verification experiments