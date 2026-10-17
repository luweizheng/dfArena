from __future__ import annotations

from pathlib import Path

import pandas as pd


def solve(inputs_dir: Path) -> dict[str, pd.DataFrame]:
    input_path = inputs_dir / "input_01.csv"
    df = pd.read_csv(input_path)

    df["Mins Played"] = (df["ms_played"] / (1000 * 60)).round(2)
    # Preserve per-listen rounding, then sum exact hundredths to keep ties equal.
    df["Minute Hundredths"] = (df["Mins Played"] * 100).round().astype("int64")
    df["Year"] = pd.to_datetime(df["ts"]).dt.year

    totals = (
        df.groupby("Artist Name", as_index=False)["Minute Hundredths"]
        .sum()
        .rename(columns={"Minute Hundredths": "Total Mins"})
    )
    totals["Overall Rank"] = totals["Total Mins"].rank(
        method="min", ascending=False
    ).astype(int)
    totals = totals.drop(columns=["Total Mins"])

    year_group = (
        df.groupby(["Artist Name", "Year"], as_index=False)["Minute Hundredths"]
        .sum()
        .rename(columns={"Minute Hundredths": "Yearly Mins"})
    )

    year_group["Ranking"] = year_group.groupby("Year")["Yearly Mins"].rank(
        method="min", ascending=False
    ).astype(int)
    year_group = year_group.drop(columns=["Yearly Mins"])

    year_columns = list(range(2015, 2023))

    pivot = (
        year_group.pivot(index="Artist Name", columns="Year", values="Ranking")
        .reindex(columns=year_columns)
        .reset_index()
    )
    pivot.columns.name = None

    output = totals.merge(pivot, on="Artist Name", how="left")
    output = output.sort_values(
        "Overall Rank").loc[output["Overall Rank"] <= 100]
    output = output.reset_index(drop=True)

    rename_map = {year: str(year) for year in year_columns}
    output = output.rename(columns=rename_map)

    for col in rename_map.values():
        output[col] = output[col].astype("Int64")

    ordered_columns = ["Overall Rank", "Artist Name", *rename_map.values()]
    output = output[ordered_columns]

    return {"output_01.csv": output}


if __name__ == "__main__":
    task_dir = Path(__file__).resolve().parent.parent
    inputs_dir = task_dir / "inputs"
    cand_dir = task_dir / "output"
    cand_dir.mkdir(exist_ok=True)

    outputs = solve(inputs_dir)
    for filename, df in outputs.items():
        df.to_csv(cand_dir / filename, index=False, encoding="utf-8")
