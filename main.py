import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from datetime import datetime, timedelta

# ---------------------------------
# 페이지 설정
# ---------------------------------

st.set_page_config(
    page_title="📈 글로벌 주식 분석기",
    page_icon="📊",
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
        #0f172a,
        #111827,
        #020617
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
    '<div class="title">📈 글로벌 주식 분석기</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">최근 1년간 주요 기업 주가 비교</div>',
    unsafe_allow_html=True
)

# ---------------------------------
# 종목 목록
# ---------------------------------

stocks = {
    "삼성전자":"005930.KS",
    "SK하이닉스":"000660.KS",
    "구글":"GOOGL",
    "마이크로소프트":"MSFT",
    "애플":"AAPL"
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

        except:
            pass

    return df

prices = load_data()

if prices.empty:
    st.error("데이터를 가져오지 못했습니다.")
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
    hovermode="x unified",
    height=650,
    title="최근 1년 성과 비교",
    xaxis_title="날짜",
    yaxis_title="지수 (시작=100)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------
# 수익률
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

st.header("🏆 수익률 순위")

st.dataframe(
    ranking,
    use_container_width=True
)

# ---------------------------------
# TOP3
# ---------------------------------

col1, col2, col3 = st.columns(3)

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

# ---------------------------------
# 막대 그래프
# ---------------------------------

st.header("📈 수익률 비교")

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
    title="최근 1년 수익률"
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
        name=selected,
        line=dict(width=3)
    )
)

fig3.update_layout(
    template="plotly_dark",
    height=500,
    title=f"{selected} 최근 1년 주가"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💰 현재가",
        f"{stock_price.iloc[-1]:,.2f}"
    )

with col2:
    st.metric(
        "📈 최고가",
        f"{stock_price.max():,.2f}"
    )

with col3:
    st.metric(
        "📉 최저가",
        f"{stock_price.min():,.2f}"
    )

st.metric(
    "🚀 1년 수익률",
    f"{returns[selected]:.2f}%"
)

st.markdown("---")

st.info(
    "🇺🇸 미국 주요 주식 분석은 왼쪽 사이드바의 페이지 메뉴에서 확인하세요."
)

st.caption(
    "데이터 출처: Yahoo Finance (yfinance)"
)
