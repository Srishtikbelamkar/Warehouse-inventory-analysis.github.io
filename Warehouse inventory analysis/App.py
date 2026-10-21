from pathlib import Path
import sys
import hashlib
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

import base64



BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
DATA_FILE = BASE_DIR / "data" / "warehouse_inventory.csv"
DB_FILE = BASE_DIR / "src" / "users.db"
INCIDENT_FILE = BASE_DIR / "src" / "incidents.csv"
IMAGE_PATH = BASE_DIR / "images" / "warehouse_background.png"



    # --------------------------------------------------
# LOGIN / SIGN UP / FORGOT PASSWORD STYLING ONLY
# --------------------------------------------------

st.markdown("""
<style>
/* Center the authentication tabs */
div[data-testid="stTabs"] {
    max-width: 650px;
    margin-left: auto;
    margin-right: auto;
}

/* Style authentication forms */
div[data-testid="stForm"] {
    max-width: 520px;
    margin-left: auto;
    margin-right: auto;
    padding: 24px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #d5e0eb;
    border-radius: 14px;
}

/* Shorter text fields */
div[data-testid="stTextInput"] {
    max-width: 420px;
    margin-left: auto;
    margin-right: auto;
}

/* Center submit buttons */
div[data-testid="stFormSubmitButton"] {
    max-width: 420px;
    margin-left: auto;
    margin-right: auto;
}

div[data-testid="stFormSubmitButton"] button {
    width: 100%;
    border-radius: 8px;
    background-color: #1672bd;
    color: white;
    border: none;
}

/* Authentication messages */
div[data-testid="stAlert"] {
    max-width: 480px;
    margin-left: auto;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)




# --------------------------------------------------
# APPLICATION DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f4f7fb, #ffffff, #eaf4ef);
}
.block-container {
    padding-top: 1.5rem;
}
.hero {
    padding: 22px;
    border-radius: 15px;
    color: white;
    background: linear-gradient(110deg, #142b45, #267358);
    margin-bottom: 20px;
}
.hero h1 {
    margin: 0;
    font-size: 29px;
}
.hero p {
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)


def show_header(title, subtitle=""):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1>'
        f'<p>{subtitle}</p></div>',
        unsafe_allow_html=True
    )


# --------------------------------------------------
# USER DATABASE AND AUTHENTICATION
# --------------------------------------------------

def init_user_database():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, email, password):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                (username.strip(), email.strip().lower(),
                 hash_password(password))
            )
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(identifier, password):
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute("""
            SELECT username, email FROM users
            WHERE (username = ? OR email = ?)
            AND password_hash = ?
        """, (
            identifier.strip(),
            identifier.strip().lower(),
            hash_password(password)
        )).fetchone()

    if row:
        return {"username": row[0], "email": row[1]}

    return None


init_user_database()

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Splash Screen"


# --------------------------------------------------
# SPLASH SCREEN
# --------------------------------------------------

if st.session_state.user is None:

    if st.session_state.page == "Splash Screen":

        show_header(
            "📦 WAREHOUSE INVENTORY ANALYSIS",
            "Inventory monitoring, analytics and intelligent stock management"
        )

        st.markdown("## Welcome to the Warehouse Management System")

        st.write(
            "Monitor inventory levels, analyze warehouse performance, "
            "forecast demand and identify products requiring replenishment."
        )

        if st.button("Get Started →", type="primary"):
            st.session_state.page = "Login"
            st.rerun()

    else:

        show_header(
            "🔐 Account Access",
            "Log in or create your account"
        )

        login_tab, signup_tab, forgot_tab = st.tabs(
            ["Login", "Sign Up", "Forgot Password"]
        )

        with login_tab:
            with st.form("login_form"):
                identifier = st.text_input("Username or email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")

            if submitted:
                user = login_user(identifier, password)

                if user:
                    st.session_state.user = user
                    st.session_state.page = "Home Dashboard"
                    st.rerun()
                else:
                    st.error("Incorrect username/email or password.")

        with signup_tab:
            with st.form("signup_form"):
                username = st.text_input("Create username")
                email = st.text_input("Email address")
                password = st.text_input("Create password", type="password")
                confirm = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create Account")

            if submitted:
                if not username.strip() or not email.strip():
                    st.error("Complete all fields.")
                elif "@" not in email:
                    st.error("Enter a valid email address.")
                elif len(password) < 8:
                    st.error("Password must have at least 8 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif register_user(username, email, password):
                    st.success("Account created. Please log in.")
                else:
                    st.error("Username or email already exists.")

        with forgot_tab:
            st.warning(
                "Demo recovery only. This form does not verify account "
                "ownership or send an email."
            )

            with st.form("forgot_form"):
                email = st.text_input("Registered email")
                new_password = st.text_input(
                    "New password", type="password"
                )
                submitted = st.form_submit_button("Reset Password")

            if submitted:
                if len(new_password) < 8:
                    st.error("Password must have at least 8 characters.")
                else:
                    with sqlite3.connect(DB_FILE) as conn:
                        cur = conn.execute(
                            "UPDATE users SET password_hash=? WHERE email=?",
                            (hash_password(new_password), email.strip().lower())
                        )

                    if cur.rowcount:
                        st.success("Password reset. Please log in.")
                    else:
                        st.error("Email address not found.")

    st.stop()


# --------------------------------------------------
# LOAD AND PREPARE INVENTORY DATA
# --------------------------------------------------

def load_inventory():
    uploaded = st.session_state.get("uploaded_data")

    if uploaded is not None:
        df = uploaded.copy()
    elif DATA_FILE.exists():
        if DATA_FILE.suffix.lower() == ".xlsx":
            df = pd.read_excel(DATA_FILE)
        else:
            df = pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame()

    df.columns = df.columns.astype(str).str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date"], errors="coerce", dayfirst=True
        )

    numeric_columns = [
        "Opening_Stock", "Received_Qty", "Issued_Qty",
        "Closing_Stock", "Reorder_Level", "Safety_Stock",
        "Unit_Cost_INR", "Inventory_Value_INR",
        "Damaged_Qty", "Expired_Qty", "Lead_Time_Days",
        "Demand_Qty"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if {"Closing_Stock", "Unit_Cost_INR"}.issubset(df.columns):
        df["Inventory_Value_INR"] = (
            df["Closing_Stock"] * df["Unit_Cost_INR"]
        )

    if {"Closing_Stock", "Reorder_Level"}.issubset(df.columns):
        df["Stock_Status"] = np.select(
            [
                df["Closing_Stock"] <= 0,
                df["Closing_Stock"] <= df["Reorder_Level"]
            ],
            ["Out of Stock", "Reorder Required"],
            default="Stock Sufficient"
        )

    return df.drop_duplicates().reset_index(drop=True)


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

pages = [
    "Home Dashboard",
    "Live Inventory",
    "Inventory Analytics",
    "Demand Forecasting",
    "Stock Optimization",
    "Incident Reporting",
    "Alerts & Notifications",
    "History & Reports",
    "Profile & Settings"
]

with st.sidebar:
    st.title("📦 Warehouse App")
    st.write(f"User: **{st.session_state.user['username']}**")

    selected_page = st.radio(
        "Navigation",
        pages,
        index=(
            pages.index(st.session_state.page)
            if st.session_state.page in pages else 0
        )
    )

    st.session_state.page = selected_page

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload inventory CSV or Excel",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".xlsx"):
                st.session_state.uploaded_data = pd.read_excel(
                    uploaded_file
                )
            else:
                st.session_state.uploaded_data = pd.read_csv(
                    uploaded_file
                )
            st.success("Inventory file loaded.")
        except Exception as error:
            st.error(f"Unable to load file: {error}")

    if st.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.page = "Login"
        st.session_state.pop("uploaded_data", None)
        st.rerun()


df = load_inventory()

if df.empty:
    show_header(
        st.session_state.page,
        "Load your warehouse inventory dataset to continue."
    )
    st.warning(
        "Place warehouse_inventory.csv inside the data folder, "
        "or upload a CSV/Excel file in the sidebar."
    )
    st.info(
        "Expected fields include Product_ID, Product_Name, Category, "
        "Warehouse, Closing_Stock, Reorder_Level, Demand_Qty and Unit_Cost_INR."
    )
    st.stop()


# --------------------------------------------------
# FILTERS
# --------------------------------------------------

with st.sidebar:
    st.subheader("Inventory Filters")

    if "Warehouse" in df.columns:
        warehouses = sorted(
            df["Warehouse"].dropna().astype(str).unique()
        )
        chosen_warehouses = st.multiselect(
            "Warehouse", warehouses, default=warehouses
        )
        if chosen_warehouses:
            df = df[df["Warehouse"].astype(str).isin(chosen_warehouses)]

    if "Category" in df.columns:
        categories = sorted(
            df["Category"].dropna().astype(str).unique()
        )
        chosen_categories = st.multiselect(
            "Category", categories, default=categories
        )
        if chosen_categories:
            df = df[df["Category"].astype(str).isin(chosen_categories)]


def total(column):
    if column not in df.columns:
        return 0
    return pd.to_numeric(df[column], errors="coerce").fillna(0).sum()


def show_chart(fig):
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)


page = st.session_state.page


# --------------------------------------------------
# 3. HOME DASHBOARD
# --------------------------------------------------

if page == "Home Dashboard":

    show_header(
        "🏠 Home Dashboard",
        "Overview of stock levels, inventory value and warehouse performance"
    )

    product_count = (
        df["Product_ID"].nunique() if "Product_ID" in df.columns else 0
    )
    reorder_count = (
        df["Stock_Status"].eq("Reorder Required").sum()
        if "Stock_Status" in df.columns else 0
    )
    out_count = (
        df["Stock_Status"].eq("Out of Stock").sum()
        if "Stock_Status" in df.columns else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Products", f"{product_count:,}")
    c2.metric("Closing Stock", f"{total('Closing_Stock'):,.0f}")
    c3.metric("Inventory Value", f"₹{total('Inventory_Value_INR'):,.0f}")
    c4.metric("Reorder Required", f"{reorder_count:,}")
    c5.metric("Out of Stock", f"{out_count:,}")

    left, right = st.columns(2)

    if {"Category", "Closing_Stock"}.issubset(df.columns):
        category = df.groupby("Category", as_index=False)["Closing_Stock"].sum()
        left.plotly_chart(
            px.bar(category, x="Category", y="Closing_Stock",
                   title="Closing Stock by Category"),
            use_container_width=True
        )

    if "Stock_Status" in df.columns:
        status = df["Stock_Status"].value_counts().reset_index()
        status.columns = ["Stock_Status", "Count"]
        right.plotly_chart(
            px.pie(status, names="Stock_Status", values="Count",
                   title="Stock Status Distribution"),
            use_container_width=True
        )

    st.subheader("Recent Inventory Records")
    st.dataframe(df.tail(20), use_container_width=True, hide_index=True)


# --------------------------------------------------
# 4. LIVE INVENTORY
# --------------------------------------------------

elif page == "Live Inventory":

    show_header(
        "📡 Live Inventory",
        "View the latest inventory records and stock availability"
    )

    st.caption(
        "This page displays the latest available dataset. "
        "Automatic warehouse-system updates require a live data connection."
    )

    view = (
        df.sort_values("Date", ascending=False).head(100)
        if "Date" in df.columns else df.tail(100)
    )

    a, b, c = st.columns(3)
    a.metric("Records Shown", len(view))
    b.metric(
        "Warehouses",
        view["Warehouse"].nunique() if "Warehouse" in view.columns else "N/A"
    )
    c.metric(
        "Products Requiring Reorder",
        int(view["Stock_Status"].isin(
            ["Reorder Required", "Out of Stock"]
        ).sum()) if "Stock_Status" in view.columns else "N/A"
    )

    st.dataframe(view, use_container_width=True, hide_index=True)

    


# --------------------------------------------------
# 5. INVENTORY ANALYTICS
# --------------------------------------------------

elif page == "Inventory Analytics":

    show_header(
        "📊 Inventory Analytics",
        "Category, warehouse, supplier and stock movement analysis"
    )

    left, right = st.columns(2)

    if {"Category", "Inventory_Value_INR"}.issubset(df.columns):
        cat = df.groupby("Category", as_index=False)["Inventory_Value_INR"].sum()
        left.plotly_chart(
            px.bar(cat, x="Category", y="Inventory_Value_INR",
                   title="Inventory Value by Category"),
            use_container_width=True
        )

    if {"Warehouse", "Closing_Stock"}.issubset(df.columns):
        wh = df.groupby("Warehouse", as_index=False)["Closing_Stock"].sum()
        right.plotly_chart(
            px.bar(wh, x="Warehouse", y="Closing_Stock",
                   title="Closing Stock by Warehouse"),
            use_container_width=True
        )

    if {"Date", "Received_Qty", "Issued_Qty"}.issubset(df.columns):
        monthly = df.groupby(df["Date"].dt.to_period("M").astype(str)).agg(
            Received_Qty=("Received_Qty", "sum"),
            Issued_Qty=("Issued_Qty", "sum")
        ).reset_index(names="Month")

        st.plotly_chart(
            px.line(
                monthly, x="Month",
                y=["Received_Qty", "Issued_Qty"],
                markers=True, title="Monthly Stock Movement"
            ),
            use_container_width=True
        )

    if {"Supplier", "Received_Qty"}.issubset(df.columns):
        supplier = df.groupby("Supplier", as_index=False)["Received_Qty"].sum()
        st.plotly_chart(
            px.bar(supplier, x="Supplier", y="Received_Qty",
                   title="Received Quantity by Supplier"),
            use_container_width=True
        )

    st.subheader("Inventory Data")
    st.dataframe(df, use_container_width=True, hide_index=True)


# --------------------------------------------------
# 6. DEMAND FORECASTING
# --------------------------------------------------

elif page == "Demand Forecasting":

    show_header(
        "🔮 Demand Forecasting",
        "Estimate demand for upcoming months"
    )

    months = st.slider("Months to forecast", 3, 12, 6)

    if {"Date", "Demand_Qty"}.issubset(df.columns):

        temp = df.dropna(subset=["Date"]).copy()
        monthly = temp.groupby(
            temp["Date"].dt.to_period("M")
        )["Demand_Qty"].sum().sort_index()

        if len(monthly) == 0:
            st.warning("No valid demand history is available.")
        else:
            average_demand = monthly.tail(3).mean()
            future_months = pd.period_range(
                monthly.index.max() + 1,
                periods=months,
                freq="M"
            )

            forecast = pd.DataFrame({
                "Month": future_months.astype(str),
                "Forecast_Demand": [round(average_demand, 2)] * months
            })

            st.metric(
                "Estimated Monthly Demand",
                f"{average_demand:,.0f}"
            )

            st.plotly_chart(
                px.line(
                    forecast, x="Month", y="Forecast_Demand",
                    markers=True, title="Demand Forecast"
                ),
                use_container_width=True
            )

            st.dataframe(forecast, use_container_width=True, hide_index=True)

            st.download_button(
                "Download Forecast CSV",
                forecast.to_csv(index=False).encode("utf-8"),
                "demand_forecast.csv",
                "text/csv"
            )

    else:
        st.warning("The dataset must contain Date and Demand_Qty columns.")

    st.caption(
        "This starter forecast uses the average of the latest three months; "
        "it is an estimate, not a guarantee."
    )


# --------------------------------------------------
# 7. STOCK OPTIMIZATION
# --------------------------------------------------

elif page == "Stock Optimization":

    show_header(
        "⚙️ Stock Optimization",
        "Identify low-stock products and suggested replenishment quantities"
    )

    required = [
        "Product_ID", "Product_Name", "Warehouse",
        "Closing_Stock", "Reorder_Level", "Safety_Stock"
    ]

    if all(col in df.columns for col in required):

        optimized = df.copy()

        if "Date" in optimized.columns:
            optimized = optimized.sort_values("Date")

        optimized = optimized.drop_duplicates(
            ["Product_ID", "Warehouse"], keep="last"
        )

        daily_demand = (
            optimized["Demand_Qty"].fillna(0) / 30
            if "Demand_Qty" in optimized.columns else 0
        )

        lead_time = (
            optimized["Lead_Time_Days"].fillna(1)
            if "Lead_Time_Days" in optimized.columns else 1
        )

        optimized["Suggested_Reorder_Point"] = (
            daily_demand * lead_time + optimized["Safety_Stock"]
        )

        optimized["Suggested_Order_Qty"] = np.ceil(
            (
                optimized["Suggested_Reorder_Point"]
                - optimized["Closing_Stock"]
            ).clip(lower=0)
        ).astype(int)

        optimized["Recommendation"] = np.where(
            optimized["Closing_Stock"] <= optimized["Suggested_Reorder_Point"],
            "Order Now",
            "Stock Sufficient"
        )

        needs_order = optimized[
            optimized["Recommendation"] == "Order Now"
        ]

        st.metric("Products Recommended for Reorder", len(needs_order))
        st.dataframe(optimized, use_container_width=True, hide_index=True)

        st.download_button(
            "Download Optimization CSV",
            optimized.to_csv(index=False).encode("utf-8"),
            "stock_optimization.csv",
            "text/csv"
        )

    else:
        st.warning("Some required inventory columns are missing.")

    st.caption(
        "The daily-demand calculation assumes Demand_Qty is approximately "
        "a monthly quantity. Adjust it to match your dataset's actual period."
    )




# --------------------------------------------------
# 8. INCIDENT REPORTING
# --------------------------------------------------

elif page == "Incident Reporting":

    show_header(
        "⚠️ Incident Reporting",
        "Report damaged stock, expired products or warehouse issues"
    )

    warehouses = (
        sorted(df["Warehouse"].dropna().astype(str).unique())
        if "Warehouse" in df.columns else []
    )
    products = (
        sorted(df["Product_ID"].dropna().astype(str).unique())
        if "Product_ID" in df.columns else []
    )

    with st.form("incident_form", clear_on_submit=True):

        warehouse = (
            st.selectbox("Warehouse", warehouses)
            if warehouses else st.text_input("Warehouse")
        )

        product = st.selectbox(
            "Product ID", ["Not specified"] + products
        )

        incident_type = st.selectbox(
            "Incident Type",
            [
                "Damaged Stock", "Expired Stock", "Stock Mismatch",
                "Supplier Delay", "Warehouse Issue", "Other"
            ]
        )

        severity = st.select_slider(
            "Severity",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium"
        )

        description = st.text_area("Description")
        submitted = st.form_submit_button("Submit Report")

    if submitted:

        if not description.strip():
            st.error("Enter an incident description.")

        else:
            record = pd.DataFrame([{
                "Reported_At": pd.Timestamp.now(),
                "Warehouse": warehouse,
                "Product_ID": product,
                "Incident_Type": incident_type,
                "Severity": severity,
                "Description": description,
                "Reporter": st.session_state.user["username"]
            }])

            INCIDENT_FILE.parent.mkdir(parents=True, exist_ok=True)
            record.to_csv(
                INCIDENT_FILE,
                mode="a",
                header=not INCIDENT_FILE.exists(),
                index=False
            )

            st.success("Incident report saved.")

    st.subheader("Submitted Incidents")

    if INCIDENT_FILE.exists():
        st.dataframe(
            pd.read_csv(INCIDENT_FILE),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No incident reports have been submitted yet.")


# --------------------------------------------------
# 9. ALERTS AND NOTIFICATIONS
# --------------------------------------------------

elif page == "Alerts & Notifications":

    show_header(
        "🔔 Alerts & Notifications",
        "Monitor reorder, out-of-stock, damaged and expired inventory"
    )

    alerts = []

    for _, row in df.iterrows():

        status = str(row.get("Stock_Status", ""))

        if status in ["Reorder Required", "Out of Stock"]:
            alerts.append({
                "Alert": status,
                "Product_ID": row.get("Product_ID", ""),
                "Product_Name": row.get("Product_Name", ""),
                "Warehouse": row.get("Warehouse", ""),
                "Details": f"Closing stock: {row.get('Closing_Stock', 0)}"
            })

        if row.get("Damaged_Qty", 0) > 0:
            alerts.append({
                "Alert": "Damaged Stock",
                "Product_ID": row.get("Product_ID", ""),
                "Product_Name": row.get("Product_Name", ""),
                "Warehouse": row.get("Warehouse", ""),
                "Details": f"Damaged quantity: {row.get('Damaged_Qty', 0)}"
            })

        if row.get("Expired_Qty", 0) > 0:
            alerts.append({
                "Alert": "Expired Stock",
                "Product_ID": row.get("Product_ID", ""),
                "Product_Name": row.get("Product_Name", ""),
                "Warehouse": row.get("Warehouse", ""),
                "Details": f"Expired quantity: {row.get('Expired_Qty', 0)}"
            })

    alert_df = pd.DataFrame(alerts).drop_duplicates()

    if alert_df.empty:
        st.success("No alerts found in the selected inventory data.")
    else:
        st.metric("Alerts Generated", len(alert_df))
        st.dataframe(alert_df, use_container_width=True, hide_index=True)

        st.download_button(
            "Download Alerts CSV",
            alert_df.to_csv(index=False).encode("utf-8"),
            "inventory_alerts.csv",
            "text/csv"
        )

    st.caption(
        "These are dataset-based alerts. Automated email or mobile notifications "
        "require additional services."
    )


# --------------------------------------------------
# 10. HISTORY AND REPORTS
# --------------------------------------------------

elif page == "History & Reports":

    show_header(
        "📄 History & Reports",
        "Review historical inventory and export reports"
    )

    st.metric("Inventory Records", len(df))
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Export Inventory History CSV",
        df.to_csv(index=False).encode("utf-8"),
        "inventory_history.csv",
        "text/csv"
    )

    if "Date" in df.columns:
        st.subheader("Monthly Inventory Report")

        monthly_cols = [
            c for c in [
                "Received_Qty", "Issued_Qty",
                "Demand_Qty", "Inventory_Value_INR"
            ] if c in df.columns
        ]

        if monthly_cols:
            monthly = df.groupby(
                df["Date"].dt.to_period("M").astype(str)
            )[monthly_cols].sum().reset_index(names="Month")

            st.dataframe(
                monthly, use_container_width=True, hide_index=True
            )

            st.download_button(
                "Export Monthly Report CSV",
                monthly.to_csv(index=False).encode("utf-8"),
                "monthly_inventory_report.csv",
                "text/csv"
            )

    st.subheader("Incident History")

    if INCIDENT_FILE.exists():
        st.dataframe(
            pd.read_csv(INCIDENT_FILE),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No incident history available.")


# --------------------------------------------------
# 11. PROFILE AND SETTINGS
# --------------------------------------------------

elif page == "Profile & Settings":

    show_header(
        "👤 Profile & Settings",
        "Manage your account and application preferences"
    )

    st.write(f"**Username:** {st.session_state.user['username']}")
    st.write(f"**Email:** {st.session_state.user['email']}")

    with st.form("password_form"):

        current_password = st.text_input(
            "Current password", type="password"
        )

        new_password = st.text_input(
            "New password", type="password"
        )

        confirm_password = st.text_input(
            "Confirm new password", type="password"
        )

        submitted = st.form_submit_button("Change Password")

    if submitted:

        current_user = login_user(
            st.session_state.user["username"],
            current_password
        )

        if not current_user:
            st.error("Current password is incorrect.")

        elif len(new_password) < 8:
            st.error("New password must have at least 8 characters.")

        elif new_password != confirm_password:
            st.error("Passwords do not match.")

        else:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute(
                    "UPDATE users SET password_hash=? WHERE username=?",
                    (
                        hash_password(new_password),
                        st.session_state.user["username"]
                    )
                )

            st.success("Password changed successfully.")

    st.toggle("Enable notifications (demo setting)", value=True)

    st.selectbox(
        "Theme Preference",
        ["Light", "Dark", "System"]
    )

    st.caption(
        "Theme and notification settings are demo controls and are not saved yet."
    )

# Logout is available in the sidebar from every authenticated page.