from __future__ import annotations
from pathlib import Path
import pandas as pd


def solve(inputs_dir: Path) -> dict[str, pd.DataFrame]:
    inp = inputs_dir / "input_01.csv"
    df = pd.read_csv(inp)

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

    result = []
    for destination in sorted(df["Destination"].unique()) + ["All"]:
        source = df if destination == "All" else df[df["Destination"] == destination]
        for day in sorted(source["Date"].unique()):
            day = pd.Timestamp(day)
            values = source.loc[source["Date"].between(
                day - pd.Timedelta(days=3), day + pd.Timedelta(days=3)), "Revenue"]
            result.append({"Destination": destination, "Date": day,
                           "Rolling Week Avg": values.mean(),
                           "Rolling Week Total": values.sum()})
    out = pd.DataFrame(result)

    out["Rolling Week Avg"] = out["Rolling Week Avg"].round(9)
    out["Rolling Week Total"] = out["Rolling Week Total"].round(0).astype(int)

    out["Date"] = out["Date"].dt.strftime("%d/%m/%Y")

    out = out[["Destination", "Date", "Rolling Week Avg", "Rolling Week Total"]]

    return {"output_01.csv": out}


if __name__ == "__main__":
    import sys

    task_dir = Path(__file__).resolve().parent.parent
    inputs_dir = task_dir / "inputs"
    cand_dir = task_dir / "output"
    cand_dir.mkdir(parents=True, exist_ok=True)

    result = solve(inputs_dir)
    for fname, df in result.items():
        (cand_dir / fname).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cand_dir / fname, index=False, encoding="utf-8")
