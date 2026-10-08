from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "credit_data.csv"


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Avoid division by zero
    duration = df["duration_months"].replace(0, 1)
    age = df["age"].replace(0, 1)

    df["monthly_payment"] = df["credit_amount"] / duration
    df["amount_per_age"] = df["credit_amount"] / age
    df["payment_to_installment"] = df["monthly_payment"] * df["installment_rate"]
    return df


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    df = add_features(df)
    X = df.drop(columns=["target"])
    y = df["target"]
    return X, y


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    num_cols = X.select_dtypes(include="number").columns.tolist()
    cat_cols = X.select_dtypes(exclude="number").columns.tolist()
    return ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ])


def split_data(X, y):
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)