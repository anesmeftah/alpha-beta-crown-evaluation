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
BENCHMARK_NAME = "cifar2020_convbig"

CONFIG = BENCHMARK / "cifar_conv_big.yaml"
INSTANCES = BENCHMARK / "instances.csv"
SPECS = BENCHMARK / "specs"

NETWORK = "models/eran/cifar_conv_big_pgd.pth"
ONNX_PATH = f"./benchmarks/{NETWORK}"

TIMEOUT = 120

LOG_DIR = PROJECT_ROOT / "data" / "experiments" / "txt"
LOG_DIR.mkdir(parents=True, exist_ok=True)

GEN_RESULTS = LOG_DIR / "gen_results_convbig.txt"
ABCROWN_RESULTS = LOG_DIR / "abcrown_results_convbig.pkl"

RESULTS = PROJECT_ROOT / "data" / "experiments" / "csv" / "results_convbig.csv"
RESULTS.parent.mkdir(parents=True, exist_ok=True)

IMAGES = [
    1189,
    0,
    400,
    800,
    1200,
    1600,
    2000,
    2400,
    2800,
    3200,
    3600,
    4000,
    4400,
    4800,
    5200,
    5600,
    6000,
    6400,
    6800,
    7200,
    7600,
    8000,
    8400,
    8800,
    9200,
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


def save_csv(rows: list[list[str]]):
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS, "w", newline="") as f:
        writer = csv.writer(f)
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
        for row in rows:
            writer.writerow(row)


def main():
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

    print(f"Running ConvBig sweep and saving raw output to {GEN_RESULTS}...")
    with open(GEN_RESULTS, "w") as log:
        subprocess.run(
            [
                sys.executable,
                str(ABCROWN),
                "--config",
                str(CONFIG),
                "--results_file",
                str(ABCROWN_RESULTS),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=ABCROWN.parent,
            check=True,
        )

    runtime = time.perf_counter() - start

    print(f"Parsing ConvBig raw output from {GEN_RESULTS}...")
    parsed_results = parse_results(str(GEN_RESULTS))

    csv_rows = []
    for idx, (_image, _epsilon, vnnlib_name) in enumerate(case_rows):
        parsed = parsed_results.get(idx)
        total_time = parsed.total_time if parsed and parsed.total_time else runtime
        result_text = normalize_result(parsed.status if parsed else "unknown")
        csv_rows.append(
            [
                BENCHMARK_NAME,
                ONNX_PATH,
                build_vnnlib_path(vnnlib_name),
                format_time(total_time),
                result_text,
                format_time(total_time),
            ]
        )

    save_csv(csv_rows)
    print(f"ConvBig sweep finished. Results saved to {RESULTS}.")


if __name__ == "__main__":
    main()
