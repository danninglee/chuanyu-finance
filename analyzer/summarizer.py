import json
import psycopg2
from datetime import datetime
from analyzer.backends import get_backend
from analyzer.prompt_templates import SUMMARIZE_PROMPT, POLICY_SUMMARIZE_PROMPT
from shared.config import settings


class Summarizer:
    def __init__(self):
        self.backend = get_backend()
        self.conn = psycopg2.connect(settings.database_url)

    def run(self):
        self._summarize_unprocessed_news()
        self._summarize_unprocessed_policies()
        self.conn.close()

    def _summarize_unprocessed_news(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, content FROM news "
                "WHERE summary IS NULL AND content != '' "
                "ORDER BY publish_time DESC LIMIT 100"
            )
            rows = cur.fetchall()
            for news_id, title, content in rows:
                try:
                    prompt = SUMMARIZE_PROMPT.format(title=title, content=content[:2000])
                    summary = self.backend.generate(prompt, max_tokens=200)
                    cur.execute(
                        "UPDATE news SET summary = %s WHERE id = %s",
                        (summary.strip(), news_id),
                    )
                    self.conn.commit()
                except Exception as e:
                    self.conn.rollback()
                    print(f"Summarize failed for news {news_id}: {e}")

    def _summarize_unprocessed_policies(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, content FROM policies "
                "WHERE summary IS NULL AND content != '' "
                "ORDER BY publish_time DESC LIMIT 50"
            )
            rows = cur.fetchall()
            for pol_id, title, content in rows:
                try:
                    prompt = POLICY_SUMMARIZE_PROMPT.format(title=title, content=content[:2000])
                    summary = self.backend.generate(prompt, max_tokens=300)
                    cur.execute(
                        "UPDATE policies SET summary = %s WHERE id = %s",
                        (summary.strip(), pol_id),
                    )
                    self.conn.commit()
                except Exception as e:
                    self.conn.rollback()
                    print(f"Summarize failed for policy {pol_id}: {e}")


if __name__ == "__main__":
    Summarizer().run()
