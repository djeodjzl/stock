import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from datetime import datetime, timedelta

st.set_page_config(
    page_title="🇺🇸 미국 주요 주식",
    page_icon="🚀",
    layout="wide"
)

st.title("🇺🇸 미국 주요 주식 분석")

stocks = {
    "Tesla":"TSLA",
    "NVIDIA":"NVDA",
    "Microsoft":"MSFT",
    "Apple":"AAPL",
    "Amazon":"AMZN",
    "Alphabet":"GOOGL",
    "Meta":"META",
    "Broadcom":"AVGO",
    "AMD":"AMD",
    "Netflix":"NFLX"
}

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

@st.cache_data
def load_data():

    df = pd.DataFrame()

    for name, ticker in stocks.items():

        try:

            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False
            )

            if not data.empty:
                df[name] = data["Close"]

        except:
            pass

    return df

prices = load_data()

if prices.empty:
    st.error("데이터를 가져오지 못했습니다.")
    st.stop()

normalized = prices / prices.iloc[0] * 100

st.subheader("📊 최근 1년 성과 비교")

fig = go.Figure()

for company in normalized.columns:

    fig.add_trace(
        go.Scatter(
            x=normalized.index,
            y=normalized[company],
            mode="lines",
            name=company,
            line=dict(width=3)
        )
    )

fig.update_layout(
    template="plotly_dark",
    height=700,
    hovermode="x unified",
    title="미국 주요 주식 TOP10"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

returns = (
    (prices.iloc[-1] / prices.iloc[0]) - 1
) * 100

ranking = pd.DataFrame({
    "기업": returns.index,
    "수익률(%)": returns.values
})

ranking = ranking.sort_values(
    "수익률(%)",
    ascending=False
)

st.subheader("🏆 수익률 순위")

st.dataframe(
    ranking,
    use_container_width=True
)

col1,col2,col3 = st.columns(3)

with col1:
    st.metric(
        "🥇 1위",
        ranking.iloc[0]["기업"],
        f"{ranking.iloc[0]['수익률(%)']:.2f}%"
    )

with col2:
    st.metric(
        "🥈 2위",
        ranking.iloc[1]["기업"],
        f"{ranking.iloc[1]['수익률(%)']:.2f}%"
    )

with col3:
    st.metric(
        "🥉 3위",
        ranking.iloc[2]["기업"],
        f"{ranking.iloc[2]['수익률(%)']:.2f}%"
    )

st.subheader("🔍 기업 상세 분석")

selected = st.selectbox(
    "기업 선택",
    list(stocks.keys())
)

stock_price = prices[selected]

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=stock_price.index,
        y=stock_price,
        mode="lines",
        fill="tozeroy",
        name=selected,
        line=dict(width=3)
    )
)

fig2.update_layout(
    template="plotly_dark",
    height=500,
    title=f"{selected} 최근 1년 주가"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

c1,c2,c3 = st.columns(3)

with c1:
    st.metric(
        "현재가",
        f"{stock_price.iloc[-1]:.2f}"
    )

with c2:
    st.metric(
        "최고가",
        f"{stock_price.max():.2f}"
    )

with c3:
    st.metric(
        "최저가",
        f"{stock_price.min():.2f}"
    )
