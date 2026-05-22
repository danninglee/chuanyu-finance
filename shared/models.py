from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Company(BaseModel):
    id: Optional[int] = None
    code: str = Field(min_length=6, max_length=6)
    name: str
    full_name: Optional[str] = None
    region: str  # 四川 | 重庆
    industry: Optional[str] = None
    market: Optional[str] = None  # 主板 | 中小板 | 创业板 | 科创板 | 北交所
    listing_date: Optional[date] = None
    registered_city: Optional[str] = None


class NewsItem(BaseModel):
    id: Optional[int] = None
    company_id: Optional[int] = None
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    source: str  # 东方财富 | 巨潮资讯
    publish_time: datetime
    crawl_time: Optional[datetime] = None
    simhash: Optional[str] = None
    summary: Optional[str] = None
    sentiment_score: Optional[Decimal] = None
    sentiment_label: Optional[str] = None  # positive | negative | neutral
    trading_signal: Optional[str] = None  # buy | hold | sell | none
    confidence: Optional[Decimal] = None


class PolicyItem(BaseModel):
    id: Optional[int] = None
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    publish_time: datetime
    region: str  # 四川 | 重庆 | 全域
    category: Optional[str] = None
    industry_tags: Optional[list[str]] = None


class MarketSnapshot(BaseModel):
    id: Optional[int] = None
    date: date
    region: str
    total_news_count: int = 0
    positive_ratio: Decimal = Decimal("0")
    negative_ratio: Decimal = Decimal("0")
    avg_sentiment: Decimal = Decimal("0")
    buy_signal_count: int = 0
    sell_signal_count: int = 0
    top_news_ids: list[int] = []


class TradingSignal(BaseModel):
    id: Optional[int] = None
    news_id: int
    company_id: int
    date: date
    signal_type: str
    signal_strength: Optional[Decimal] = None
    reason: Optional[str] = None


class AnalysisResult(BaseModel):
    summary: str
    sentiment_label: str
    sentiment_score: float
    trading_signal: str
    confidence: float
