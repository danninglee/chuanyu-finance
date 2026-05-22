import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import date, timedelta
from shared.config import settings


def get_connection():
    return psycopg2.connect(settings.database_url)


def get_today_summary(region: str | None = None) -> dict:
    conn = get_connection()
    if region:
        query = """
            SELECT total_news_count, positive_ratio, negative_ratio, avg_sentiment,
                   buy_signal_count, sell_signal_count, top_news_ids
            FROM market_snapshots
            WHERE date = CURRENT_DATE AND region = %s
            ORDER BY date DESC LIMIT 1
        """
        df = pd.read_sql(query, conn, params=(region,))
    else:
        query = """
            SELECT total_news_count, positive_ratio, negative_ratio, avg_sentiment,
                   buy_signal_count, sell_signal_count, top_news_ids
            FROM market_snapshots
            WHERE date = CURRENT_DATE
            ORDER BY date DESC LIMIT 1
        """
        df = pd.read_sql(query, conn)
    conn.close()
    if df.empty:
        return {
            "total_news_count": 0, "positive_ratio": 0.0, "negative_ratio": 0.0,
            "avg_sentiment": 0.0, "buy_signal_count": 0, "sell_signal_count": 0,
        }
    row = df.iloc[0].to_dict()
    row["positive_ratio"] = float(row["positive_ratio"])
    row["negative_ratio"] = float(row["negative_ratio"])
    row["avg_sentiment"] = float(row["avg_sentiment"])
    return row


def get_sentiment_trend(days: int = 7) -> pd.DataFrame:
    conn = get_connection()
    query = f"""
        SELECT date, region, avg_sentiment
        FROM market_snapshots
        WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_top_news(limit: int = 10) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT n.id, n.title, n.summary, n.sentiment_label, n.trading_signal,
               n.confidence, n.publish_time, c.name AS company_name, c.region, c.code
        FROM news n
        JOIN companies c ON n.company_id = c.id
        WHERE n.publish_time::date = CURRENT_DATE
        ORDER BY n.confidence DESC NULLS LAST
        LIMIT %s
    """
    df = pd.read_sql(query, conn, params=(limit,))
    conn.close()
    return df


def get_industry_distribution() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT c.industry, COUNT(*) AS news_count
        FROM news n
        JOIN companies c ON n.company_id = c.id
        WHERE n.publish_time::date = CURRENT_DATE
        GROUP BY c.industry
        ORDER BY news_count DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_company_list() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT id, code, name, region, industry FROM companies ORDER BY code", conn)
    conn.close()
    return df


def get_company_sentiment_trend(company_id: int, days: int = 30) -> pd.DataFrame:
    conn = get_connection()
    query = f"""
        SELECT publish_time::date AS date, sentiment_label,
               COUNT(*) AS count, AVG(sentiment_score) AS avg_score
        FROM news
        WHERE company_id = %s AND publish_time >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY publish_time::date, sentiment_label
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn, params=(company_id,))
    conn.close()
    return df


def get_company_news(company_id: int, days: int = 7) -> pd.DataFrame:
    conn = get_connection()
    query = f"""
        SELECT id, title, content, summary, sentiment_label, trading_signal,
               confidence, publish_time, source
        FROM news
        WHERE company_id = %s AND publish_time >= CURRENT_DATE - INTERVAL '{days} days'
        ORDER BY publish_time DESC
        LIMIT 50
    """
    df = pd.read_sql(query, conn, params=(company_id,))
    conn.close()
    return df


def get_company_policies(company_id: int) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT p.title, p.summary, p.category, p.publish_time, p.source_name
        FROM policies p
        JOIN companies c ON c.industry = ANY(p.industry_tags)
        WHERE c.id = %s
        ORDER BY p.publish_time DESC
        LIMIT 10
    """
    df = pd.read_sql(query, conn, params=(company_id,))
    conn.close()
    return df
