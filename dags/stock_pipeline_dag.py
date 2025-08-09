import asyncio
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from scripts.fetcher import fetch_all
from scripts.db_client import get_symbols_to_fetch
from scripts.email_alerts import send_email
from scripts.logger import logger

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def run_fetch_all():
    try:
        logger.log_event(
            "Stock data pipeline DAG execution started",
            "INFO",
            {
                "operation": "dag_start",
                "dag_id": "stock_data_pipeline",
                "execution_date": datetime.now().isoformat()
            }
        )
        
        symbols = get_symbols_to_fetch()
        
        if not symbols:
            msg = "No tickers to fetch today. Please check upstream data or database."
            
            logger.log_event(
                "No symbols found to fetch - sending alert email",
                "WARNING",
                {
                    "operation": "dag_no_symbols",
                    "symbol_count": 0,
                    "status": "no_symbols_found"
                }
            )
            
            send_email(
                subject="Stock Pipeline Alert: No tickers to fetch",
                body=msg
            )
            return
        
        logger.log_event(
            f"Starting stock data fetch process for {len(symbols)} symbols",
            "INFO",
            {
                "operation": "dag_fetch_start", 
                "symbol_count": len(symbols),
                "symbols": str(symbols)
            }
        )
        
        asyncio.run(fetch_all(symbols))
        
        logger.log_event(
            f"Stock data pipeline completed successfully for {len(symbols)} symbols",
            "INFO",
            {
                "operation": "dag_success",
                "symbol_count": len(symbols),
                "completion_time": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.log_event(
            f"Stock data pipeline DAG execution failed: {str(e)}",
            "ERROR",
            {
                "operation": "dag_failure",
                "error_type": type(e).__name__,
                "failure_time": datetime.now().isoformat()
            }
        )

with DAG(
    "stock_data_pipeline",
    default_args=default_args,
    description="Fetch stock data and upsert into Postgres daily",
    schedule_interval="0 18 * * *",  # every day at 6 PM UTC (adjust as needed)
    start_date=datetime(2023, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_stock_data",
        python_callable=run_fetch_all,
    )
