from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import numpy as np


def round_half_up(value):
    if pd.isna(value):
        return np.nan
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def solve(inputs_dir: Path) -> dict[str, pd.DataFrame]:
    input_file = inputs_dir / "input_01.csv"
    # Read money as decimal text so a binary float cannot move a half-penny tie.
    df = pd.read_csv(input_file, dtype=str)

    df.columns = [c.strip() for c in df.columns]

    df["Date Sold"] = pd.to_datetime(df["Date Sold"], format="%d/%m/%Y", dayfirst=True, errors="coerce")
    df["Date Returned"] = pd.to_datetime(df["Date Returned"], format="%d/%m/%Y", dayfirst=True, errors="coerce")

    df["Price"] = df["Price"].map(lambda value: Decimal(value) if pd.notna(value) else np.nan)

    mask_swap = (~df["Date Returned"].isna()) & (~df["Date Sold"].isna()) & (df["Date Sold"] > df["Date Returned"])
    sold_orig = df.loc[mask_swap, "Date Sold"].copy()
    returned_orig = df.loc[mask_swap, "Date Returned"].copy()
    df.loc[mask_swap, "Date Sold"] = returned_orig.values
    df.loc[mask_swap, "Date Returned"] = sold_orig.values

    df["Days to Return"] = (df["Date Returned"] - df["Date Sold"]).dt.days

    def refund_amount(days, price):
        if pd.isna(days) or pd.isna(price):
            return np.nan
        if days <= 60:
            return price
        if days <= 100:
            return round_half_up(price / Decimal(2))
        return Decimal('0.00')

    df["Refund"] = [refund_amount(d, p) for d, p in zip(df["Days to Return"], df["Price"])]

    df["Sold Month"] = df["Date Sold"].dt.to_period("M").dt.to_timestamp()
    df["Returned Month"] = df["Date Returned"].dt.to_period("M").dt.to_timestamp()

    year = 2023
    months = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-01", freq="MS")
    out = pd.DataFrame({"Date": months})

    revenue = (
        df.dropna(subset=["Sold Month"]).groupby("Sold Month", as_index=False)["Price"].sum()
        .rename(columns={"Sold Month": "Date", "Price": "Revenue"})
    )
    out = out.merge(revenue, on="Date", how="left")

    returns = df.dropna(subset=["Returned Month"]).copy()

    total_returns = (
        returns.groupby("Returned Month", as_index=False)["Refund"].sum()
        .rename(columns={"Returned Month": "Date", "Refund": "Total Returns Value"})
    )

    num_returns = (
        returns.groupby("Returned Month", as_index=False)["Unique Sales ID"].count()
        .rename(columns={"Returned Month": "Date", "Unique Sales ID": "Number of Returns"})
    )

    avg_days = returns.groupby("Returned Month", as_index=False).agg(
        days_total=("Days to Return", "sum"), days_count=("Days to Return", "count"))
    avg_days["Avg Days to Return"] = [
        round_half_up(Decimal(int(total)) / Decimal(int(count))) if count else np.nan
        for total, count in zip(avg_days["days_total"], avg_days["days_count"])
    ]
    avg_days = avg_days.rename(columns={"Returned Month": "Date"})[
        ["Date", "Avg Days to Return"]]

    out = out.merge(total_returns, on="Date", how="left")
    out = out.merge(num_returns, on="Date", how="left")
    out = out.merge(avg_days, on="Date", how="left")

    no_returns_mask = out["Number of Returns"].isna()
    for col in ["Total Returns Value", "Number of Returns", "Avg Days to Return"]:
        out.loc[no_returns_mask, col] = np.nan

    if "Revenue" in out.columns:
        out["Revenue"] = out["Revenue"].map(round_half_up)
    if "Total Returns Value" in out.columns:
        out["Total Returns Value"] = out["Total Returns Value"].map(round_half_up)
    if "Avg Days to Return" in out.columns:
        out["Avg Days to Return"] = out["Avg Days to Return"].map(round_half_up)

    out["Date"] = out["Date"].dt.strftime("%d/%m/%Y")

    out = out[
        [
            "Date",
            "Revenue",
            "Total Returns Value",
            "Number of Returns",
            "Avg Days to Return",
        ]
    ]

    return {"output_01.csv": out}


if __name__ == "__main__":
    task_dir = Path(__file__).resolve().parent.parent
    inputs_dir = task_dir / "inputs"
    cand_dir = task_dir / "output"
    cand_dir.mkdir(parents=True, exist_ok=True)

    outputs = solve(inputs_dir)
    for filename, df in outputs.items():
        (cand_dir / filename).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cand_dir / filename, index=False, encoding="utf-8")
