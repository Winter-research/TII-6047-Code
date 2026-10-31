import argparse
import re
import shutil
from pathlib import Path

import yaml
from PIL import Image


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
SECTION_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SECTION_DIR.parent
DEFAULT_CONFIG = SECTION_DIR / "configs" / "image_preprocessing.yaml"


def load_config(config_path):
    """Load preprocessing parameters from a YAML file."""
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    dataset_dir = Path(config["dataset_dir"])
    if not dataset_dir.is_absolute():
        dataset_dir = PROJECT_DIR / dataset_dir

    results_dir = Path(config["results_dir"])
    if not results_dir.is_absolute():
        results_dir = PROJECT_DIR / results_dir

    save_next_to_source = bool(config.get("save_next_to_source", True))
    resolutions = tuple(int(value) for value in config["resolutions"])
    return dataset_dir, results_dir, save_next_to_source, resolutions


def resize_images(dataset_dir, results_dir, resolutions, save_next_to_source=True):
    """Create resized copies in the results directory and beside source images."""
    dataset_dir = Path(dataset_dir)
    results_dir = Path(results_dir)
    source_paths = [
        path
        for path in dataset_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and not re.search(r"_p\d+$", path.stem)
    ]

    for source_path in source_paths:
        with Image.open(source_path) as image:
            for resolution in resolutions:
                target_name = f"{source_path.stem}_p{resolution}{source_path.suffix.lower()}"
                relative_parent = source_path.parent.relative_to(dataset_dir)
                target_paths = [results_dir / relative_parent / target_name]
                if save_next_to_source:
                    target_paths.append(source_path.with_name(target_name))

                for target_path in target_paths:
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                scale = resolution / max(image.size)

                if scale >= 1:
                    for target_path in target_paths:
                        shutil.copy2(source_path, target_path)
                    continue

                new_size = tuple(round(side * scale) for side in image.size)
                output = image.resize(new_size, Image.Resampling.LANCZOS)

                if source_path.suffix.lower() in {".jpg", ".jpeg"} and output.mode not in {"RGB", "L"}:
                    output = output.convert("RGB")

                for target_path in target_paths:
                    output.save(target_path)

    destination_count = 2 if save_next_to_source else 1
    generated_count = len(source_paths) * len(resolutions) * destination_count
    print(f"Processed {len(source_paths)} source images.")
    print(f"Generated {generated_count} image files at {list(resolutions)} pixels.")
    print(f"Results directory: {results_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate configured image resolutions in the dataset folders."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the preprocessing YAML file.",
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        help="Optional dataset directory override.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        help="Optional results directory override.",
    )
    parser.add_argument(
        "--resolutions",
        nargs="+",
        type=int,
        help="Optional target-resolution override.",
    )
    args = parser.parse_args()

    dataset_dir, results_dir, save_next_to_source, resolutions = load_config(args.config)

    if args.dataset_dir is not None:
        dataset_dir = args.dataset_dir
    if args.results_dir is not None:
        results_dir = args.results_dir
    if args.resolutions is not None:
        resolutions = tuple(args.resolutions)

    if not dataset_dir.is_dir():
        parser.error(f"Dataset directory does not exist: {dataset_dir}")
    if any(resolution <= 0 for resolution in resolutions):
        parser.error("All resolutions must be positive integers.")

    resize_images(dataset_dir, results_dir, resolutions, save_next_to_source)


if __name__ == "__main__":
    main()
