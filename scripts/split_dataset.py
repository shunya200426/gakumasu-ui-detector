import argparse
import random
import shutil
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def reset_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", default="dataset")
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)

    img_all = dataset_dir / "images" / "all"
    label_all = dataset_dir / "labels" / "all"

    img_train = dataset_dir / "images" / "train"
    img_val = dataset_dir / "images" / "val"
    label_train = dataset_dir / "labels" / "train"
    label_val = dataset_dir / "labels" / "val"

    images = sorted(
        p for p in img_all.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )

    valid_pairs = []
    missing_labels = []

    for img_path in images:
        label_path = label_all / f"{img_path.stem}.txt"
        if label_path.exists():
            valid_pairs.append((img_path, label_path))
        else:
            missing_labels.append(img_path.name)

    if not valid_pairs:
        raise RuntimeError("画像とラベルのペアが見つかりませんでした。")

    random.seed(args.seed)
    random.shuffle(valid_pairs)

    train_count = int(len(valid_pairs) * args.train_ratio)
    train_pairs = valid_pairs[:train_count]
    val_pairs = valid_pairs[train_count:]

    reset_dir(img_train)
    reset_dir(img_val)
    reset_dir(label_train)
    reset_dir(label_val)

    for img_path, label_path in train_pairs:
        shutil.copy2(img_path, img_train / img_path.name)
        shutil.copy2(label_path, label_train / label_path.name)

    for img_path, label_path in val_pairs:
        shutil.copy2(img_path, img_val / img_path.name)
        shutil.copy2(label_path, label_val / label_path.name)

    print("=== Split complete ===")
    print(f"Total pairs : {len(valid_pairs)}")
    print(f"Train       : {len(train_pairs)}")
    print(f"Val         : {len(val_pairs)}")

    if missing_labels:
        print()
        print("Warning: labels not found for these images:")
        for name in missing_labels[:20]:
            print(f"  - {name}")
        if len(missing_labels) > 20:
            print(f"  ... and {len(missing_labels) - 20} more")


if __name__ == "__main__":
    main()