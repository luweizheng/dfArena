from pathlib import Path
from decimal import Decimal
import pandas as pd


def solve(inputs_dir: Path) -> dict[str, pd.DataFrame]:
    data = pd.read_csv(inputs_dir / 'input_01.csv', dtype=str, keep_default_na=False)
    data['Balance Date'] = pd.to_datetime(data['Balance Date'], format='%d/%m/%Y')
    start = pd.Timestamp('2023-01-31')
    end = pd.Timestamp('2023-02-14')
    selected = pd.Timestamp('2023-02-01')
    output = []
    for account, records in data.groupby('Account Number', sort=True):
        snapshot = records[records['Balance Date'] == start]
        if len(snapshot) != 1 or snapshot.iloc[0]['Transaction Value'] != '':
            raise ValueError(f'Expected one opening balance snapshot for account {account}')
        balance = Decimal(snapshot.iloc[0]['Balance'])
        transactions = {}
        for day, group in records.groupby('Balance Date'):
            transactions[day] = sum((Decimal(v) for v in group['Transaction Value'] if v != ''), Decimal(0))
        for day in pd.date_range(start, end):
            amount = transactions.get(day)
            if day != start and amount is not None:
                balance += amount
            if day == selected:
                output.append({'Account Number': account, 'Transaction Value': amount, 'Balance': balance})
    return {'output_01.csv': pd.DataFrame(output)}


if __name__ == '__main__':
    task_dir = Path(__file__).resolve().parent.parent
    output_dir = task_dir / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in solve(task_dir / 'inputs').items():
        frame.to_csv(output_dir / name, index=False, encoding='utf-8')
