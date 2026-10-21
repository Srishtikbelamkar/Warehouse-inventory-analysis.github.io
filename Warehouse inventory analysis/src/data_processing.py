import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "warehouse_inventory.csv"


def load_data(file_path=DATA_FILE):
    """Load warehouse inventory data from a CSV file."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}\n"
            "Place warehouse_inventory.csv inside the data folder."
        )

    df = pd.read_csv(file_path)
    return clean_data(df)


def clean_data(df):
    """Clean and prepare the inventory dataset."""
    df = df.copy()

    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_columns = [
        "Opening_Stock",
        "Received_Qty",
        "Issued_Qty",
        "Closing_Stock",
        "Reorder_Level",
        "Safety_Stock",
        "Unit_Cost_INR",
        "Inventory_Value_INR",
        "Damaged_Qty",
        "Expired_Qty",
        "Lead_Time_Days",
        "Demand_Qty",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            ).fillna(0)

    if {"Closing_Stock", "Unit_Cost_INR"}.issubset(df.columns):
        df["Inventory_Value_INR"] = (
            df["Closing_Stock"] * df["Unit_Cost_INR"]
        )

    if {"Closing_Stock", "Reorder_Level"}.issubset(df.columns):
        df["Stock_Status"] = df.apply(
            lambda row: (
                "Out of Stock"
                if row["Closing_Stock"] <= 0
                else "Reorder Required"
                if row["Closing_Stock"] <= row["Reorder_Level"]
                else "Available"
            ),
            axis=1,
        )

    if "Date" in df.columns:
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month
        df["Month_Year"] = df["Date"].dt.to_period("M").astype(str)

    df = df.drop_duplicates()

    return df


if __name__ == "__main__":
    data = load_data()
    print("Data loaded successfully!")
    print("Rows and columns:", data.shape)
    print(data.head())
    print("\nMissing values:\n", data.isnull().sum())