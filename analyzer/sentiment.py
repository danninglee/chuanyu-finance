import psycopg2
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from shared.config import settings

MODEL_NAME = "ProsusAI/finbert"
SENTIMENT_LABELS = ["positive", "negative", "neutral"]
SIGNAL_MAP = {
    "positive": "buy",
    "negative": "sell",
    "neutral": "hold",
}


class SentimentAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        self.model.eval()
        self.conn = psycopg2.connect(settings.database_url)

    def analyze(self, text: str) -> dict:
        """Run FinBERT inference. Returns {sentiment_label, sentiment_score, trading_signal, confidence}."""
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0]
            idx = torch.argmax(probs).item()
            score = probs[idx].item()

        label = SENTIMENT_LABELS[idx]
        signal = SIGNAL_MAP[label]
        return {
            "sentiment_label": label,
            "sentiment_score": round(score, 3),
            "trading_signal": signal,
            "confidence": round(score, 3),
        }

    def run(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, COALESCE(summary, ''), COALESCE(content, '') FROM news "
                "WHERE sentiment_label IS NULL ORDER BY publish_time DESC LIMIT 200"
            )
            rows = cur.fetchall()
            for news_id, summary, content in rows:
                text = (summary + " " + content)[:1000]
                if len(text.strip()) < 20:
                    continue
                try:
                    result = self.analyze(text)
                    cur.execute(
                        """UPDATE news SET
                           sentiment_label = %(sentiment_label)s,
                           sentiment_score = %(sentiment_score)s,
                           trading_signal = %(trading_signal)s,
                           confidence = %(confidence)s
                           WHERE id = %(id)s""",
                        {**result, "id": news_id},
                    )
                    cur.execute(
                        """INSERT INTO trading_signals (news_id, company_id, date, signal_type, signal_strength, reason)
                           VALUES (%(news_id)s, (SELECT company_id FROM news WHERE id = %(news_id)s),
                                   CURRENT_DATE, %(signal_type)s, %(signal_strength)s, 'FinBERT自动分析')
                           ON CONFLICT DO NOTHING""",
                        {"news_id": news_id, "signal_type": result["trading_signal"],
                         "signal_strength": result["confidence"]},
                    )
                    self.conn.commit()
                except Exception as e:
                    self.conn.rollback()
                    print(f"Sentiment analysis failed for news {news_id}: {e}")

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    analyzer.run()
    analyzer.close()
