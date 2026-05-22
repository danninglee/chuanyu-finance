CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    full_name VARCHAR(200),
    region VARCHAR(10) NOT NULL CHECK (region IN ('四川', '重庆')),
    industry VARCHAR(50),
    market VARCHAR(20) CHECK (market IN ('主板', '中小板', '创业板', '科创板', '北交所')),
    listing_date DATE,
    registered_city VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_companies_region ON companies(region);
CREATE INDEX idx_companies_industry ON companies(industry);

-- News (30-day retention)
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    url VARCHAR(1000),
    source VARCHAR(50) NOT NULL CHECK (source IN ('东方财富', '巨潮资讯')),
    publish_time TIMESTAMP NOT NULL,
    crawl_time TIMESTAMP DEFAULT NOW(),
    simhash VARCHAR(64),
    summary TEXT,
    sentiment_score NUMERIC(4,3),
    sentiment_label VARCHAR(10) CHECK (sentiment_label IN ('positive', 'negative', 'neutral')),
    trading_signal VARCHAR(10) CHECK (trading_signal IN ('buy', 'hold', 'sell', 'none')),
    confidence NUMERIC(4,3),
    embedding vector(768),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_company ON news(company_id);
CREATE INDEX idx_news_publish_time ON news(publish_time DESC);
CREATE INDEX idx_news_simhash ON news(simhash);
CREATE INDEX idx_news_sentiment ON news(sentiment_label);

-- Policies (365-day retention)
CREATE TABLE policies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    summary TEXT,
    source_url VARCHAR(1000),
    source_name VARCHAR(100),
    publish_time TIMESTAMP NOT NULL,
    region VARCHAR(20) NOT NULL CHECK (region IN ('四川', '重庆', '全域')),
    category VARCHAR(50) CHECK (category IN ('产业', '金融', '税收', '土地', '环保', '其他')),
    industry_tags TEXT[],
    embedding vector(768),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_policies_region ON policies(region);
CREATE INDEX idx_policies_publish_time ON policies(publish_time DESC);
CREATE INDEX idx_policies_category ON policies(category);

-- Market snapshots
CREATE TABLE market_snapshots (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    region VARCHAR(10) NOT NULL,
    total_news_count INTEGER DEFAULT 0,
    positive_ratio NUMERIC(5,4) DEFAULT 0,
    negative_ratio NUMERIC(5,4) DEFAULT 0,
    avg_sentiment NUMERIC(4,3) DEFAULT 0,
    buy_signal_count INTEGER DEFAULT 0,
    sell_signal_count INTEGER DEFAULT 0,
    top_news_ids INTEGER[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, region)
);

CREATE INDEX idx_snapshots_date ON market_snapshots(date DESC);

-- Trading signals
CREATE TABLE trading_signals (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES news(id) ON DELETE CASCADE,
    company_id INTEGER REFERENCES companies(id),
    date DATE NOT NULL,
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('buy', 'hold', 'sell', 'none')),
    signal_strength NUMERIC(4,3),
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_signals_company_date ON trading_signals(company_id, date DESC);
