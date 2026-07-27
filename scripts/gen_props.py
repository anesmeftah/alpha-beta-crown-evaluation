from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from PIL import Image


def load_image(image_path):
    """
    Returns a flattened float32 array in [0,1].
    """

    img = Image.open(image_path).convert("RGB")
    img = np.asarray(img, dtype=np.float32) / 255.0

    return img.flatten()


def compute_bounds(image, epsilon):
    lower = np.clip(image - epsilon, 0.0, 1.0)
    upper = np.clip(image + epsilon, 0.0, 1.0)
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
    constraints = []

    for c in range(10):
        if c != true_label:
            constraints.append(f"(>= Y_{c} Y_{true_label})")

    property_text = "(assert (or\n"
    for c in constraints:
        property_text += f"    {c}\n"
    property_text += "))"

    return property_text


def parse_args():
    parser = ArgumentParser(description="Generate a VNN-LIB property file for an image.")
    parser.add_argument("--image", required=True, help="Path to the input image.")
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

    image_path = Path(args.image)
    image = load_image(image_path)
    lower, upper = compute_bounds(image, args.epsilon)
    property_text = build_property_text(args.label)

    output_dir = Path(args.output_dir)
    output_path = output_dir / f"{image_path.stem}_label_{args.label}_eps_{args.epsilon:.5f}.vnnlib"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    write_vnnlib(
        output_path,
        lower,
        upper,
        property_text,
    )