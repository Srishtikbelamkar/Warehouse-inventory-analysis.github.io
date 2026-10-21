import pandas as pd


def optimize_inventory(df):
    """Identify products requiring replenishment."""
    data = df.copy()

    required_columns = [
        "Product_ID",
        "Product_Name",
        "Warehouse",
        "Closing_Stock",
        "Reorder_Level",
        "Safety_Stock",
        "Demand_Qty",
        "Lead_Time_Days",
    ]

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Use the most recent record for each product and warehouse.
    if "Date" in data.columns:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        data = data.sort_values("Date")

    latest = data.drop_duplicates(
        subset=["Product_ID", "Warehouse"],
        keep="last",
    ).copy()

    # Estimate average daily demand using a 30-day period.
    latest["Average_Daily_Demand"] = latest["Demand_Qty"] / 30

    latest["Reorder_Point"] = (
        latest["Average_Daily_Demand"] * latest["Lead_Time_Days"]
        + latest["Safety_Stock"]
    )

    latest["Suggested_Order_Qty"] = (
        latest["Reorder_Point"] - latest["Closing_Stock"]
    ).clip(lower=0).apply(lambda value: int(value + 0.999999))

    latest["Recommendation"] = latest.apply(
        lambda row: (
            "Order Now"
            if row["Closing_Stock"] <= row["Reorder_Point"]
            else "Stock Sufficient"
        ),
        axis=1,
    )

    return latest[[
        "Product_ID",
        "Product_Name",
        "Warehouse",
        "Closing_Stock",
        "Reorder_Level",
        "Safety_Stock",
        "Average_Daily_Demand",
        "Reorder_Point",
        "Suggested_Order_Qty",
        "Recommendation",
    ]].sort_values(
        ["Recommendation", "Suggested_Order_Qty"],
        ascending=[True, False],
    )


if __name__ == "__main__":
    from data_processing import load_data

    df = load_data()
    result = optimize_inventory(df)

    print("\nINVENTORY OPTIMIZATION")
    print(result.head(20).to_string(index=False))