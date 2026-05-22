import psycopg2
from shared.config import settings


def cleanup_old_data():
    conn = psycopg2.connect(settings.database_url)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM trading_signals WHERE news_id IN "
            "(SELECT id FROM news WHERE publish_time < NOW() - INTERVAL '%s days')",
            (str(settings.news_retention_days),),
        )
        cur.execute(
            "DELETE FROM news WHERE publish_time < NOW() - INTERVAL '%s days'",
            (str(settings.news_retention_days),),
        )
        cur.execute(
            "DELETE FROM policies WHERE publish_time < NOW() - INTERVAL '%s days'",
            (str(settings.policy_retention_days),),
        )
        deleted_news = cur.rowcount
    conn.commit()
    conn.close()
    print(f"Cleanup: removed old news and policies. News deletions: {deleted_news}")


def compute_market_snapshot():
    conn = psycopg2.connect(settings.database_url)
    with conn.cursor() as cur:
        for region in ("四川", "重庆"):
            cur.execute(
                """INSERT INTO market_snapshots (date, region, total_news_count, positive_ratio,
                   negative_ratio, avg_sentiment, buy_signal_count, sell_signal_count, top_news_ids)
                SELECT
                    CURRENT_DATE,
                    c.region,
                    COUNT(*) AS total,
                    COALESCE(SUM(CASE WHEN n.sentiment_label = 'positive' THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(*), 0), 0),
                    COALESCE(SUM(CASE WHEN n.sentiment_label = 'negative' THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(*), 0), 0),
                    COALESCE(AVG(n.sentiment_score), 0),
                    COALESCE(SUM(CASE WHEN n.trading_signal = 'buy' THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN n.trading_signal = 'sell' THEN 1 ELSE 0 END), 0),
                    ARRAY(SELECT n2.id FROM news n2 JOIN companies c2 ON n2.company_id = c2.id
                          WHERE c2.region = %s AND n2.publish_time::date = CURRENT_DATE
                          ORDER BY n2.confidence DESC NULLS LAST LIMIT 5)
                FROM news n
                JOIN companies c ON n.company_id = c.id
                WHERE c.region = %s AND n.publish_time::date = CURRENT_DATE
                ON CONFLICT (date, region) DO UPDATE SET
                    total_news_count = EXCLUDED.total_news_count,
                    positive_ratio = EXCLUDED.positive_ratio,
                    negative_ratio = EXCLUDED.negative_ratio,
                    avg_sentiment = EXCLUDED.avg_sentiment,
                    buy_signal_count = EXCLUDED.buy_signal_count,
                    sell_signal_count = EXCLUDED.sell_signal_count,
                    top_news_ids = EXCLUDED.top_news_ids""",
                (region, region),
            )
    conn.commit()
    conn.close()
    print("Market snapshot computed for both regions.")
