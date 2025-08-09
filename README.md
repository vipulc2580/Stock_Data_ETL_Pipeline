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
- [Logging & Volumes](#logging--volumes)  

---

## Overview

This project sets up a fully automated ETL pipeline that:
1. **Extracts** stock price data from the Alpha Vantage API.  
2. **Transforms** the data (e.g., cleansing, formatting).  
3. **Loads** it into your selected storage or database using Apache Airflow orchestrated workflows.

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
Create or update the .env file in the project root:
```bash
ALPHAVANTAGE_API_KEY=your_api_key_here
```

### 3. Launch with Docker-Compose
```bash
docker-compose up --build
```
This will spin up Airflow and its components. You can access the Airflow UI at http://localhost:8080.

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
- Open the Airflow UI and enable the DAG (e.g., stock_etl_dag) to kick off ETL runs.
- Monitor task statuses, logs, and execution graphs via the interface.

## Logging & Volumes
- The logs/ directory in your project root will automatically be created when Docker runs (if it doesn’t already exist). Airflow writes execution logs into /opt/airflow/logs, which in turn appear in your logs/ local directory—even though logs are .gitignored, they’re accessible locally.


