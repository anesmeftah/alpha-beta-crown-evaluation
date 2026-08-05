# Benchmark Assets

[![VNN-COMP](https://img.shields.io/badge/benchmark-VNN--COMP%202020-blue.svg)](https://sites.google.com/view/vnn2020)
[![Format: VNNLIB](https://img.shields.io/badge/specification-VNNLIB-green.svg)](https://www.vnnlib.org/)

## 1. Introduction

This directory contains the benchmark assets used by the reproducibility evaluation. It currently includes the **CIFAR2020** benchmark inputs and the ERAN-trained CIFAR convolutional models referenced by the α,β-CROWN configurations.

The CIFAR2020 benchmark verifies robustness properties for CIFAR-10 image classifiers. Each verification task pairs a neural-network model with a VNNLIB specification that constrains a perturbed input and requires the classifier to preserve the expected label.

---

## 2. Directory Structure

```text
benchmarks/
├── Cifar2020/                         # CIFAR2020 benchmark configuration and properties
│   ├── cifar_conv_big.yaml             # α,β-CROWN configuration for the larger CNN
│   ├── cifar_conv_small.yaml           # α,β-CROWN configuration for the smaller CNN
│   ├── instances.csv                   # Properties selected for a run
│   ├── nets/                           # ONNX benchmark-network artifact
│   ├── specs/                          # VNNLIB properties and compiled variants
│   └── src/                            # Utilities for evaluating networks and generating specs
└── models/
    └── eran/                           # ERAN CIFAR convolutional model checkpoints
        ├── cifar_conv_big_pgd.pth
        └── cifar_conv_small_pgd.pth
```

---

## 3. CIFAR2020 Benchmark

`Cifar2020/` supplies the verification properties and α,β-CROWN run configurations for the CIFAR2020 workload.

### 🧪 Verification Properties

- `specs/*.vnnlib` are the source VNNLIB property files.
- `specs/*.vnnlib.compiled` are compiled forms of those properties for use by the verification workflow.
- File names identify the CIFAR test-image index, its expected label, and the perturbation radius. For example, `00000_label_3_eps_0.00392.vnnlib` describes image `00000`, label `3`, and an $L_\infty$ radius of `0.00392`.
- Some files use `patch_...` in their names; these describe localized patch perturbations instead of a perturbation over the entire image.

`instances.csv` lists the specifications selected by the current configurations. Adjust this file to change the run set without modifying the property collection.

### ⚙️ Configurations

The two YAML files select the model checkpoint, properties, solver settings, and Branch-and-Bound timeout:

| Configuration | Model checkpoint | Batch size | Timeout |
| :--- | :--- | :---: | :---: |
| `cifar_conv_big.yaml` | `models/eran/cifar_conv_big_pgd.pth` | 64 | 120 s |
| `cifar_conv_small.yaml` | `models/eran/cifar_conv_small_pgd.pth` | 200 | 120 s |

Both configurations currently use the complete `bab` verifier with `kfsb` branching. The `root_path` and model `path` entries are absolute paths; update them if the repository is moved or checked out elsewhere.

### 🛠️ Supporting Utilities

`Cifar2020/src/` contains scripts to evaluate a network and generate specifications:

- `evaluate_network.py` evaluates a model on CIFAR inputs.
- `generate_specs.py` produces VNNLIB specifications.
- `specs_from_seed.sh` generates specifications from seeded inputs.

---

## 4. Model Checkpoints

`models/eran/` stores the PyTorch (`.pth`) checkpoints used by the CIFAR2020 YAML configurations:

- `cifar_conv_big_pgd.pth` is selected by `cifar_conv_big.yaml`.
- `cifar_conv_small_pgd.pth` is selected by `cifar_conv_small.yaml`.

These files are benchmark inputs, not generated evaluation results. Keep the checkpoint name and its configuration `model.path` in sync when replacing or relocating a model.

---

## 5. Running a Benchmark Configuration

From an α,β-CROWN installation, invoke the verifier with one of the configurations:

```bash
python complete_verifier/abcrown.py --config benchmarks/Cifar2020/cifar_conv_big.yaml
```

Use `cifar_conv_small.yaml` to run the smaller network. Before running, confirm that the absolute paths in the selected YAML file point to this checkout.

---

## 6. Planned Evaluation Protocol

The benchmark assets support a parameterized robustness study beyond a single fixed property. The workflow below records both the verification outcome and the execution cost, then uses the same data to compare perturbation sizes, classes, and network architectures.

### 1. Generate Parameterized Properties

Create `gen_props.py` to generate a VNNLIB property from an `(image_id, epsilon, target_class)` triplet in the format expected by α,β-CROWN. The generated property should constrain the input image inside the selected $L_\infty$ ball and express the desired classification condition.

### 2. Sweep the Perturbation Radius

Select 20–30 CIFAR-10 test images, **including image index `1189`** so the study remains comparable with the earlier case study. Run each image at:

```text
epsilon ∈ {1, 2, 4, 8, 16} / 255
```

Record one row per run in `results.csv`, including at minimum the image ID, true/target class, model, epsilon, verifier status, runtime, and specification path. A useful status convention is:

| Status | Meaning |
| :--- | :--- |
| `UNSAT` | The stated robustness property was proved. |
| `SAT` | A counterexample was found; the property is not robust. |
| `timeout` / `unknown` | The verifier did not determine the property within the allotted run. |

Before scheduling the full sweep, benchmark two or three images to estimate the runtime. If the full grid is impractical, use 15 images and three epsilon values while retaining the same measurement fields.

### 3. Estimate the Critical Radius $\epsilon^*$

For each image, use bisection within the interval identified by the sweep to refine the transition between robust and non-robust behaviour. Plot the resulting $\epsilon^*$ distribution. If bisection is too expensive, retain the sweep interval that brackets the transition instead of omitting the analysis.

### 4. Analyse Class Pairs

Group images by `(true class, most likely second class)` and compare the $\epsilon^*$ distributions for semantically close and distant pairs. Suggested close pairs include horse/deer and automobile/truck. This tests whether visually or semantically similar classes systematically have lower certified robustness thresholds.

### 5. Compare ConvSmall and ConvBig

Repeat the same sweep with `cifar_conv_small_pgd.pth` and `cifar_conv_big_pgd.pth` on identical images and generated properties. Compare their verifier statuses, $\epsilon^*$ values, and runtimes to separate the effect of model complexity from input difficulty. If ConvBig is prohibitively expensive, report the limitation and retain the ConvSmall results.

### 6. Profile and Extend

Use the sweep data to relate runtime to epsilon, model size, and property complexity; no additional runs are needed for this profiling step. Once the core workflow is complete, patch properties can be explored by varying only a bounded image region. A further extension is to verify a published RobustBench CIFAR-10 model and compare PGD attack outcomes with formal CROWN certification on the same images and epsilon values.

### 🔗 Resources

- [VNN-COMP 2020](https://sites.google.com/view/vnn2020)
- [VNN-COMP 2020 benchmarks](https://github.com/verivital/vnn-comp/tree/main/benchmarks)
- [α,β-CROWN](https://github.com/Verified-Intelligence/alpha-beta-CROWN)
