from __future__ import annotations

import csv
import subprocess
import sys
import time
from pathlib import Path

from gen_props import generate_property
from parser import parser as parse_results




PROJECT_ROOT = Path(__file__).resolve().parents[1]

ABCROWN = Path("/home/anasmefteh/crns/alpha-beta-CROWN/complete_verifier") / "abcrown.py"

BENCHMARK = PROJECT_ROOT / "benchmarks" / "Cifar2020"
BENCHMARK_NAME = "cifar2020"

CONFIG = BENCHMARK / "cifar_conv_small.yaml"

INSTANCES = BENCHMARK / "instances.csv"

SPECS = BENCHMARK / "specs"

NETWORK = "models/eran/cifar_conv_small_pgd.pth"
ONNX_PATH = f"./benchmarks/{NETWORK}"

TIMEOUT = 120

LOG_DIR = PROJECT_ROOT / "data" / "experiments" / "txt"
LOG_DIR.mkdir(parents=True, exist_ok=True)

GEN_RESULTS = LOG_DIR / "gen_results.txt"

RESULTS = PROJECT_ROOT / "data" / "experiments" / "csv" / "results.csv"
RESULTS.parent.mkdir(parents=True, exist_ok=True)


IMAGES = [
    1189,
    15,
    42,
    80,
]

EPSILONS = [1, 2, 4, 8, 16]


def format_time(seconds: float) -> str:
    return f"{seconds:.9f}"


def normalize_result(status: str) -> str:
    normalized = status.strip().lower()

    if normalized.startswith("unsafe") or normalized in {"sat", "ce"}:
        return "SAT"

    if normalized.startswith("safe") or normalized in {"unsat", "verified-safe"}:
        return "UNSAT"

    if normalized == "timeout":
        return "TIMEOUT"

    return normalized.upper()


def build_vnnlib_path(vnnlib_name: str) -> str:
    return f"./benchmarks/Cifar2020/specs/{vnnlib_name}"




def write_instances(rows, timeout: int = TIMEOUT):

    with open(INSTANCES, "w", newline="") as f:

        writer = csv.writer(f)

        for row in rows:
            writer.writerow(row)


def append_csv(result):

    exists = RESULTS.exists()

    with open(RESULTS, "a", newline="") as f:

        writer = csv.writer(f)

        if not exists:

            writer.writerow(
                [
                    "benchmark",
                    "onnx_path",
                    "vnnlib_path",
                    "total_time",
                    "result",
                    "solver_time",
                ]
            )

        writer.writerow(result)



instance_rows = []
case_rows = []

for image in IMAGES:

    for eps in EPSILONS:

        epsilon = eps / 255

        print(f"Image {image} | epsilon={epsilon:.6f}")



        vnnlib = generate_property(
            image=image,
            epsilon=epsilon,
            output_dir=SPECS,
        )



        instance_row = [f"specs/{vnnlib.name}"]
        instance_rows.append(instance_row)
        case_rows.append([image, epsilon, vnnlib.name])

write_instances(instance_rows)

start = time.perf_counter()

with open(GEN_RESULTS, "w") as log:
    subprocess.run(
        [
            sys.executable,
            str(ABCROWN),
            "--config",
            str(CONFIG),
        ],
        stdout=log,
        stderr=subprocess.STDOUT,
        check=False,
    )

runtime = time.perf_counter() - start

parsed_results = parse_results(str(GEN_RESULTS))

for idx, (_image, _epsilon, vnnlib_name) in enumerate(case_rows):
    parsed = parsed_results.get(idx)
    total_time = parsed.total_time if parsed and parsed.total_time else runtime
    result_text = normalize_result(parsed.status if parsed else "unknown")
    append_csv(
        [
            BENCHMARK_NAME,
            ONNX_PATH,
            build_vnnlib_path(vnnlib_name),
            format_time(total_time),
            result_text,
            format_time(total_time),
        ]
    )

print("Sweep finished.")