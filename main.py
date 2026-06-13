import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="📈 글로벌 주식 1년 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📈 최근 1년간 주요 기업 주가 분석")
st.markdown(
    """
삼성전자, SK하이닉스, 구글, 마이크로소프트, 애플의
최근 1년간 주가 변동을 비교합니다.
"""
)

# 티커
stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "구글": "GOOGL",
    "마이크로소프트": "MSFT",
    "애플": "AAPL"
}

# 기간
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

@st.cache_data
def load_data():
    df = pd.DataFrame()

    for name, ticker in stocks.items():
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False
        )

        if not data.empty:
            df[name] = data["Close"]

    return df

prices = load_data()

if prices.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

# -----------------------
# 정규화
# -----------------------

normalized = prices / prices.iloc[0] * 100

st.subheader("📊 주가 변동 비교 (시작일 = 100)")

fig = go.Figure()

for col in normalized.columns:
    fig.add_trace(
        go.Scatter(
            x=normalized.index,
            y=normalized[col],
            mode="lines",
            name=col,
            hovertemplate=
            "<b>%{fullData.name}</b><br>" +
            "날짜: %{x}<br>" +
            "지수: %{y:.2f}<extra></extra>"
        )
    )

fig.update_layout(
    height=650,
    template="plotly_dark",
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="주가 지수 (시작=100)",
    legend_title="기업"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# 수익률 계산
# -----------------------

returns = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100

st.subheader("🏆 최근 1년 수익률")

ranking = pd.DataFrame({
    "기업": returns.index,
    "수익률(%)": returns.values
}).sort_values(
    by="수익률(%)",
    ascending=False
)

st.dataframe(
    ranking,
    use_container_width=True
)

# -----------------------
# 막대 그래프
# -----------------------

fig2 = go.Figure()

fig2.add_trace(
    go.Bar(
        x=ranking["기업"],
        y=ranking["수익률(%)"],
        text=ranking["수익률(%)"].round(2),
        textposition="auto"
    )
)

fig2.update_layout(
    title="최근 1년 수익률 비교",
    template="plotly_dark",
    height=500,
    yaxis_title="수익률 (%)"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# 통계
# -----------------------

st.subheader("📌 핵심 분석")

best = ranking.iloc[0]
worst = ranking.iloc[-1]

col1, col2 = st.columns(2)

with col1:
    st.success(
        f"🥇 최고 수익률\n\n"
        f"{best['기업']}\n\n"
        f"{best['수익률(%)']:.2f}%"
    )

with col2:
    st.error(
        f"📉 최저 수익률\n\n"
        f"{worst['기업']}\n\n"
        f"{worst['수익률(%)']:.2f}%"
    )

# -----------------------
# 개별 기업 선택
# -----------------------

st.subheader("🔍 기업별 상세 분석")

selected = st.selectbox(
    "기업 선택",
    list(stocks.keys())
)

stock_price = prices[selected]

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=stock_price.index,
        y=stock_price,
        mode="lines",
        fill="tozeroy",
        name=selected
    )
)

fig3.update_layout(
    title=f"{selected} 최근 1년 주가",
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig3, use_container_width=True)

st.metric(
    "1년 수익률",
    f"{returns[selected]:.2f}%"
)

st.caption(
    "데이터 출처: Yahoo Finance (yfinance)"
)
