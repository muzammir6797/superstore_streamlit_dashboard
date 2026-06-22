import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Superstore Dashborad",
    page_icon="📊",
    layout='wide'
)
df=pd.read_csv(r'superstore_cleaned.csv')
df['order_date']=pd.to_datetime(df['order_date'])

with st.sidebar:
    st.header("Filters")
    st.caption("Adjust filters than click Apply")
    with st.form("filter_form", clear_on_submit=False):
        
        regions = st.multiselect(
            "Region",
            options=df['region'].unique(),
            default=df['region'].unique()
        )
        order_year = df["order_date"].dt.year
        years = st.multiselect(
            "Year",
            options=sorted(order_year.unique()),
            default=sorted(order_year.unique())
        )
        shipping = st.multiselect(
            "Ship Mode",
            options=df['ship_mode'].unique(),
            default=df['ship_mode'].unique()
        )
        segment = st.multiselect(
            "Segment",
            options=df['segment'].unique(),
            default=df['segment'].unique()
        )
        st.form_submit_button("Apply")

filtered=df[
    (df["region"].isin(regions))
    & (order_year.isin(years))
    & (df["ship_mode"].isin(shipping))
    & (df["segment"].isin(segment))
]

st.title("📊 Superstore Sales Dashboard")
col1,col2,col3,col4=st.columns(4)

with col1:
    st.metric(
        "Total Sales",
        f"${filtered['sales_price'].sum():,.0f}"
    )
with col2:
    st.metric(
        "Total Profit",
        f"${filtered['profit'].sum():,.0f}"
    )
with col3:
    st.metric(
        "Average Discount",
        f"{filtered['discount(%)'].mean():.2%}"
    )
with col4:
    st.metric(
        " Order",
        f"{filtered['order_id'].nunique():,}"
    )
tab1,tab2,tab3 ,tab4=st.tabs(
    ["Overview","BY Category","By Region","Quality Alerts"]
)

with tab1:
    
    with st.expander("View Row Data"):
        
        st.dataframe(
        df.head(20),
        use_container_width=True
    )
    st.header("monthly sales by year")
    df['order_year']=df['order_date'].dt.year
    df['month']=df.order_date.dt.to_period("M").astype(str)
    monthly_yr=df.groupby(["month", "order_year"])["sales_price"].sum().reset_index()
    monthly_yr_fig=px.line(monthly_yr,x="month",y="sales_price",color="order_year")
    st.plotly_chart(monthly_yr_fig)
    st.download_button(
        label="Download Filtered Data",
        data=filtered.to_csv(index=False).encode('utf-8'),
        file_name='filtered_data.csv',
        mime='text/csv'
    )

with tab2:
    col1,col2=st.columns(2)
    with col1:
       st.header("top 10 sub_category by sales")
       top_10_sub_category=df.groupby("sub_category")['sales_price'].sum().nlargest(10).reset_index()
       cat_plot=top_10_sub_category.plot(x="sub_category",y="sales_price",kind="barh")
       st.pyplot(cat_plot.figure)
    with col2:
        st.header("sales vs profit")
        scatter_fig = px.scatter(df,x="sales_price",y="profit",color="category")
        st.plotly_chart(scatter_fig)




with tab3:
    st.subheader("Sales by Region")
    region_profit = (
        filtered.groupby("region")["profit"]
        .sum()
        .reset_index()
    )
    fig = px.pie(
        region_profit,
        names="region",
        values="profit",
        hole=0.4,
        title="Region Share of Total Profit"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:

    st.header("Quality Alerts")

    #Profit Margin Alert
    profit_margin = np.mean(
        (filtered["profit"] / filtered["sales_price"]) * 100
    )

    if profit_margin > 20:
        st.success(
            f"🟢 Healthy profit margin: {profit_margin:.1f}%"
        )

    elif profit_margin >= 10:
        st.warning(
            f"🟡 Moderate profit margin: {profit_margin:.1f}%"
       )

    else:
        st.error(
            f"🔴 Low profit margin: {profit_margin:.1f}%"
        )

    # 75th Percentile Discount Alert
    p75 = filtered["discount(%)"].quantile(0.75)

    high_discount_orders = (
        filtered["discount(%)"] > p75
    ).sum()

    st.info(
        f"ℹ️ {high_discount_orders} orders above the 75th percentile discount"
    )

    # Sales Outlier Alert using Z-Score
    z_score = (
        (filtered["sales_price"] - filtered["sales_price"].mean())
        / filtered["sales_price"].std()
    )

    outliers = filtered[abs(z_score) > 2]

    st.warning(
        f"⚠️ {len(outliers)} sales outliers detected (|z| > 2)"
    )


with st.expander("View Outlier Rows"):

    st.dataframe(
        outliers[
            [
                "order_id",
                "order_date",
                "sales_price",
                "profit",
                "region"
            ]
        ],
        use_container_width=True
    )