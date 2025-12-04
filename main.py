import argparse
import os
import re
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
) -> str:
    def visualize_span(begin: int, end: int) -> str:
        ellipsis = "..."
        context_begin = max(0, begin - 15)
        context_end = min(len(problem_string), end + 15)
        prefix = f"{ellipsis if context_begin > 0 else ''}{problem_string[context_begin:begin]}<NON_ASCII>"

        postfix = f"</NON_ASCII>{problem_string[context_begin:begin]}{ellipsis if context_end < len(problem_string) else ''}"
        return f"{prefix}{problem_string[begin:end]}{postfix}"

    return "\n".join(
        visualize_span(*problem_span) for problem_span in find_bad_spans(problem_string)
    )


@dataclass
class ProblemFile:
    filename: str
    bad_paragraph_indices: list[int]
    bad_paragraphs: list[str]

    @staticmethod
    def __visualize_paragraph(paragraph: str, index: int) -> str:
        problem_spans = find_bad_spans(paragraph)
        return f"\nPARAGRAPH {index} TEXT:\n{paragraph}\nPARAGRAPH {index} PROBLEMS:\n{visualize_problem_spans(paragraph, problem_spans)}\n"

    def visualize(self) -> str:
        def __local_viz(paragraph: str, index: int) -> str:
            return f"\nFile {self.filename} - {ProblemFile.__visualize_paragraph(paragraph, index)}"

        return "".join(
            __local_viz(paragraph, index)
            for paragraph, index in zip(self.bad_paragraphs, self.bad_paragraph_indices)
        )


def parse_problem_file_from_line(line: str) -> tuple[str, ProblemFile]:
    filename = line.strip().split()[-1]
    core = line.split("-")[-1].strip()
    raw_list_str = core.split("of")[0].strip().removeprefix("Failed paragraphs")
    bad_paragraph_indices = [int(elem) for elem in raw_list_str.strip().split(",")]
    return filename, ProblemFile(
        filename=filename,
        bad_paragraph_indices=bad_paragraph_indices,
        bad_paragraphs=[],
    )


def parse_log_for_fn_to_problem_file(log_file: str) -> dict[str, ProblemFile]:
    def is_relevant(line: str) -> bool:
        return "Failed paragraphs" in line

    fn_to_problem_file = {}
    with open(log_file, mode="r") as f:
        for line in f:
            if is_relevant(line):
                fn, problem_file = parse_problem_file_from_line(line)
                fn_to_problem_file[fn] = problem_file
    return fn_to_problem_file


def get_offending_paragraphs(
    source_path: str, offending_indices: list[int]
) -> list[str]:
    print(offending_indices)
    with open(source_path, mode="r") as f:
        raw = f.read()
        paragraphs = re.split(r"(\n[\t\r ]*){2,}", raw)
    print(paragraphs)
    # print(raw)
    return [paragraphs[ind] for ind in offending_indices]


def populate_problem_files_with_offending_paragraphs(
    fn_to_problem_file: dict[str, ProblemFile], source_dir: str
) -> Iterable[ProblemFile]:
    for fn in os.listdir(source_dir):
        if fn in fn_to_problem_file:
            problem_file = fn_to_problem_file[fn]
            problem_file.bad_paragraphs = get_offending_paragraphs(
                os.path.join(source_dir, fn), problem_file.bad_paragraph_indices
            )
            yield problem_file


def process(log_file: str, source_dir: str) -> None:
    eq_buffer = "=" * 100
    fn_to_problem_file = parse_log_for_fn_to_problem_file(log_file)
    for problem_file in populate_problem_files_with_offending_paragraphs(
        fn_to_problem_file, source_dir
    ):
        print(eq_buffer)
        print(problem_file.visualize())
        print(eq_buffer)


def main() -> None:
    args = parser.parse_args()
    process(args.log_file, args.source_dir)


if __name__ == "__main__":
    main()
