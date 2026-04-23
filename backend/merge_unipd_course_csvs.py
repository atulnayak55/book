import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT_DIR = Path("/home/atul-nayak/book")
DEFAULT_OLD_CSV = ROOT_DIR / "unipd_courses_2025.csv"
DEFAULT_NEW_CSV = ROOT_DIR / "unipd_courses_2025_full.csv"
DEFAULT_OUTPUT_CSV = ROOT_DIR / "unipd_courses_2025_merged.csv"

PROGRAM_PATTERN = re.compile(r"^\[([^\]]+)\]\s*(.*)$")

SCHOOL_BY_PREFIX = {
    "AV": "School of Agricultural Sciences and Veterinary Medicine",
    "EP": "School of Economics and Political Science",
    "GI": "Law School",
    "IA": "School of Human and Social Sciences and Cultural Heritage",
    "IN": "School of Engineering",
    "LE": "School of Human and Social Sciences and Cultural Heritage",
    "ME": "School of Medicine",
    "PS": "School of Psychology",
    "SC": "School of Science",
    "SU": "School of Human and Social Sciences and Cultural Heritage",
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_program(program: str) -> tuple[str, str]:
    match = PROGRAM_PATTERN.match(normalize_text(program))
    if not match:
        return "NO_CODE", normalize_text(program)
    return match.group(1).strip().upper(), normalize_text(match.group(2))


def is_track_variant(name: str) -> bool:
    return " - " in name


def choose_canonical_program_name(code: str, old_names: set[str], new_names: set[str]) -> str:
    new_base_names = sorted(name for name in new_names if not is_track_variant(name))
    if new_base_names:
        return new_base_names[0]

    old_base_names = sorted(name for name in old_names if not is_track_variant(name))
    if old_base_names:
        return old_base_names[0]

    if new_names:
        return sorted(new_names, key=lambda value: (value.count(" - "), len(value), value))[0]

    if old_names:
        return sorted(old_names, key=lambda value: (value.count(" - "), len(value), value))[0]

    return code


def choose_department(code: str, departments: set[str]) -> str:
    prefix = code[:2]
    if prefix in SCHOOL_BY_PREFIX:
        return SCHOOL_BY_PREFIX[prefix]
    if departments:
        return sorted(departments)[0]
    return "University of Padua"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as file:
        return list(csv.DictReader(file))


def merge_csvs(old_csv: Path, new_csv: Path, output_csv: Path) -> int:
    merged: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "old_names": set(),
            "new_names": set(),
            "departments": set(),
            "subjects": set(),
        }
    )

    for source_name, path in (("old", old_csv), ("new", new_csv)):
        for row in load_rows(path):
            code, program_name = parse_program(row["program"])
            entry = merged[code]
            if source_name == "old":
                entry["old_names"].add(program_name)
            else:
                entry["new_names"].add(program_name)
            entry["departments"].add(normalize_text(row["department"]))
            entry["subjects"].add((normalize_text(row["year"]), normalize_text(row["subjects"])))

    merged_rows: list[tuple[str, str, str, str]] = []
    for code, entry in merged.items():
        program_name = choose_canonical_program_name(
            code,
            entry["old_names"],
            entry["new_names"],
        )
        department = choose_department(code, entry["departments"])
        program = f"[{code}] {program_name}"
        for year, subject in sorted(entry["subjects"], key=lambda item: (item[0], item[1].lower())):
            merged_rows.append((department, program, year, subject))

    merged_rows.sort(key=lambda item: (item[0].lower(), item[1].lower(), item[2], item[3].lower()))

    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["department", "program", "year", "subjects"])
        writer.writerows(merged_rows)

    return len(merged_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge old and scraped UniPd course CSVs.")
    parser.add_argument("--old", default=str(DEFAULT_OLD_CSV))
    parser.add_argument("--new", default=str(DEFAULT_NEW_CSV))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_CSV))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    row_count = merge_csvs(Path(args.old), Path(args.new), Path(args.output))
    print(f"Wrote {row_count} merged rows to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
