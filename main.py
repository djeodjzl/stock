import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from datetime import datetime, timedelta

# --------------------------------
# 페이지 설정
# --------------------------------

st.set_page_config(
    page_title="📈 글로벌 주식 분석기",
    page_icon="📊",
    layout="wide"
)

# --------------------------------
# CSS
# --------------------------------

st.markdown("""
<style>

.stApp{
    background:
    linear-gradient(
    135deg,
    #0f172a,
    #111827,
    #020617
    );
}

.main-title{
    text-align:center;
    font-size:3rem;
    font-weight:bold;
    color:white;
}

.sub-title{
    text-align:center;
    color:#94a3b8;
}

div[data-testid="metric-container"]{
    background:#111827;
    border:1px solid #334155;
    padding:20px;
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">📈 글로벌 주식 분석기</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Yahoo Finance 기반 주가 분석</div>',
    unsafe_allow_html=True
)

# --------------------------------
# 사이드바
# --------------------------------

page = st.sidebar.radio(
    "📂 페이지 선택",
    [
        "대표 5종목",
        "미국 빅테크 TOP10"
    ]
)

# --------------------------------
# 기간
# --------------------------------

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# --------------------------------
# 대표 5종목
# --------------------------------

stocks_5 = {
    "삼성전자":"005930.KS",
    "SK하이닉스":"000660.KS",
    "구글":"GOOGL",
    "마이크로소프트":"MSFT",
    "애플":"AAPL"
}

# --------------------------------
# 미국 TOP10
# --------------------------------

stocks_us = {
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

# --------------------------------
# 데이터 로드
# --------------------------------

@st.cache_data
def load_data(stock_dict):

    df = pd.DataFrame()

    for name, ticker in stock_dict.items():

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

# --------------------------------
# 공통 분석 함수
# --------------------------------

def analyze_market(title, stock_dict):

    st.header(title)

    prices = load_data(stock_dict)

    if prices.empty:
        st.error("데이터를 가져올 수 없습니다.")
        return

    normalized = prices / prices.iloc[0] * 100

    fig = go.Figure()

    for col in normalized.columns:

        fig.add_trace(
            go.Scatter(
                x=normalized.index,
                y=normalized[col],
                mode="lines",
                name=col,
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

    st.subheader("🏆 수익률 순위")

    st.dataframe(
        ranking,
        use_container_width=True
    )

    best = ranking.iloc[0]
    second = ranking.iloc[1]
    third = ranking.iloc[2]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            f"🥇 {best['기업']}",
            f"{best['수익률(%)']:.2f}%"
        )

    with col2:
        st.metric(
            f"🥈 {second['기업']}",
            f"{second['수익률(%)']:.2f}%"
        )

    with col3:
        st.metric(
            f"🥉 {third['기업']}",
            f"{third['수익률(%)']:.2f}%"
        )
            # -----------------------------
    # 수익률 막대그래프
    # -----------------------------

    st.subheader("📊 수익률 비교")

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
        xaxis_title="기업",
        yaxis_title="수익률 (%)",
        title="최근 1년 수익률"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -----------------------------
    # 종목 상세 분석
    # -----------------------------

    st.subheader("🔍 종목 상세 분석")

    selected = st.selectbox(
        "분석할 기업 선택",
        list(stock_dict.keys()),
        key=title
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

    current_price = float(stock_price.iloc[-1])
    highest_price = float(stock_price.max())
    lowest_price = float(stock_price.min())

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "💰 현재 가격",
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

    st.caption(
        "데이터 출처: Yahoo Finance (yfinance)"
    )

# --------------------------------
# 페이지 실행
# --------------------------------

if page == "대표 5종목":

    analyze_market(
        "📈 삼성전자 · SK하이닉스 · 구글 · MS · 애플",
        stocks_5
    )

elif page == "미국 빅테크 TOP10":

    analyze_market(
        "🚀 미국 빅테크 TOP10",
        stocks_us
    )

# --------------------------------
# 푸터
# --------------------------------

st.markdown("---")

st.markdown(
    """
    <center>
    <h4>📊 글로벌 주식 분석기</h4>
    <p>최근 1년 주가 데이터 자동 분석</p>
    </center>
    """,
    unsafe_allow_html=True
)
