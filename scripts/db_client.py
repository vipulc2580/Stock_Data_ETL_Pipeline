from .config_loader import config
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from scripts.logger import logger


DB_USER = config("POSTGRES_USER")
DB_PASS = config("POSTGRES_PASSWORD")
DB_NAME = config("POSTGRES_DB")
DB_HOST = config("POSTGRES_HOST", "postgres")  # service name in docker-compose
DB_PORT = config("POSTGRES_PORT", "5432")

def get_connection():
    return psycopg2.connect(
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

def upsert_stock_data(rows):
    """
    rows: list of tuples (symbol, timestamp, open, high, low, close, volume)
    """
    query = """
        INSERT INTO stock_data (symbol, timestamp, open_price, high_price, low_price, close_price, volume)
        VALUES %s
        ON CONFLICT (symbol, timestamp)
        DO UPDATE SET
            open_price = EXCLUDED.open_price,
            high_price = EXCLUDED.high_price,
            low_price = EXCLUDED.low_price,
            close_price = EXCLUDED.close_price,
            volume = EXCLUDED.volume;
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                execute_values(cur, query, rows)
            conn.commit()
        
        # Log successful upsert
        symbols = list(set(row[0] for row in rows))  # unique symbols
        logger.log_event(
            f"Upserted {len(rows)} stock data records for {len(symbols)} symbols",
            "INFO",
            {
                "operation": "upsert_stock_data",
                "record_count": len(rows),
                "symbol_count": len(symbols),
                "symbols":str(symbols)
            }
        )
    except Exception as e:
        logger.log_event(
            f"Failed to upsert stock data: {str(e)}",
            "ERROR",
            {
                "operation": "upsert_stock_data",
                "record_count": len(rows),
                "error_type": type(e).__name__
            }
        )
        raise

def update_ticker_status(symbol, status):
    query = """
        UPDATE tickers
        SET last_status = %s,
            last_fetched = NOW()
        WHERE symbol = %s;
    """
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (status, symbol))
                rows_affected = cur.rowcount
            conn.commit()
        
        # Log status update
        logger.log_event(
            f"Updated ticker status for {symbol} to {status}",
            "INFO",
            {
                "operation": "update_ticker_status",
                "symbol": symbol,
                "status": status,
                "rows_affected": rows_affected
            }
        )
        
    except Exception as e:
        logger.log_event(
            f"Failed to update ticker status for {symbol}: {str(e)}",
            "ERROR",
            {
                "operation": "update_ticker_status",
                "symbol": symbol,
                "status": status,
                "error_type": type(e).__name__
            }
        )
        raise

def get_symbols_to_fetch():
    query = """
        SELECT symbol FROM tickers
        WHERE is_active = TRUE
          AND (
            last_fetched IS NULL
            OR last_fetched < %s
            OR last_status = 'failed'
          );
    """
    yesterday = datetime.now() - timedelta(days=1)
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (yesterday,))
                rows = cur.fetchall()
        
        symbols = [row[0] for row in rows]
        
        # Log the query result
        logger.log_event(
            f"Retrieved {len(symbols)} symbols to fetch",
            "INFO",
            {
                "operation": "get_symbols_to_fetch",
                "symbol_count": len(symbols),
                "query_date_threshold": yesterday.isoformat(),
                "symbols":str(symbols)
            }
        )
        
        return symbols
        
    except Exception as e:
        logger.log_event(
            f"Failed to get symbols to fetch: {str(e)}",
            "ERROR",
            {
                "operation": "get_symbols_to_fetch",
                "error_type": type(e).__name__
            }
        )
        raise