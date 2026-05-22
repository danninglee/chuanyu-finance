import altair as alt
import pandas as pd


def sentiment_trend_chart(df: pd.DataFrame) -> alt.Chart:
    """Line chart: sentiment trend by region over time."""
    base = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("date:T", title="日期"),
        y=alt.Y("avg_sentiment:Q", title="平均情绪分"),
        color=alt.Color("region:N", title="地区",
                        scale=alt.Scale(domain=["四川", "重庆"], range=["#d62728", "#1f77b4"])),
        tooltip=["date:T", "region:N", "avg_sentiment:Q"],
    ).properties(height=300)
    return base


def industry_bar_chart(df: pd.DataFrame) -> alt.Chart:
    """Horizontal bar chart: news count by industry."""
    bar = alt.Chart(df).mark_bar().encode(
        x=alt.X("news_count:Q", title="新闻数量"),
        y=alt.Y("industry:N", sort="-x", title="行业"),
        color=alt.Color("news_count:Q", scale=alt.Scale(scheme="reds")),
        tooltip=["industry:N", "news_count:Q"],
    ).properties(height=350)
    return bar


def company_sentiment_score_chart(df: pd.DataFrame) -> alt.Chart:
    """Scatter + line: company sentiment score over time."""
    if df.empty:
        return alt.Chart(pd.DataFrame({"text": ["暂无数据"]})).mark_text().encode(text="text:N")
    chart = alt.Chart(df).mark_circle(size=80).encode(
        x=alt.X("date:T", title="日期"),
        y=alt.Y("avg_score:Q", title="情绪分",
                scale=alt.Scale(domain=[-1, 1])),
        color=alt.Color("sentiment_label:N",
                        scale=alt.Scale(domain=["positive", "negative", "neutral"],
                                        range=["#2ca02c", "#d62728", "#7f7f7f"])),
        size="count:Q",
        tooltip=["date:T", "sentiment_label:N", "avg_score:Q", "count:Q"],
    ).properties(height=300)
    return chart
