import psycopg2
from shared.config import settings


class PostgresPipeline:
    def open_spider(self, spider):
        self.conn = psycopg2.connect(settings.database_url)

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        with self.conn.cursor() as cur:
            spider_name = spider.name
            if spider_name in ("eastmoney", "juchao"):
                self._insert_news(cur, item)
            elif spider_name == "policy":
                self._insert_policy(cur, item)
        self.conn.commit()
        return item

    def _insert_news(self, cur, item):
        cur.execute("SELECT id FROM companies WHERE code = %s", (item["code"],))
        row = cur.fetchone()
        if not row:
            return
        company_id = row[0]

        cur.execute("SELECT id FROM news WHERE simhash = %s LIMIT 1", (item["simhash"],))
        if cur.fetchone():
            return

        cur.execute(
            """INSERT INTO news (company_id, title, content, url, source, publish_time, crawl_time, simhash)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT DO NOTHING""",
            (
                company_id, item["title"], item.get("content", ""),
                item.get("url", ""), item["source"], item["publish_time"],
                item["crawl_time"], item["simhash"],
            ),
        )

    def _insert_policy(self, cur, item):
        cur.execute(
            """INSERT INTO policies (title, content, source_url, source_name, publish_time, region, category, industry_tags)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT DO NOTHING""",
            (
                item["title"], item.get("content", ""), item.get("source_url", ""),
                item.get("source_name", ""), item["publish_time"],
                item["region"], item.get("category", "其他"), item.get("industry_tags", []),
            ),
        )
