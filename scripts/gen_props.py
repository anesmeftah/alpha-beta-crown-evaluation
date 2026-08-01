from argparse import ArgumentParser
import json
from pathlib import Path

import numpy as np
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "data" / "dataset" / "cifar10_test"
METADATA_PATH = DATASET_DIR / "metadata.json"


def load_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = np.asarray(img, dtype=np.float32) / 255.0

    # HWC -> CHW
    img = np.transpose(img, (2, 0, 1))

    return img.flatten()

def compute_bounds(image, epsilon):
    lower = np.clip(image - epsilon, 0.0, 1.0)
    upper = np.clip(image + epsilon, 0.0, 1.0)
    return lower, upper


def write_vnnlib(output_file, lower, upper, output_property):
    with open(output_file, "w") as f:

        # Inputscompute_bounds
        for i in range(len(lower)):
            f.write(f"(declare-const X_{i} Real)\n")

        f.write("\n")

        # Outputs (10 classes for CIFAR)
        for i in range(10):
            f.write(f"(declare-const Y_{i} Real)\n")

        f.write("\n")

        # Input domain
        for i in range(len(lower)):
            f.write(f"(assert (>= X_{i} {lower[i]:.8f}))\n")
            f.write(f"(assert (<= X_{i} {upper[i]:.8f}))\n")

        f.write("\n")

        # Output property
        f.write(output_property)
        f.write("\n")



def build_property_text(true_label):
    clauses = []

    for c in range(10):
        if c != true_label:
            clauses.append(f"(and (>= Y_{c} Y_{true_label}))")

    property_text = "(assert (or\n"
    for clause in clauses:
        property_text += f"    {clause}\n"
    property_text += "))"

    return property_text


def load_label(image_id):
    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)

    for entry in metadata:
        if entry["id"] == image_id:
            return entry["label"]

    raise ValueError(f"No label found for image id {image_id}")


def generate_property(image, epsilon, output_dir, label=None):
    image_path = DATASET_DIR / f"{image:05d}.png"
    image_array = load_image(image_path)
    lower, upper = compute_bounds(image_array, epsilon)

    true_label = load_label(image) if label is None else label
    property_text = build_property_text(true_label)

    output_dir = Path(output_dir)
    output_path = output_dir / f"{image_path.stem}_label_{true_label}_eps_{epsilon:.5f}.vnnlib"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    write_vnnlib(
        output_path,
        lower,
        upper,
        property_text,
    )

    return output_path


def parse_args():
    parser = ArgumentParser(description="Generate a VNN-LIB property file for an image.")
    parser.add_argument("--image", type=int, required=True, help="Image ID in cifar10_test, e.g. 1 for 00001.png.")
    parser.add_argument("--label", type=int, required=True, help="True label for the image.")
    parser.add_argument("--epsilon", type=float, required=True, help="L-infinity perturbation radius.")
    parser.add_argument(
        "--output-dir",
        default=Path(__file__).resolve().parents[1] / "data" / "VNNLIB",
        help="Directory where the .vnnlib file will be written.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    generate_property(
        image=args.image,
        epsilon=args.epsilon,
        output_dir=args.output_dir,
        label=args.label,
    )