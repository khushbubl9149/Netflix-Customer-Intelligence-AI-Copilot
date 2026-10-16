from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_ROOT / "data" / "processed"


for file_path in sorted(DATA_FOLDER.glob("*.csv")):

    print("\n" + "=" * 70)
    print(file_path.name)
    print("=" * 70)

    df = pd.read_csv(file_path)

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumn names:")
    print(list(df.columns))

    print("\nMissing values:")
    print(df.isna().sum())