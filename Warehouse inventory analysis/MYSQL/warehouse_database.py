import pandas as pd
import mysql.connector
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "warehouse_inventory.csv"


# Update these settings to match your MySQL account
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345",
    "database": "warehouse_inventory_db",
}


COLUMNS = [
    "Inventory_ID",
    "Date",
    "Product_ID",
    "Product_Name",
    "Category",
    "Warehouse",
    "Supplier",
    "Region",
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
    "Stock_Status",
    "Salesperson",
    "Movement_Type",
]


def get_connection():
    """Connect to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)


def create_table():
    """Create the inventory table if it does not exist."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                Inventory_ID VARCHAR(50) PRIMARY KEY,
                Date DATE,
                Product_ID VARCHAR(50),
                Product_Name VARCHAR(150),
                Category VARCHAR(100),
                Warehouse VARCHAR(100),
                Supplier VARCHAR(150),
                Region VARCHAR(100),
                Opening_Stock INT DEFAULT 0,
                Received_Qty INT DEFAULT 0,
                Issued_Qty INT DEFAULT 0,
                Closing_Stock INT DEFAULT 0,
                Reorder_Level INT DEFAULT 0,
                Safety_Stock INT DEFAULT 0,
                Unit_Cost_INR DECIMAL(12,2) DEFAULT 0,
                Inventory_Value_INR DECIMAL(15,2) DEFAULT 0,
                Damaged_Qty INT DEFAULT 0,
                Expired_Qty INT DEFAULT 0,
                Lead_Time_Days INT DEFAULT 0,
                Demand_Qty INT DEFAULT 0,
                Stock_Status VARCHAR(50),
                Salesperson VARCHAR(100),
                Movement_Type VARCHAR(50)
            )
        """)
        connection.commit()
        print("Inventory table is ready.")

    finally:
        cursor.close()
        connection.close()


def save_data(df):
    """Insert CSV records into MySQL without duplicating IDs."""
    missing = [col for col in COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(f"Missing CSV columns: {missing}")

    data = df[COLUMNS].copy()

    # Format dates for MySQL
    data["Date"] = pd.to_datetime(
        data["Date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # Convert missing values into Python None
    data = data.astype(object).where(pd.notna(data), None)

    records = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in data.itertuples(index=False, name=None)
    ]

    placeholders = ", ".join(["%s"] * len(COLUMNS))
    column_names = ", ".join(f"`{col}`" for col in COLUMNS)

    query = f"""
        INSERT IGNORE INTO inventory ({column_names})
        VALUES ({placeholders})
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.executemany(query, records)
        connection.commit()

        inserted = cursor.rowcount
        print(f"Records inserted: {inserted}")
        return inserted

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def fetch_data():
    """Retrieve inventory records from MySQL."""
    connection = get_connection()

    try:
        df = pd.read_sql(
            "SELECT * FROM inventory",
            connection,
        )
        return df

    finally:
        connection.close()


if __name__ == "__main__":
    try:
        create_table()

        if not DATA_FILE.exists():
            raise FileNotFoundError(
                f"CSV file not found: {DATA_FILE}"
            )

        df = pd.read_csv(DATA_FILE)

        print("CSV loaded successfully.")
        print("CSV rows:", len(df))

        save_data(df)

        saved_data = fetch_data()

        print("\nFirst five database records:")
        print(saved_data.head().to_string(index=False))

        print("\nTotal records in MySQL:", len(saved_data))

    except mysql.connector.Error as error:
        print("MySQL error:", error)

    except Exception as error:
        print("Error:", error)