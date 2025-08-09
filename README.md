# Stock Data ETL Pipeline

**An automated ETL pipeline for Stock Ticker data using Apache Airflow and the Alpha Vantage API.**

---

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Getting Started](#getting-started)  
  - [1. Clone the Repository](#1-clone-the-repository)  
  - [2. Configure Environment Variables](#2-configure-environment-variables)  
  - [3. Launch with Docker-Compose](#3-launch-with-docker-compose)  
- [Pipeline Structure](#pipeline-structure)  
- [Usage](#usage)
- [Verifying Data with pgAdmin](#verifying-data-with-pgadmin)  
- [Logging & Volumes](#logging--volumes)  
- [Acknowledgments](#acknowledgments)
- [License](#license)
---

## Overview

This project sets up a fully automated ETL pipeline that:
1. **Extracts** stock price data from the Alpha Vantage API.  
2. **Transforms** the data (e.g., cleansing, formatting).  
3. **Loads** it into Postgres database using Apache Airflow orchestrated workflows.

---

## Features

- Easy setup via `docker-compose.yml`  
- Configurable through `.env` file  
- Modular code under `dags/`, `scripts/`, and SQL components in `sql/`  
- Automatically-generated logs via a mounted volume

---

## Prerequisites

Before getting started, make sure you have:

- Docker and Docker Compose installed  
- A valid **Alpha Vantage API key**  
- The `logs/` directory (if required) — it will be auto-generated when running Docker

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/vipulc2580/Stock_Data_ETL_Pipeline.git
cd Stock_Data_ETL_Pipeline
```

### 2. Configure Environment Variables
Create or update the .env file in the project root as .env_example:
```bash
ALPHAVANTAGE_API_KEY=your_api_key_here
```

### 3. Launch with Docker-Compose
```bash
docker-compose up --build
```
  - Airflow UI: http://localhost:8080
  - pgAdmin UI: http://localhost:5050

## Pipeline Structure
```bash
/
├── dags/                # Airflow DAG definitions
├── scripts/             # ETL scripts (e.g., data extraction, transformation)
├── sql/                 # SQL scripts or query templates
├── docker-compose.yml   # Defines Airflow services and volume mounts
├── requirements.txt     # Python dependencies
├── .env                 # Environment configurations
└── logs/ (auto-generated)
```

##  Usage
1. Open the Airflow UI at http://localhost:8080
    - Default credentials: airflow / airflow (unless changed)
    - Enable the DAG (e.g., stock_etl_dag) to kick off ETL runs.
2. pgAdmin is available at http://localhost:5050
    - Login with the credentials from .env
    - Register the PostgreSQL server using:
    - Host: postgres
    - Port: 5432
    - Username: same as POSTGRES_USER in .env
    - Password: same as POSTGRES_PASSWORD in .env
      
## Verifying Data with pgAdmin
  After the ETL run:
  - Open pgAdmin (http://localhost:5050)
  - Connect to the PostgreSQL server (host: postgres, port: 5432)
  - Navigate to your database (POSTGRES_DB)
  - Run SQL queries to verify that the stock data is correctly loaded.
 Example
  ```sql
  SELECT * FROM tickers;
  SELECT * FROM stock_data;
  ```

## Logging & Volumes
- The logs/ directory in your project root will automatically be created when Docker runs (if it doesn’t already exist). Airflow writes execution logs into /opt/airflow/logs, which in turn appear in your logs/ local directory—even though logs are .gitignored, they’re accessible locally.

## Acknowledgments
I would like to express my sincere gratitude to:
 - Alpha Vantage for providing free and reliable stock market data APIs.
 - The open-source community for creating and maintaining powerful tools like Apache Airflow, PostgreSQL, and pgAdmin, without which this project would not have been possible.

## License
Feel free to adapt or extend this pipeline as needed. Consider adding the license type if you're planning to make this open source (e.g., MIT, Apache 2.0).
```yaml
If you want, I can also add a **simple architecture diagram** showing how Alpha Vantage → Airflow → PostgreSQL → pgAdmin connects.  
That will make the README even more professional and beginner-friendly.
```
