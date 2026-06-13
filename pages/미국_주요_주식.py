import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from datetime import datetime, timedelta

# ---------------------------------
# 페이지 설정
# ---------------------------------

st.set_page_config(
    page_title="🇺🇸 미국 주요 주식",
    page_icon="🚀",
    layout="wide"
)

# ---------------------------------
# 스타일
# ---------------------------------

st.markdown("""
<style>

.stApp{
    background: linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #111827
    );
}

.title{
    text-align:center;
    color:white;
    font-size:3rem;
    font-weight:bold;
}

.subtitle{
    text-align:center;
    color:#94a3b8;
}

div[data-testid="metric-container"]{
    background:#111827;
    border:1px solid #334155;
    border-radius:15px;
    padding:15px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="title">🇺🇸 미국 주요 주식 TOP10</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">최근 1년간 미국 대표 성장주 분석</div>',
    unsafe_allow_html=True
)

# ---------------------------------
# 종목 목록
# ---------------------------------

stocks = {
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Microsoft": "MSFT",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Broadcom": "AVGO",
    "AMD": "AMD",
    "Netflix": "NFLX"
}

# ---------------------------------
# 기간
# ---------------------------------

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# ---------------------------------
# 데이터 다운로드
# ---------------------------------

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

        except Exception:
            pass

    return df

prices = load_data()

if prices.empty:
    st.error("주가 데이터를 불러오지 못했습니다.")
    st.stop()

# ---------------------------------
# 성과 비교
# ---------------------------------

st.header("📊 최근 1년 성과 비교")

normalized = prices / prices.iloc[0] * 100

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
    title="미국 주요 주식 TOP10 성과 비교",
    xaxis_title="날짜",
    yaxis_title="지수 (시작=100)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------
# 수익률 계산
# ---------------------------------

returns = (
    (prices.iloc[-1] / prices.iloc[0]) - 1
) * 100

ranking = pd.DataFrame({
    "기업": returns.index,
    "수익률(%)": returns.values
})

ranking = ranking.sort_values(
    by="수익률(%)",
    ascending=False
)

# ---------------------------------
# TOP3
# ---------------------------------

st.header("🏆 TOP 3 수익률")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        f"🥇 {ranking.iloc[0]['기업']}",
        f"{ranking.iloc[0]['수익률(%)']:.2f}%"
    )

with col2:
    st.metric(
        f"🥈 {ranking.iloc[1]['기업']}",
        f"{ranking.iloc[1]['수익률(%)']:.2f}%"
    )

with col3:
    st.metric(
        f"🥉 {ranking.iloc[2]['기업']}",
        f"{ranking.iloc[2]['수익률(%)']:.2f}%"
    )

# ---------------------------------
# 수익률 표
# ---------------------------------

st.header("📈 수익률 순위")

st.dataframe(
    ranking,
    use_container_width=True
)

# ---------------------------------
# 수익률 막대그래프
# ---------------------------------

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
    template="plotly_dark",
    height=500,
    title="최근 1년 수익률 비교",
    xaxis_title="기업",
    yaxis_title="수익률 (%)"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ---------------------------------
# 상세 분석
# ---------------------------------

st.header("🔍 종목 상세 분석")

selected = st.selectbox(
    "분석할 기업 선택",
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
        name=selected,
        line=dict(width=3)
    )
)

fig3.update_layout(
    template="plotly_dark",
    height=550,
    title=f"{selected} 최근 1년 주가"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

current_price = float(stock_price.iloc[-1])
highest_price = float(stock_price.max())
lowest_price = float(stock_price.min())

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "💰 현재가",
        f"{current_price:,.2f}"
    )

with c2:
    st.metric(
        "📈 1년 최고가",
        f"{highest_price:,.2f}"
    )

with c3:
    st.metric(
        "📉 1년 최저가",
        f"{lowest_price:,.2f}"
    )

st.metric(
    "🚀 1년 수익률",
    f"{returns[selected]:.2f}%"
)

# ---------------------------------
# 투자 인사이트
# ---------------------------------

st.header("💡 투자 인사이트")

best_stock = ranking.iloc[0]["기업"]
best_return = ranking.iloc[0]["수익률(%)"]

worst_stock = ranking.iloc[-1]["기업"]
worst_return = ranking.iloc[-1]["수익률(%)"]

col1, col2 = st.columns(2)

with col1:
    st.success(
        f"""
🏆 최고 수익률

기업: {best_stock}

수익률: {best_return:.2f}%
"""
    )

with col2:
    st.warning(
        f"""
📉 최저 수익률

기업: {worst_stock}

수익률: {worst_return:.2f}%
"""
    )

st.markdown("---")

st.caption(
    "📊 Data Source: Yahoo Finance (yfinance)"
)
