import argparse
from collections.abc import Iterable
import operator
from itertools import groupby
from dataclasses import dataclass

parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--log_file",
    type=str,
)

parser.add_argument(
    "--source_dir",
    type=str,
)


def find_bad_spans(problem_string: str) -> Iterable[tuple[int, int]]:
    current = 0
    for non_ascii, run in groupby(map(str.isascii, problem_string), key=operator.not_):
        run_length = sum(1 for _ in run)
        end = current + run_length
        if non_ascii:
            yield current, end
        current = run_length


def visualize_problem_spans(
    problem_string: str, problem_spans: Iterable[tuple[int, int]]
) -> None:
    def visualize_span(begin: int, end: int) -> str:
        ellipsis = "..."
        context_begin = max(0, begin - 15)
        context_end = min(len(problem_string), end + 15)
        prefix = f"{ellipsis if context_begin > 0 else ''}{problem_string[context_begin:begin]}<NON_ASCII>"

        postfix = f"</NON_ASCII>{problem_string[context_begin:begin]}{ellipsis if context_end < len(problem_string) else ''}"
        return f"{prefix}{problem_string[begin:end]}{postfix}"

    for problem_span in find_bad_spans(problem_string):
        begin, end = problem_span
        print(visualize_span(begin, end))


@dataclass
class ProblemFile:
    filename: str
    bad_paragraph_indices: list[int]
    bad_paragraphs: list[str]


def parse_problem_file_from_line(line: str) -> ProblemFile:
    def get_filename(_line: str) -> str:
        return ""

    def get_bad_paragraph_inds(_line: str) -> list[int]:
        return []

    return ProblemFile(
        filename=get_filename(line),
        bad_paragraph_indices=get_bad_paragraph_inds(line),
        bad_paragraphs=[],
    )


def parse_log_for_problem_files(log_file: str) -> set[ProblemFile]:
    def is_relevant(line: str) -> bool:
        return False

    problem_files = set()
    with open(log_file, mode="r") as f:
        for line in f:
            if is_relevant(line):
                problem_files.add(parse_problem_file_from_line(line))
    return problem_files


def process(log_file: str, source_dir: str) -> None:
    pass


def main() -> None:
    args = parser.parse_args()
    process(args.log_file, args.source_dir)


if __name__ == "__main__":
    main()
