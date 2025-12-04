import os
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--source_dir",
    type=str,
)
parser.add_argument(
    "--target_dir",
    type=str,
)


def process(source_dir: str, target_dir: str) -> None:
    for fn in os.listdir(source_dir):
        with (
            open(os.path.join(source_dir, fn), mode="r") as source_f,
            open(os.path.join(target_dir, fn), mode="w") as target_f,
        ):
            target_f.write("".join(filter(str.isprintable, source_f.read())))


def main() -> None:
    args = parser.parse_args()
    process(args.source_dir, args.target_dir)


if __name__ == "__main__":
    main()
