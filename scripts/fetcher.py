import asyncio
import aiohttp
from typing import List
from scripts.models import StockData
from scripts.db_client import upsert_stock_data, update_ticker_status
from scripts.email_alerts import send_email
from .config_loader import config
from scripts.logger import logger 
import time 

API_KEY = config("ALPHAVANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

CONCURRENCY = int(config("CONCURRENCY", "10"))

async def fetch_symbol(session, symbol):
    start_time = time.time()
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize":"compact",
        "apikey": API_KEY
    }
    try:
        async with session.get(BASE_URL, params=params, timeout=30) as resp:
            data = await resp.json()
            if "Time Series (Daily)" not in data:
                raise ValueError(f"Unexpected API response for {symbol}")
            rows = []
            for date_str, ohlcv in data["Time Series (Daily)"].items():
                stock = StockData(
                    symbol=symbol,
                    timestamp=date_str,
                    open_price=float(ohlcv["1. open"]),
                    high_price=float(ohlcv["2. high"]),
                    low_price=float(ohlcv["3. low"]),
                    close_price=float(ohlcv["4. close"]),
                    volume=int(ohlcv["5. volume"])
                )
                rows.append((
                    stock.symbol,
                    stock.timestamp,
                    stock.open_price,
                    stock.high_price,
                    stock.low_price,
                    stock.close_price,
                    stock.volume
                ))
                # this is to make sure we take only today's data
                break
            upsert_stock_data(rows)
            update_ticker_status(symbol, "success")
            duration_ms = int((time.time() - start_time) * 1000)
            logger.log_event(
                f"Successfully fetched stock data for {symbol}",
                "INFO",
                {
                    "operation": "fetch_symbol",
                    "symbol": symbol,
                    "duration_ms": duration_ms,
                    "record_count": len(rows)
                }
            )
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        
        update_ticker_status(symbol, "failed")
        
        logger.log_event(
            f"Failed to fetch stock data for {symbol}: {str(e)}",
            "ERROR",
            {
                "operation": "fetch_symbol",
                "symbol": symbol,
                "duration_ms": duration_ms,
                "error_type": type(e).__name__
            }
        )
        error_msg = f"Error fetching {symbol}: {e}"
        send_email(
            subject=f"Stock Fetch Failure: {symbol}",
            body=error_msg
        )

async def fetch_all(symbols: List[str]):
    start_time = time.time()
    logger.log_event(
        "Starting batch stock data fetch",
        "INFO",
        {
            "operation": "batch_fetch",
            "symbol_count": len(symbols),
            "concurrency": CONCURRENCY
        }
    )
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for symbol in symbols:
            async def bound_fetch(sym=symbol):
                async with sem:
                    await fetch_symbol(session, sym)
            tasks.append(bound_fetch())
        await asyncio.gather(*tasks)
        
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_event(
        "Completed batch stock data fetch",
        "INFO",
        {
            "operation": "batch_fetch",
            "symbol_count": len(symbols),
            "duration_ms": duration_ms
        }
    )
