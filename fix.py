import os
import string
import argparse
from functools import lru_cache
import unicodedata
from collections import deque
from collections.abc import Iterable
import pathlib
import polars as pl
from more_itertools import unzip
from operator import itemgetter
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)


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


def get_character_map_and_string(
    raw_string: str,
) -> tuple[str, list[tuple[int, int]]]:
    current = 0
    relevant_characters = deque()
    relevant_character_to_original = deque()
    for idx, char in enumerate(raw_string):
        if relevant_character(char):
            relevant_character_to_original.append((idx, current))
            relevant_characters.append(char)
            current += 1
    return "".join(relevant_characters), list(relevant_character_to_original)


def log_problem_indices(fn: int, offset_iter: Iterable[tuple[int, int]]) -> int:
    problem_offsets = [offsets for offsets in offset_iter if offsets[0] != offsets[1]]
    match len(problem_offsets):
        case 0:
            return 0
        case 1 | 2 | 3 | 4 | 5:
            logger.info(
                "%d - has %d problematic offsets - %s",
                fn,
                len(problem_offsets),
                ",".join(map(str, problem_offsets)),
            )
        case _:
            logger.info("%d - has %d problematic offsets", fn, len(problem_offsets))
    return 1


def offsets_to_str(offset_iter: Iterable[tuple[int, int]]) -> str:
    def offset_to_str(offsets: tuple[int, int]) -> str:
        begin, end = offsets
        return f"{begin}_{end}"

    return ",".join(map(offset_to_str, offset_iter))


def process(source_dir: str, target_dir: str) -> None:
    fns_offset_map_strs = deque()
    notes_dir = os.path.join(target_dir, "notes")
    make_directory(notes_dir)
    total_files_with_printable_character_issues = 0
    files = os.listdir(source_dir)
    for fn in files:
        with (
            open(os.path.join(source_dir, fn), mode="r") as source_f,
            open(os.path.join(notes_dir, fn), mode="w", encoding="utf-8") as target_f,
        ):
            fixed_contents, offset_map = get_character_map_and_string(source_f.read())
            target_f.write(fixed_contents)
        report_id = int(fn.split(".")[0])
        fns_offset_map_strs.append((report_id, offsets_to_str(offset_map)))
        total_files_with_printable_character_issues += log_problem_indices(
            report_id, offset_map
        )
    logger.info(
        "%d of %d files had character problems",
        total_files_with_printable_character_issues,
        len(files),
    )
    fn_iter, offsets_iter = unzip(sorted(fns_offset_map_strs, key=itemgetter(0)))
    pl.DataFrame({"fn": fn_iter, "offset": offsets_iter}).write_csv(
        os.path.join(target_dir, "offset_map.tsv"), separator="\t"
    )


def main() -> None:
    args = parser.parse_args()
    process(args.source_dir, args.target_dir)


if __name__ == "__main__":
    main()
