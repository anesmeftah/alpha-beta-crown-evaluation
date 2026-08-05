# Reproducibility Evaluation of α,β-CROWN on VNN-COMP Benchmarks

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 1. Introduction

Formally verifying neural networks is critical for safety-critical applications such as autonomous driving, medical systems, and robotics. The **Verification of Neural Networks Competition (VNN-COMP)** provides a standardized benchmark suite to evaluate state-of-the-art verifiers.

This repository focuses on evaluating the **reproducibility and performance** of **α,β-CROWN** (alpha-beta-CROWN), an award-winning neural network verifier. By running independent local evaluations against official competition benchmarks (starting with VNN-COMP **CIFAR2020**), this project aims to:
- Assess verification result consistency (SAT / UNSAT / Timeout / Unknown agreement rates).
- Quantify performance and runtime variations across different execution environments.
- Provide automated tools for log parsing, dataset normalization, and comparative statistical reporting.

---

## 2. What is α,β-CROWN?

**α,β-CROWN** is a state-of-the-art neural network verifier based on efficient bound propagation and Branch-and-Bound (BaB) search. It combines linear bound propagation methods with optimized parameters to achieve both efficiency and completeness.

Key components of α,β-CROWN include:
- **α-CROWN (Optimized Linear Bound Propagation):** Uses gradient-based optimization to tune variable lower/upper bounds ($\alpha$) for non-linear activation functions (e.g., ReLU), yielding significantly tighter bounds than standard CROWN.
- **β-CROWN (Branch-and-Bound Verification):** Incorporates intermediate neuron split decisions ($\beta$ parameters) into bound propagation, enabling rapid, GPU-accelerated Branch-and-Bound reasoning for complete verification.
- **Auto-LiRPA Library:** Built on top of `auto_LiRPA`, an automatic linear bound propagation library for general PyTorch models.

α,β-CROWN has consistently won top awards in **VNN-COMP 2021, 2022, 2023, 2024, and 2025**.

### 🔗 Resource Links

- **Official Repository:** [Verified-Intelligence/alpha-beta-CROWN](https://github.com/Verified-Intelligence/alpha-beta-CROWN)
- **Core Library (`auto_LiRPA`):** [Verified-Intelligence/auto_LiRPA](https://github.com/Verified-Intelligence/auto_LiRPA)
- **VNN-COMP Official Site:** [VNN-COMP Standardized Verification Competition](https://sites.google.com/view/vnn2020)
- **VNN-COMP Benchmarks Repository:** [vnncomp/vnncomp2020_benchmarks](https://github.com/vnncomp/vnncomp2020_benchmarks)
- **Key Publications:**
  - *α-CROWN Paper:* [Fast and Complete Neural Network Verification via Fast Bounds (NeurIPS 2021)](https://arxiv.org/abs/2103.06624)
  - *β-CROWN Paper:* [Beta-CROWN: Efficient Bound Propagation with Branch and Bound for Neural Network Verification (NeurIPS 2021)](https://arxiv.org/abs/2103.06624)
  - *General LiRPA Paper:* [Automatic Perturbation Analysis for Scalable Certified Robustness (NeurIPS 2020)](https://arxiv.org/abs/2002.12920)

---

## 3. How to Use This Repository

### 📁 Project Structure

```text
alpha-beta-crown-evaluation/
├── configs/            # Configuration files for benchmark experiments
├── data/               # Evaluation datasets
│   ├── official/       # Official VNN-COMP benchmark results (e.g., cifar2020.csv, a-b-CROWN.csv)
│   └── experiments/    # Local experiment logs (.txt) and parsed outputs (.csv)
├── figures/            # Generated plots and evaluation diagrams
│   ├── CIFAR2020 confusion matrix.png
│   └── solved over time curve.png
├── notebooks/          # Jupyter notebooks for interactive analysis
│   └── CIFAR2020_Evaluation.ipynb
├── reports/            # Generated summary reports and documentation
├── scripts/            # Parsing and result extraction utilities
│   ├── extract_official_results.py  # Filters official results per benchmark
│   ├── parser.py                    # Parses raw α,β-CROWN execution log files
│   └── results.py                   # Converts parsed execution logs to standardized CSV format
├── README.md           # Project documentation
└── requirements.txt    # Python dependencies
```

### ⚙️ Prerequisites & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anesmeftah/alpha-beta-crown-evaluation.git
   cd alpha-beta-crown-evaluation
   ```

2. **Set up Python Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install pandas numpy matplotlib seaborn scikit-learn
   ```

### 🚀 Running the Evaluation Workflow

1. **Extract Official Results:**
   Extract official VNN-COMP results from the master CSV into benchmark-specific datasets:
   ```bash
   python scripts/extract_official_results.py
   ```

2. **Parse Execution Logs to CSV:**
   Convert raw α,β-CROWN log files into structured CSV format:
   ```bash
   python scripts/results.py data/experiments/txt/cifar2020_run.log data/experiments/csv/cifar2020.csv
   ```

3. **Run the Notebook Analysis:**
   Launch Jupyter Notebook to inspect comparative metrics, confusion matrices, and runtime curves:
   ```bash
   jupyter notebook notebooks/CIFAR2020_Evaluation.ipynb
   ```

---

## 4. Benchmark Description & Evaluation Results

### 🧪 Benchmark Overview: VNN-COMP CIFAR2020

The **CIFAR2020** benchmark from VNN-COMP evaluates certified robustness on Convolutional Neural Networks (ResNet-like architectures) trained on the CIFAR-10 dataset under $L_\infty$ perturbation bounds ($\epsilon = 2/255$ and $\epsilon = 8/255$).

- **Total Test Instances:** 147 verification properties (`ONNX` models coupled with `VNNLIB` specification constraints).
- **Timeout Limit:** 300 seconds per property.

### 📊 Results Summary

| Metric | Official VNN-COMP | Local Reproduction | Agreement Status |
| :--- | :---: | :---: | :---: |
| **Total Evaluated** | 147 | 147 | 100% Evaluated |
| **UNSAT (Safe)** | 103 | 103 | 100% Match |
| **SAT (Unsafe / CEX)** | 35 | 34 | 97.1% Match |
| **Timeout** | 9 | 0 | Distinct from `unknown` |
| **Unknown** | 0 | 10 | Distinct from `timeout` |
| **Overall Verdict Match** | **137 / 147** | — | **93.2% Agreement** |
---

## 5. Conclusion

This reproducibility study confirms that **α,β-CROWN is reproducible** across independent execution environments, achieving a **93.2% verdict agreement rate** on the VNN-COMP CIFAR2020 benchmark.

### Key Observations & Takeaways:
1. **High Reliability:** Both SAT (counterexample generation) and UNSAT (safety certification) results transfer consistently between systems.
2. **Sensitivity on Edge Instances:** Divergences are concentrated in the slower instances near the 300-second timeout threshold, where the local run returns `unknown` instead of the official verdict.
