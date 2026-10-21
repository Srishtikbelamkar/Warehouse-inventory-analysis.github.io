import plotly.express as px
from analytics import (
    category_summary,
    warehouse_summary,
    monthly_summary,
)


def inventory_value_trend(df):
    monthly = monthly_summary(df)

    return px.line(
        monthly,
        x="Month_Year",
        y="Inventory_Value",
        markers=True,
        title="Monthly Inventory Value Trend",
        labels={
            "Month_Year": "Month",
            "Inventory_Value": "Inventory Value (INR)",
        },
    )


def stock_movement_chart(df):
    monthly = monthly_summary(df)

    return px.line(
        monthly,
        x="Month_Year",
        y=["Received_Qty", "Issued_Qty"],
        markers=True,
        title="Monthly Stock Received vs Issued",
        labels={
            "Month_Year": "Month",
            "value": "Quantity",
            "variable": "Movement Type",
        },
    )


def category_stock_chart(df):
    summary = category_summary(df)

    return px.bar(
        summary,
        x="Category",
        y="Total_Stock",
        color="Category",
        title="Closing Stock by Category",
        labels={
            "Category": "Product Category",
            "Total_Stock": "Closing Stock",
        },
    )


def warehouse_value_chart(df):
    summary = warehouse_summary(df)

    return px.bar(
        summary,
        x="Warehouse",
        y="Inventory_Value",
        color="Warehouse",
        title="Inventory Value by Warehouse",
        labels={
            "Warehouse": "Warehouse",
            "Inventory_Value": "Inventory Value (INR)",
        },
    )


def stock_status_chart(df):
    return px.pie(
        df,
        names="Stock_Status",
        title="Inventory Stock Status Distribution",
        hole=0.4,
    )


if __name__ == "__main__":
    from data_processing import load_data

    df = load_data()

    inventory_value_trend(df).show()
    stock_movement_chart(df).show()
    category_stock_chart(df).show()
    warehouse_value_chart(df).show()
    stock_status_chart(df).show()