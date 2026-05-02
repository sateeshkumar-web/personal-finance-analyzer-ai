# app.py - Dark Premium + All Advanced Features ✨
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Try to import ARIMA (for forecasting)
try:
    from statsmodels.tsa.arima.model import ARIMA
    HAS_ARIMA = True
except Exception:
    HAS_ARIMA = False

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(
    page_title="Personal Finance Analyzer",
    page_icon="💸",
    layout="wide",
)

# ------------------ GLOBAL STYLE ------------------ #
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1f2933 0, #020617 45%, #020617 100%);
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    h1 {
        margin-bottom: 0.2rem;
        color: #f9fafb !important;
        font-weight: 750;
    }
    h2, h3, h4 {
        color: #e5e7eb !important;
    }

    .metric-card {
        padding: 1rem 1.2rem;
        border-radius: 0.9rem;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.45);
        box-shadow: 0 18px 35px rgba(15, 23, 42, 0.85);
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #9ca3af;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 0.2rem;
        color: #f9fafb;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #9ca3af;
    }

    .stTabs [role="tablist"] {
        gap: 0.35rem;
        margin-top: 0.2rem;
        margin-bottom: 0.8rem;
    }
    .stTabs [role="tab"] {
        padding: 0.45rem 1.0rem;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.45);
        background: #020617;
        color: #e5e7eb;
        font-size: 0.9rem;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #22c55e, #22d3ee);
        color: #020617;
        border-color: transparent;
        font-weight: 600;
        box-shadow: 0 8px 22px rgba(34, 197, 94, 0.4);
    }

    section[data-testid="stSidebar"] > div {
        background: #020617;
        border-right: 1px solid rgba(55,65,81,0.85);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label {
        color: #e5e7eb !important;
    }

    .footer {
        margin-top: 1.8rem;
        padding-top: 0.6rem;
        border-top: 1px solid rgba(31,41,55,0.8);
        font-size: 0.8rem;
        color: #9ca3af;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ HEADER ------------------ #
st.markdown(
    """
    <div style="margin-bottom: 1.2rem;">
        <h1>💸 Personal Finance Analyzer</h1>
        <p style="color:#E5E7EB; font-size:0.95rem;">
            Upload one or two CSVs and instantly see where your money goes —
            trends, categories, forecasts, subscriptions, and smart insights.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------ SIDEBAR ------------------ #
st.sidebar.header("⚙️ Settings")

currency_symbol = st.sidebar.text_input("Currency symbol", "₹")
base_label = st.sidebar.text_input("Label for main file", "This Period")
compare_label = st.sidebar.text_input("Label for comparison file", "Previous Period")

st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ CSV format")
st.sidebar.write(
    "Required columns:\n\n"
    "- `date` → e.g. 2024-06-01\n"
    "- `description` → merchant / note\n"
    "- `amount` → negative for expenses, positive for income"
)

with st.sidebar.expander("Need a sample CSV?"):
    st.code(
        "date,description,amount\n"
        "2024-06-01,Starbucks,-5.25\n"
        "2024-06-02,Amazon Marketplace,-749.00\n"
        "2024-06-03,Uber,-230.00\n"
        "2024-06-05,Salary,42000.00",
        language="csv",
    )

# ------------------ FILE UPLOADS ------------------ #
st.subheader("📂 Upload transactions CSV")

col_up1, col_up2 = st.columns(2)
with col_up1:
    base_file = st.file_uploader("Main period CSV", type=["csv"], key="base_csv")
with col_up2:
    compare_file = st.file_uploader("Comparison CSV (optional)", type=["csv"], key="compare_csv")










# ================== CSV AUTO-CONVERTER (BETA) ================== #
st.markdown("---")
st.subheader("🛠 CSV auto-converter (beta)")

st.write(

    "Here you can upload any CSV and convert it into the app-compatible format [date, description, amount]."



)

conv_file = st.file_uploader(
    "Upload ANY CSV to convert to app format",
    type=["csv"],
    key="converter_csv"
)

if conv_file is not None:
    import pandas as pd
    import numpy as np

    conv_df = pd.read_csv(conv_file)

    st.markdown("**🔍 Preview of uploaded data:**")
    st.dataframe(conv_df.head(), use_container_width=True)

    cols = list(conv_df.columns)

    # --- Try to auto-detect useful columns ---
    def guess_col(candidates, default_index=0):
        for i, c in enumerate(cols):
            lc = str(c).lower()
            if any(x in lc for x in candidates):
                return i
        return default_index

    date_idx = guess_col(["date", "period", "time"])
    desc_idx = guess_col(["desc", "detail", "narration", "industry", "name"])

    # numeric auto-detect
    numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(conv_df[c])]
    amount_idx = cols.index(numeric_cols[0]) if numeric_cols else guess_col(["value", "amount"])

    # --- User chooses the real columns ---
    date_col = st.selectbox("📅 Choose DATE column", cols, index=date_idx)
    desc_col = st.selectbox("📝 Choose DESCRIPTION column", cols, index=desc_idx)
    amount_col = st.selectbox("💰 Choose AMOUNT column", cols, index=amount_idx)

    # --- Amount sign selection ---
    sign_option = st.radio(
        "Amount kis format me hai?",
        [
            "Already + and - correctly",
            "Sab positive hai — Expense / Income alag column me hai",
        ]
    )

    type_col = None
    if sign_option.startswith("Sab positive"):
        type_col = st.selectbox(
            "Type column choose karein (Income/Expense, Debit/Credit)",
            cols
        )

    # --- Convert Button ---
    if st.button("⚙️ Convert & Download CSV", type="primary"):
        out = pd.DataFrame()

        # Date fixing
        out["date"] = pd.to_datetime(conv_df[date_col], errors="coerce").dt.date

        # Description
        out["description"] = conv_df[desc_col].astype(str)

        # Amount fixing
        amt = pd.to_numeric(conv_df[amount_col], errors="coerce")

        if sign_option.startswith("Already"):
            out["amount"] = amt
        else:
            t = conv_df[type_col].astype(str).str.lower()
            is_expense = (
                t.str.contains("exp")
                | t.str.contains("debit")
                | t.str.contains("dr")
            )
            out["amount"] = np.where(is_expense, -abs(amt), abs(amt))

        out = out.dropna(subset=["date", "amount"])

        st.success("✅ Conversion successful!")
        st.dataframe(out.head(), use_container_width=True)

        csv_bytes = out.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download converted CSV",
            csv_bytes,
            "converted_for_finance_app.csv",
            mime="text/csv",
        )














# ------------------ HELPERS ------------------ #
def fmt_money(x: float) -> str:
    sign = "-" if x < 0 else ""
    return f"{sign}{currency_symbol}{abs(x):,.2f}"

CATEGORY_KEYWORDS = {
    "Coffee & Snacks": ["starbucks", "coffee", "cafe"],
    "Groceries": ["supermarket", "grocery", "bigbasket", "dmart"],
    "Transport": ["uber", "ola", "lyft", "taxi", "metro", "bus", "train"],
    "Entertainment": ["netflix", "spotify", "prime", "youtube", "movie", "pvr"],
    "Shopping": ["amazon", "flipkart", "myntra"],
    "Bills & Utilities": ["electricity", "water", "bill", "internet", "mobile", "phone"],
    "Dining Out": ["restaurant", "pizza", "burger", "food court"],
    "Income": ["salary", "payroll", "credit", "refund"],
}

def rule_category(desc: str) -> str:
    s = str(desc).lower()
    for cat, keys in CATEGORY_KEYWORDS.items():
        for k in keys:
            if k in s:
                return cat
    return "Other"

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    if "date" not in df.columns or "amount" not in df.columns or "description" not in df.columns:
        st.error("❌ CSV must contain `date`, `description`, and `amount` columns.")
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount"])
    df["description"] = df["description"].fillna("").astype(str)

    if "category" not in df.columns:
        df["category"] = df["description"].apply(rule_category)

    df["date_only"] = df["date"].dt.date
    return df

def compute_metrics(df: pd.DataFrame):
    total_spend = -df.loc[df["amount"] < 0, "amount"].sum()
    total_income = df.loc[df["amount"] > 0, "amount"].sum()
    daily = df.groupby("date_only")["amount"].sum()
    avg_daily_net = daily.mean() if not daily.empty else 0

    date_min = df["date_only"].min()
    date_max = df["date_only"].max()
    days = (date_max - date_min).days + 1 if pd.notnull(date_min) and pd.notnull(date_max) else None

    return total_spend, total_income, avg_daily_net, days

# ------------------ LOAD DATA ------------------ #
if base_file is None:
    st.info("⬆️ Upload at least the main CSV to see your dashboard.")
    st.stop()

base_raw = pd.read_csv(base_file)
base_df = clean_df(base_raw)
if base_df.empty:
    st.stop()

compare_df = None
if compare_file is not None:
    try:
        compare_raw = pd.read_csv(compare_file)
        compare_df = clean_df(compare_raw)
        if compare_df.empty:
            compare_df = None
    except Exception:
        compare_df = None
        st.warning("Could not read comparison CSV.")

# ------------------ METRICS ------------------ #
base_spend, base_income, base_avg_daily, base_days = compute_metrics(base_df)
if compare_df is not None:
    cmp_spend, cmp_income, cmp_avg_daily, cmp_days = compute_metrics(compare_df)

st.markdown("### 🔍 Overview")

cols = st.columns(4)
with cols[0]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Spend ({base_label})</div>
            <div class="metric-value" style="color:#f97373;">{fmt_money(base_spend)}</div>
            <div class="metric-sub">{base_days or '-'} days</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with cols[1]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Income ({base_label})</div>
            <div class="metric-value" style="color:#4ade80;">{fmt_money(base_income)}</div>
            <div class="metric-sub">{base_days or '-'} days</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with cols[2]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Net ({base_label})</div>
            <div class="metric-value">{fmt_money(base_income - base_spend)}</div>
            <div class="metric-sub">Income − Spend</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with cols[3]:
    avg_text = fmt_money(base_avg_daily) if not np.isnan(base_avg_daily) else f"{currency_symbol}0.00"
    sub = f"{base_days} days" if base_days else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Avg Daily Net</div>
            <div class="metric-value">{avg_text}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Comparison summary
if compare_df is not None:
    st.markdown("#### 📊 Comparison overview")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**{base_label}**")
        st.write(f"- Total spend: {fmt_money(base_spend)}")
        st.write(f"- Total income: {fmt_money(base_income)}")
        st.write(f"- Net: {fmt_money(base_income - base_spend)}")
    with c2:
        st.write(f"**{compare_label}**")
        st.write(f"- Total spend: {fmt_money(cmp_spend)}")
        st.write(f"- Total income: {fmt_money(cmp_income)}")
        st.write(f"- Net: {fmt_money(cmp_income - cmp_spend)}")

    diff_spend = base_spend - cmp_spend
    st.info(
        f"Change in spending vs **{compare_label}**: "
        f"{'increased' if diff_spend > 0 else 'decreased'} by **{fmt_money(diff_spend)}**."
    )

st.markdown("")

# ------------------ MAIN TABS ------------------ #
tab_overview, tab_categories, tab_table = st.tabs(
    ["📊 Trends & Forecast", "📂 Categories & Heatmap", "📜 Transactions"]
)

# ========== TAB 1: TRENDS & FORECAST ========== #
with tab_overview:
    st.markdown("#### 📈 Net amount over time")

    ts = base_df.groupby("date")["amount"].sum().reset_index()
    fig_ts = px.line(
        ts,
        x="date",
        y="amount",
        markers=True,
        labels={"amount": "Net amount", "date": "Date"},
        title="Daily net cashflow",
    )
    fig_ts.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="rgba(15,23,42,1)",
        paper_bgcolor="rgba(15,23,42,1)",
        font_color="#e5e7eb",
    )
    fig_ts.update_xaxes(showgrid=True, gridcolor="#1f2937")
    fig_ts.update_yaxes(showgrid=True, gridcolor="#1f2937")
    st.plotly_chart(fig_ts, use_container_width=True)










    # --- Forecast next 30 days (expenses only) --- #
    
    st.markdown("#### 🔮 Forecast next 30 days (expenses)")

    # Only negative amounts → expenses
    daily_expense = (
    base_df.loc[base_df["amount"] < 0]     # filter negative amounts
    .groupby("date")["amount"]
    .sum()
    .abs()                                 # convert negative expenses to positive
    .sort_index()
)






    if len(daily_expense) < 15:
        st.info("Not enough history to build a reliable forecast (need ~15+ expense days).")
    elif not HAS_ARIMA:
        st.warning(
            "ARIMA model not available. Install with: "
            "`pip install statsmodels -i https://pypi.tuna.tsinghua.edu.cn/simple`"
        )
    else:
        try:
            model = ARIMA(daily_expense, order=(1, 1, 1))
            model_fit = model.fit()
            forecast_steps = 30
            forecast = model_fit.forecast(steps=forecast_steps)

            fc_df = pd.DataFrame(
                {
                    "date": pd.date_range(
                        daily_expense.index[-1] + pd.Timedelta(days=1),
                        periods=forecast_steps,
                    ),
                    "forecast": forecast,
                }
            )

            fig_fc = px.line(
                daily_expense.reset_index(),
                x="date",
                y="amount",
                labels={"amount": "Daily expense", "date": "Date"},
                title="Historical & forecasted daily expenses",
            )
            fig_fc.add_scatter(
                x=fc_df["date"],
                y=fc_df["forecast"],
                mode="lines",
                name="Forecast",
            )
            fig_fc.update_layout(
                margin=dict(l=10, r=10, t=40, b=10),
                plot_bgcolor="rgba(15,23,42,1)",
                paper_bgcolor="rgba(15,23,42,1)",
                font_color="#e5e7eb",
            )
            fig_fc.update_xaxes(showgrid=True, gridcolor="#1f2937")
            fig_fc.update_yaxes(showgrid=True, gridcolor="#1f2937")
            st.plotly_chart(fig_fc, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not build ARIMA forecast: {e}")

# ========== TAB 2: CATEGORIES & HEATMAP ========== #
with tab_categories:
    st.markdown("#### 🧁 Spending by category")

    spend_df = (
        base_df[base_df["amount"] < 0]
        .groupby("category")["amount"]
        .sum()
        .abs()
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    if spend_df.empty:
        st.write("No expenses to show.")
    else:
        fig_pie = px.pie(
            spend_df,
            names="category",
            values="amount",
            title="Share of expenses by category",
            hole=0.45,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(15,23,42,1)",
            font_color="#e5e7eb",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### 📊 Category totals")
        spend_df["amount"] = spend_df["amount"].apply(fmt_money)
        st.dataframe(
            spend_df.rename(columns={"category": "Category", "amount": "Total spend"}),
            use_container_width=True,
        )









    

    # --- Calendar-style daily heatmap --- #
    st.markdown("#### 📅 Calendar-style daily spending heatmap")

    daily_exp = (
    base_df.loc[base_df["amount"] < 0]   # only expenses
    .groupby("date")["amount"]
    .sum()
    .abs()                               # make them positive for visualization
    .reset_index()
)














    if daily_exp.empty:
        st.info("No expenses to visualize in heatmap.")
    else:
        daily_exp["date"] = pd.to_datetime(daily_exp["date"])
        iso = daily_exp["date"].dt.isocalendar()
        daily_exp["year"] = iso.year
        daily_exp["week"] = iso.week
        daily_exp["weekday"] = daily_exp["date"].dt.weekday
        daily_exp["weekday_name"] = daily_exp["date"].dt.day_name()

        fig_heat = px.density_heatmap(
            daily_exp,
            x="week",
            y="weekday_name",
            z="amount",
            facet_row="year",
            color_continuous_scale="Blues",
            title="Weekly calendar of daily spending (darker = higher spend)",
        )
        fig_heat.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor="rgba(15,23,42,1)",
            paper_bgcolor="rgba(15,23,42,1)",
            font_color="#e5e7eb",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

# ========== TAB 3: TRANSACTIONS ========== #
with tab_table:
    st.markdown("#### 📜 All transactions")

    df_display = base_df[["date", "description", "category", "amount"]].copy()
    df_display["amount"] = df_display["amount"].apply(fmt_money)
    df_display = df_display.rename(
        columns={
            "date": "Date",
            "description": "Description",
            "category": "Category",
            "amount": "Amount",
        }
    )
    st.dataframe(df_display, use_container_width=True, height=480)

    st.download_button(
        "⬇️ Download annotated CSV",
        base_df.to_csv(index=False).encode("utf-8"),
        "annotated_transactions.csv",
        mime="text/csv",
    )

# ========== SUBSCRIPTION DETECTOR ========== #
st.markdown("---")
st.subheader("🔁 Recurring subscriptions")

def detect_subscriptions(df: pd.DataFrame, min_occurrences: int = 3):
    """Detect merchants with approx monthly recurring charges."""
    subs = []
    expenses = df[df["amount"] < 0].copy()
    if expenses.empty:
        return pd.DataFrame()

    for desc, grp in expenses.groupby("description"):
        grp = grp.sort_values("date")
        if len(grp) < min_occurrences:
            continue
        diffs = grp["date"].diff().dt.days.dropna()
        if diffs.empty:
            continue
        median_gap = diffs.median()
        if 25 <= median_gap <= 35:
            subs.append(
                {
                    "description": desc,
                    "occurrences": len(grp),
                    "median_gap_days": float(median_gap),
                    "avg_amount": grp["amount"].mean(),
                }
            )
    if not subs:
        return pd.DataFrame()
    return pd.DataFrame(subs)

subs_df = detect_subscriptions(base_df)

if subs_df.empty:
    st.info("No clear monthly-style subscriptions detected.")
else:
    subs_df_display = subs_df.copy()
    subs_df_display["avg_amount"] = subs_df_display["avg_amount"].apply(fmt_money)
    subs_df_display = subs_df_display.rename(
        columns={
            "description": "Merchant",
            "occurrences": "Times charged",
            "median_gap_days": "Median gap (days)",
            "avg_amount": "Avg charge",
        }
    )
    st.dataframe(subs_df_display, use_container_width=True)

# ========== SMART SAVINGS RECOMMENDATIONS ========== #
st.markdown("---")
st.subheader("🧠 Smart savings recommendations")

recommendations = []

if base_income > 0 and base_spend > 0:
    saving_rate = 1 - (base_spend / base_income)
    if saving_rate < 0:
        recommendations.append(
            "Your net spending exceeds income — consider prioritizing debt reduction and cutting discretionary costs."
        )
    elif saving_rate < 0.1:
        recommendations.append(
            f"Your saving rate is around **{saving_rate:.0%}**, which is quite low. "
            "Try targeting at least 20% if possible."
        )
    elif saving_rate < 0.2:
        recommendations.append(
            f"Your saving rate is ~**{saving_rate:.0%}**. Good, but you might push it towards 25–30%."
        )
    else:
        recommendations.append(
            f"Nice! Your approximate saving rate is **{saving_rate:.0%}** — keep this up consistently."
        )

# Category-based tip
if "spend_df" in locals() and not spend_df.empty and base_spend > 0:
    top_cat = spend_df.iloc[0]
    share = (float(top_cat["amount"].replace(currency_symbol, "").replace(",", ""))
             if isinstance(top_cat["amount"], str)
             else top_cat["amount"]) / base_spend
    if share > 0.4:
        recommendations.append(
            f"**{top_cat['category']}** takes about **{share:.0%}** of your total spend. "
            "Consider setting a strict monthly cap for this category."
        )

# Subscriptions tip
if subs_df is not None and not subs_df.empty:
    approx_sub_monthly = -subs_df["avg_amount"].sum()
    if approx_sub_monthly > 0:
        recommendations.append(
            "You have recurring subscriptions. Canceling just 1–2 could save roughly "
            f"{fmt_money(approx_sub_monthly)} every month."
        )

# Comparison-based tip
if compare_df is not None:
    if base_spend > cmp_spend:
        recommendations.append(
            f"Spending increased vs **{compare_label}**. Look at categories that grew the most."
        )
    else:
        recommendations.append(
            f"Spending decreased compared to **{compare_label}** — nice progress, keep tracking monthly."
        )

if not recommendations:
    recommendations.append(
        "Your spending pattern looks fairly balanced. Keep tracking every month and adjust if income changes."
    )

for tip in recommendations:
    st.success(tip)






# ------------------ FOOTER ------------------ #
st.markdown(
    """
    <div class="footer">
        Made with ❤️ by <strong>Sateesh kumar</strong> · Personal Finance Analyzer · 2026
    </div>
    """,
    unsafe_allow_html=True,
)
