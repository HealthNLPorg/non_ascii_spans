import os
import string
import argparse
from functools import lru_cache
import unicodedata
from collections import deque
from collections.abc import Iterable
import pathlib
from polars import pl


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
    return category != "So" and not category.startswith("C")


@lru_cache
def relevant_character(char: str) -> bool:
    if char in string.printable:
        return True
    category = unicodedata.category(char)
    return relevant_unicode_category(category)


def make_directory(dirname: str) -> None:
    pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)


def process(source_dir: str, target_dir: str) -> None:
    fns = deque()
    offset_map_strs = deque()
    for fn in os.listdir(source_dir):
        with (
            open(os.path.join(source_dir, fn), mode="r") as source_f,
            open(os.path.join(target_dir, fn), mode="w", encoding="utf-8") as target_f,
        ):
            fixed_contents, offset_map = get_character_map_and_string(source_f.read())
            target_f.write(fixed_contents)
        fns.append(fn)
        offset_map_strs.append(offsets_to_str(offset_map))


def get_character_map_and_string(
    raw_string: str,
) -> tuple[str, Iterable[tuple[int, int]]]:
    current = 0
    relevant_characters = deque()
    relevant_character_to_original = deque()
    for idx, char in enumerate(raw_string):
        if relevant_character(char):
            relevant_character_to_original.append((idx, current))
            relevant_characters.append(char)
            current += 1
    return "".join(relevant_characters), relevant_character_to_original


def offsets_to_str(offset_iter: Iterable[tuple[int, int]]) -> str:
    def offset_to_str(offsets: tuple[int, int]) -> str:
        begin, end = offsets
        return f"{begin}_{end}"

    return ",".join(map(offset_to_str, offset_iter))


def main() -> None:
    args = parser.parse_args()
    process(args.source_dir, args.target_dir)


if __name__ == "__main__":
    main()
