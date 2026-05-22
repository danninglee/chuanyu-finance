import streamlit as st
from dashboard.components.database import (
    get_company_list, get_company_sentiment_trend, get_company_news, get_company_policies,
)
from dashboard.components.charts import company_sentiment_score_chart


def show():
    st.title("公司详情")

    companies_df = get_company_list()
    if companies_df.empty:
        st.warning("暂无公司数据，请先运行公司列表初始化脚本。")
        return

    company_options = companies_df.apply(
        lambda r: f"{r['code']} - {r['name']} ({r['region']})", axis=1
    ).tolist()
    selected = st.selectbox("搜索并选择公司", company_options)

    if selected:
        code = selected.split(" - ")[0]
        company_row = companies_df[companies_df["code"] == code].iloc[0]
        company_id = int(company_row["id"])

        st.subheader(f"{company_row['name']} ({code})")
        st.caption(f"地区: {company_row['region']} | 行业: {company_row['industry']}")

        # Sentiment trend
        st.subheader("近30日情绪走势")
        trend_df = get_company_sentiment_trend(company_id, 30)
        st.altair_chart(company_sentiment_score_chart(trend_df), use_container_width=True)

        # News table
        st.subheader("近7日新闻")
        news_df = get_company_news(company_id, 7)
        if not news_df.empty:
            for _, row in news_df.iterrows():
                emoji = {"positive": "\U0001f7e2", "negative": "\U0001f534", "neutral": "⚪"}.get(
                    row.get("sentiment_label"), ""
                )
                signal = row.get("trading_signal", "none")
                signal_map = {"buy": "买入", "sell": "卖出", "hold": "持有", "none": "无"}
                with st.expander(
                    f"{emoji} [{row['publish_time'].strftime('%m-%d')}] {row['title'][:60]} "
                    f"| {signal_map.get(signal, signal)} ({(row.get('confidence') or 0):.0%})"
                ):
                    st.write(row.get("summary") or row.get("content", "暂无内容")[:500])
        else:
            st.info("近7日暂无新闻")

        # Related policies
        st.subheader("相关川渝政策")
        policy_df = get_company_policies(company_id)
        if not policy_df.empty:
            for _, row in policy_df.iterrows():
                with st.expander(f"[{row['category']}] {row['title'][:60]}"):
                    st.write(row.get("summary", "暂无摘要"))
                    st.caption(f"来源: {row.get('source_name', '')} | {row['publish_time']}")
        else:
            st.info("暂无相关行业政策")
