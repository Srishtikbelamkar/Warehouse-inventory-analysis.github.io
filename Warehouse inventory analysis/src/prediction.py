import pandas as pd


def forecast_demand(df, forecast_months=6):
    """Forecast monthly demand using the latest three-month average."""
    data = df.copy()

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"])

    data["Month"] = data["Date"].dt.to_period("M")

    monthly_demand = (
        data.groupby("Month")["Demand_Qty"]
        .sum()
        .sort_index()
    )

    if monthly_demand.empty:
        raise ValueError("No valid demand data is available.")

    recent_average = monthly_demand.tail(3).mean()

    last_month = monthly_demand.index.max()
    future_months = pd.period_range(
        start=last_month + 1,
        periods=forecast_months,
        freq="M",
    )

    forecast = pd.DataFrame({
        "Month": future_months.astype(str),
        "Forecast_Demand": [round(recent_average, 2)] * forecast_months,
    })

    return forecast


if __name__ == "__main__":
    from data_processing import load_data

    df = load_data()

    result = forecast_demand(df, forecast_months=6)
    print("\nDEMAND FORECAST")
    print(result.to_string(index=False))