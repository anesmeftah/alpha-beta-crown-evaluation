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


def compute_patch_bounds(image, epsilon, bbox=None, h_dim=32, w_dim=32):
    """
    Compute lower and upper bounds where perturbation is restricted to a spatial bounding box.
    bbox format: (h_min, h_max, w_min, w_max)
    """
    if bbox is None:
        bbox = (0, 32, 0, 32)
    lower = image.copy()
    upper = image.copy()

    h_min, h_max, w_min, w_max = bbox

    for c in range(3):
        for h in range(32):
            for w in range(32):
                idx = c * (h_dim * w_dim) + h * w_dim + w
                if h_min <= h < h_max and w_min <= w < w_max:
                    lower[idx] = np.clip(image[idx] - epsilon, 0.0, 1.0)
                    upper[idx] = np.clip(image[idx] + epsilon, 0.0, 1.0)
                else:
                    lower[idx] = image[idx]
                    upper[idx] = image[idx]

    return lower, upper


def write_vnnlib(output_file, lower, upper, output_property):
    with open(output_file, "w") as f:
        # Inputs
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


def generate_patch_property(image, epsilon, output_dir, bbox=None, label=None):
    image_path = DATASET_DIR / f"{image:05d}.png"
    image_array = load_image(image_path)
    lower, upper = compute_patch_bounds(image_array, epsilon, bbox=bbox)

    true_label = load_label(image) if label is None else label
    property_text = build_property_text(true_label)

    output_dir = Path(output_dir)
    output_path = (
        output_dir
        / f"{image_path.stem}_label_{true_label}_patch_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}_eps_{epsilon:.5f}.vnnlib"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    write_vnnlib(
        output_path,
        lower,
        upper,
        property_text,
    )

    return output_path
