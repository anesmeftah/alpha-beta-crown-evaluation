from pathlib import Path
import json

from datasets import load_dataset, load_from_disk


DATASET_DIR = Path(__file__).resolve().parent / "hf_cifar10"
OUTPUT_DIR = Path(__file__).resolve().parent / "cifar10_test"


def load_cifar10_test_dataset():
    marker = DATASET_DIR / "dataset_dict.json"

    if marker.exists():
        dataset = load_from_disk(str(DATASET_DIR))
    else:
        dataset = load_dataset("uoft-cs/cifar10")
        dataset.save_to_disk(str(DATASET_DIR))

    return dataset["test"]


def save_test_images(test_dataset):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metadata = []

    for idx, sample in enumerate(test_dataset):
        image = sample["img"]
        label = int(sample["label"])

        filename = f"{idx:05d}.png"
        image_path = OUTPUT_DIR / filename

        image.save(image_path)

        metadata.append(
            {
                "id": idx,
                "label": label,
                "path": filename,
            }
        )

        if (idx + 1) % 1000 == 0 or idx == 0:
            print(f"Saved {idx + 1}/{len(test_dataset)}")

    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)


def main():
    test_dataset = load_cifar10_test_dataset()
    save_test_images(test_dataset)

    print("CIFAR-10 test set created.")
    print(f"Location: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()