from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

cols = [
    "checking_status", "duration_months", "credit_history", "purpose",
    "credit_amount", "savings", "employment_since", "installment_rate",
    "personal_status", "other_debtors", "residence_since", "property",
    "age", "other_installments", "housing", "existing_credits",
    "job", "dependents", "telephone", "foreign_worker", "target",
]

raw_data_path = PROJECT_ROOT / "data" / "german.data"
output_path = PROJECT_ROOT / "data" / "credit_data.csv"

df = pd.read_csv(raw_data_path, sep=r"\s+", header=None, names=cols)
df["target"] = df["target"].map({1: 1, 2: 0})  # 1 = good credit, 0 = bad credit
df.to_csv(output_path, index=False)

print(f"Data prepared successfully: {df.shape}")
print(df["target"].value_counts())