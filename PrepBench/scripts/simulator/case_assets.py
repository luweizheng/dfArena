from pathlib import Path


def resolve_reference_solution_path(case_dir: Path, root: Path | None = None) -> Path | None:
    case = case_dir.resolve() if root is None else root.resolve() / case_dir.name
    path = case / "reference" / "solution.py"
    return path if path.is_file() else None


def read_reference_solution_text(case_dir: Path, root: Path | None = None) -> str:
    path = resolve_reference_solution_path(case_dir, root)
    return path.read_text(encoding="utf-8") if path else ""
