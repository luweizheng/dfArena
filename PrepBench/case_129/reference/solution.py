
import pandas as pd
from pathlib import Path

def solve(inputs_dir: Path) -> dict[str, pd.DataFrame]:
    df = pd.read_csv(inputs_dir / "input_01.csv")
    df["_input_order"] = range(len(df))

    def normalize_label(series: pd.Series) -> pd.Series:
        return (
            series.where(series.notna(), "")
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.upper()
        )

    df["From_clean"] = normalize_label(df["From"])
    df["To_clean"] = normalize_label(df["To"])

    missing_tokens = {"", "NA", "N/A", "-", "NULL"}
    from_missing = df["From_clean"].isin(missing_tokens)
    to_missing = df["To_clean"].isin(missing_tokens)
    from_valid = df["From_clean"].isin(["B", "G"]) | df["From_clean"].str.fullmatch(r"-?\d+")
    to_valid = df["To_clean"].isin(["B", "G"]) | df["To_clean"].str.fullmatch(r"-?\d+")

    df = df.loc[~from_missing & ~to_missing & from_valid & to_valid].copy()

    df = df.sort_values(["Hour", "Minute", "_input_order"]).reset_index(drop=True)
    df["TripID"] = df.index + 1

    def labels_to_numeric(series: pd.Series) -> pd.Series:
        return pd.to_numeric(series.replace({"B": -1, "G": 0}), errors="raise").astype("int64")

    df["From_numeric"] = labels_to_numeric(df["From_clean"])
    df["To_numeric"] = labels_to_numeric(df["To_clean"])

    counts = df["From_numeric"].value_counts()
    default_numeric = counts[counts == counts.max()].index.min()

    def numeric_to_label(value: int) -> str:
        if value == -1:
            return "B"
        if value == 0:
            return "G"
        return str(int(value))

    default_position_str = numeric_to_label(int(default_numeric))

    df["Travel_from_default"] = (df["From_numeric"] - default_numeric).abs()
    avg_travel_from_default = df["Travel_from_default"].mean()

    df["Previous_To"] = df["To_numeric"].shift(1)
    df["Travel_between_trips"] = (df["From_numeric"] - df["Previous_To"]).abs()
    avg_travel_between_trips = df["Travel_between_trips"].iloc[1:].mean()

    avg_travel_from_default = round(float(avg_travel_from_default), 2)
    avg_travel_between_trips = round(float(avg_travel_between_trips), 2)
    difference = round(avg_travel_from_default - avg_travel_between_trips, 2)

    output_df = pd.DataFrame([{
        'Default Position': default_position_str,
        'Avg travel from default position': avg_travel_from_default,
        'Avg Travel between trips currently': avg_travel_between_trips,
        'Difference': difference
    }])

    return {"output_01.csv": output_df}

if __name__ == "__main__":
    task_dir = Path(__file__).resolve().parent.parent
    inputs_dir = task_dir / "inputs"

    cand_dir = task_dir / "output"
    if not cand_dir.exists():
        cand_dir.mkdir()

    outputs = solve(inputs_dir)

    for filename, df in outputs.items():
        df.to_csv(cand_dir / filename, index=False, encoding='utf-8')
