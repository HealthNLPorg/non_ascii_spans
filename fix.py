import os
import string
import argparse
from functools import lru_cache
import unicodedata

parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--source_dir",
    type=str,
)
parser.add_argument(
    "--target_dir",
    type=str,
)

@lru_cache
def relevant_unicode_category(category: str) -> bool:
    return category !="So" and not category.startswith("C")

@lru_cache
def relevant_character(char: str) -> bool:
    if char in string.printable:
        return True
    category = unicodedata.category(char)
    return relevant_unicode_category(category)

def process(source_dir: str, target_dir: str) -> None:
    for fn in os.listdir(source_dir):
        with (
            open(os.path.join(source_dir, fn), mode="r") as source_f,
            open(os.path.join(target_dir, fn), mode="w") as target_f,
        ):
            target_f.write("".join(char for char in source_f.read() if relevant_character(char)))


def main() -> None:
    args = parser.parse_args()
    process(args.source_dir, args.target_dir)


if __name__ == "__main__":
    main()
