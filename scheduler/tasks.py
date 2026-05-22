from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, time
from scheduler.cleanup import cleanup_old_data, compute_market_snapshot
from shared.config import settings


scheduler = BlockingScheduler()


@scheduler.scheduled_job("cron", day_of_week="mon-fri", hour=16, minute=0)
def daily_crawl_job():
    print(f"[{datetime.now()}] Starting daily crawl and analysis pipeline...")
    import subprocess
    subprocess.run(["scrapy", "runspider", "/app/crawler/spiders/eastmoney.py"], cwd="/app")
    subprocess.run(["scrapy", "runspider", "/app/crawler/spiders/juchao.py"], cwd="/app")
    print(f"[{datetime.now()}] Crawl complete. Running analysis...")
    from analyzer.summarizer import Summarizer
    Summarizer().run()
    from analyzer.sentiment import SentimentAnalyzer
    SentimentAnalyzer().run()
    print(f"[{datetime.now()}] Analysis complete. Computing snapshot...")
    compute_market_snapshot()
    print(f"[{datetime.now()}] Daily pipeline complete.")


@scheduler.scheduled_job("cron", hour=2, minute=0)
def nightly_cleanup_job():
    print(f"[{datetime.now()}] Running nightly cleanup...")
    cleanup_old_data()
    print(f"[{datetime.now()}] Cleanup complete.")


@scheduler.scheduled_job("cron", hour=8, minute=0)
def morning_policy_crawl_job():
    print(f"[{datetime.now()}] Crawling policy updates...")
    import subprocess
    subprocess.run(["scrapy", "runspider", "/app/crawler/spiders/policy_spider.py"], cwd="/app")
    print(f"[{datetime.now()}] Policy crawl complete.")


if __name__ == "__main__":
    print(f"Scheduler started. Daily crawl at {settings.schedule_time} on trading days.")
    scheduler.start()
