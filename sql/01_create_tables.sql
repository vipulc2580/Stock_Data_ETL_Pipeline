CREATE TABLE tickers (
    symbol VARCHAR(20) PRIMARY KEY,
    exchange VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    last_fetched TIMESTAMP,
    last_status VARCHAR(20)
);

CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    volume BIGINT,
    created_at TIMESTAMP DEFAULT now(),
    UNIQUE(symbol, timestamp)
);

CREATE TABLE market_calendar (
    date DATE PRIMARY KEY,
    exchange VARCHAR(10),
    is_holiday BOOLEAN DEFAULT TRUE
);

CREATE TABLE bad_payloads (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    payload JSONB,
    error TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE pipeline_run_stats (
    run_id UUID PRIMARY KEY,
    run_date TIMESTAMP DEFAULT now(),
    tickers_processed INT,
    success_count INT,
    fail_count INT
);
