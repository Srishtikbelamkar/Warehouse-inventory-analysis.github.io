import pandas as pd


def inventory_summary(df):
    """Calculate key inventory metrics."""
    total_products = (
        df["Product_ID"].nunique()
        if "Product_ID" in df.columns else 0
    )

    total_stock = (
        df["Closing_Stock"].sum()
        if "Closing_Stock" in df.columns else 0
    )

    total_inventory_value = (
        df["Inventory_Value_INR"].sum()
        if "Inventory_Value_INR" in df.columns else 0
    )

    total_received = (
        df["Received_Qty"].sum()
        if "Received_Qty" in df.columns else 0
    )

    total_issued = (
        df["Issued_Qty"].sum()
        if "Issued_Qty" in df.columns else 0
    )

    total_damaged = (
        df["Damaged_Qty"].sum()
        if "Damaged_Qty" in df.columns else 0
    )

    reorder_count = (
        df["Stock_Status"].eq("Reorder Required").sum()
        if "Stock_Status" in df.columns else 0
    )

    out_of_stock_count = (
        df["Stock_Status"].eq("Out of Stock").sum()
        if "Stock_Status" in df.columns else 0
    )

    return {
        "Total Products": total_products,
        "Total Closing Stock": total_stock,
        "Inventory Value (INR)": total_inventory_value,
        "Total Received": total_received,
        "Total Issued": total_issued,
        "Damaged Quantity": total_damaged,
        "Reorder Required": int(reorder_count),
        "Out of Stock": int(out_of_stock_count),
    }


def category_summary(df):
    """Summarize stock and value by category."""
    return df.groupby("Category", as_index=False).agg(
        Total_Stock=("Closing_Stock", "sum"),
        Total_Received=("Received_Qty", "sum"),
        Total_Issued=("Issued_Qty", "sum"),
        Inventory_Value=("Inventory_Value_INR", "sum"),
    ).sort_values("Inventory_Value", ascending=False)


def warehouse_summary(df):
    """Summarize stock and value by warehouse."""
    return df.groupby("Warehouse", as_index=False).agg(
        Total_Stock=("Closing_Stock", "sum"),
        Inventory_Value=("Inventory_Value_INR", "sum"),
        Total_Damaged=("Damaged_Qty", "sum"),
        Total_Expired=("Expired_Qty", "sum"),
    ).sort_values("Inventory_Value", ascending=False)


def supplier_summary(df):
    """Summarize inventory movement by supplier."""
    return df.groupby("Supplier", as_index=False).agg(
        Total_Received=("Received_Qty", "sum"),
        Total_Damaged=("Damaged_Qty", "sum"),
        Total_Expired=("Expired_Qty", "sum"),
    ).sort_values("Total_Received", ascending=False)


def monthly_summary(df):
    """Summarize inventory movement by month."""
    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"])

    data["Month_Year"] = data["Date"].dt.to_period("M").astype(str)

    return data.groupby("Month_Year", as_index=False).agg(
        Received_Qty=("Received_Qty", "sum"),
        Issued_Qty=("Issued_Qty", "sum"),
        Demand_Qty=("Demand_Qty", "sum"),
        Inventory_Value=("Inventory_Value_INR", "sum"),
    ).sort_values("Month_Year")


if __name__ == "__main__":
    from data_processing import load_data

    df = load_data()

    print("\nINVENTORY SUMMARY")
    for metric, value in inventory_summary(df).items():
        print(f"{metric}: {value:,.2f}")

    print("\nCATEGORY SUMMARY")
    print(category_summary(df).to_string(index=False))

    print("\nWAREHOUSE SUMMARY")
    print(warehouse_summary(df).to_string(index=False))