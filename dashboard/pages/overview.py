import streamlit as st
from dashboard.components.database import (
    get_today_summary, get_sentiment_trend, get_top_news, get_industry_distribution,
)
from dashboard.components.charts import sentiment_trend_chart, industry_bar_chart


def show():
    st.title("川渝上市公司金融舆情分析")
    st.caption(f"数据来源: 东方财富 + 巨潮资讯 | 更新时间: 每个交易日16:00")

    # KPI cards
    sichuan = get_today_summary("四川")
    chongqing = get_today_summary("重庆")

    col1, col2, col3, col4 = st.columns(4)
    total_news = sichuan["total_news_count"] + chongqing["total_news_count"]
    total_pos = (
        sichuan["total_news_count"] * sichuan["positive_ratio"]
        + chongqing["total_news_count"] * chongqing["positive_ratio"]
    )
    avg_pos = (total_pos / total_news * 100) if total_news > 0 else 0
    avg_sent = (
        (sichuan["avg_sentiment"] + chongqing["avg_sentiment"]) / 2
        if sichuan["total_news_count"] + chongqing["total_news_count"] > 0 else 0
    )
    total_buy = sichuan["buy_signal_count"] + chongqing["buy_signal_count"]

    col1.metric("今日新闻", f"{total_news} 篇")
    col2.metric("正面占比", f"{avg_pos:.1f}%")
    col3.metric("平均情绪分", f"{avg_sent:.3f}" if avg_sent else "N/A")
    col4.metric("买入信号", f"{total_buy} 只")

    # Sentiment trend
    st.subheader("近7日川渝情绪趋势")
    trend_df = get_sentiment_trend(7)
    if not trend_df.empty:
        st.altair_chart(sentiment_trend_chart(trend_df), use_container_width=True)
    else:
        st.info("暂无趋势数据")

    # Top news and industry side by side
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("今日重大新闻")
        top_df = get_top_news(10)
        if not top_df.empty:
            for _, row in top_df.iterrows():
                emoji = {"positive": "\U0001f7e2", "negative": "\U0001f534", "neutral": "⚪"}.get(
                    row.get("sentiment_label"), ""
                )
                signal = row.get("trading_signal", "none")
                signal_text = {"buy": "买入", "sell": "卖出", "hold": "持有", "none": "无"}.get(signal, signal)
                with st.expander(f"{emoji} [{row['company_name']}({row['code']})] {row['title'][:60]}"):
                    st.write(row.get("summary", "暂无摘要"))
                    st.caption(f"信号: {signal_text} | 置信度: {row.get('confidence', 0):.2%}")
        else:
            st.info("暂无今日新闻")

    with col_right:
        st.subheader("行业热度")
        ind_df = get_industry_distribution()
        if not ind_df.empty:
            st.altair_chart(industry_bar_chart(ind_df.head(20)), use_container_width=True)
        else:
            st.info("暂无行业数据")
