
---

# 🚀 DevOps Dashboard for AWS Resource & Cost Monitoring

## 📌 Problem Statement

DevOps teams often struggle to monitor **resource usage** and **cloud costs** across environments. Without clear visibility into usage drivers, infrastructure optimization becomes guesswork — leading to unnecessary spend and inefficiencies.

This project solves that by building a **centralized AWS monitoring dashboard** with:

* Automated data ingestion from AWS Cost Explorer.
* Storage in a **time-series database**.
* **Grafana dashboards** for real-time + historical insights.
* A **Flask backend API** and Kubernetes deployments for scalability.

---

## 🎯 Project Goals

* Aggregate AWS cost and usage data into a **central dashboard**.
* Provide **real-time & historical visualizations** by region, service, and overall spend.
* Enable **drill-downs and filters** (by service, region, date).
* Support **alerting on anomalies** via Grafana.

---

## 🛠️ Tech Stack

### 🔹 Backend (by [@Sadanki](https://github.com/Sadanki))

* **Python (Flask API)** → serves monitoring endpoints.
* **MongoDB** → persistent store for resource/task metadata.
* **Kubernetes Manifests (YAML)** → deploy services, MongoDB, and APIs.
* **Scheduler + Celery tasks** → fetches AWS data, handles async jobs.
* **Dockerized Services** → containerized for Minikube / K8s.

### 🔹 Frontend (by [@tanujbhatia24](https://github.com/tanujbhatia24))

* **AWS Lambda** → fetches daily cost data from Cost Explorer API → pushes CSV to S3.
* **csv-watcher (Python service)** → ingests CSVs from S3 → InfluxDB.
* **InfluxDB 2.6** → time-series storage for AWS billing data.
* **Grafana Dashboards** → visualization + alerts.
* **Minikube Scripts** → automate startup and pod deployment.

---

## 📂 Project Structure

```
capstone-project/
│── backend/        # Flask API + MongoDB + K8s manifests
│   ├── app/
│   ├── k8s/
│   ├── main.py
│   └── requirements.txt
│
│── frontend/       # csv-watcher + Grafana + InfluxDB + Lambda
│   ├── Dockerfile
│   ├── csv_watcher.py
│   ├── grafana.yaml
│   ├── influxdb.yaml
│   └── startup.sh
│
└── README.md       # 📖 This file
```

---

## 🔄 Data Flow

1. **Lambda Function**

   * Runs daily → calls **AWS Cost Explorer API**.
   * Groups costs by *Service* and *Region*.
   * Saves results as daily CSV into S3 (`costs/YYYY-MM-DD.csv`).

2. **csv-watcher Service (Python)**

   * Watches S3 for new CSVs.
   * Parses and pushes data into **InfluxDB** with:

     * Tags: `service`, `region`
     * Fields: `amortized_cost`, `blended_cost`, `unblended_cost`, `usage_quantity`
     * Timestamp: CSV date

3. **InfluxDB**

   * Stores cost data (`cost_data` bucket).
   * Retains \~180 days (configurable).

4. **Flask Backend (API Layer)**

   * Provides endpoints for cost/resource queries.
   * Uses MongoDB for metadata + async task tracking.

5. **Grafana Dashboards**

   * Queries InfluxDB using Flux.
   * Provides panels: costs by region, top services, daily spend trends, anomalies.

---

## 📊 Dashboard Panels

* AWS **Cost Per Region** 💰
* AWS **Total Spend** 🌍
* **Top 5 Services & Regions Combined** 🔝
* Daily Spend Trends 📈
* Cost Comparison (**Amortized vs Blended vs Unblended**) ⚖️
* Service Usage Quantities 🔧

---

## 🚀 Deployment Guide

### 🔧 Prerequisites

* AWS Account with **Cost Explorer enabled**.
* IAM Role with:

  * `ce:GetCostAndUsage`
  * `s3:PutObject`, `s3:GetObject`
* Kubernetes cluster (Minikube on EC2 recommended).
* Docker installed.

### 📌 Steps

1. **Deploy Backend (Flask + MongoDB):**

   ```bash
   cd backend
   kubectl apply -f k8s/
   ```

2. **Deploy InfluxDB & Grafana:**

   ```bash
   cd frontend
   kubectl apply -f influxdb.yaml
   kubectl apply -f grafana.yaml
   ```

3. **Deploy csv-watcher Service:**

   * Update AWS credentials in `csv-watcher.yaml`.
   * Apply:

     ```bash
     kubectl apply -f csv-watcher.yaml
     ```

4. **Deploy Lambda Function (Python):**

   * Upload `lamda_function.py` to AWS Lambda.
   * Attach IAM role with Cost Explorer + S3 access.

5. **Import Grafana Dashboards:**

   * Load JSON files under `frontend/dashboards/`.

---

## ⚡ Limitations

* AWS Cost Explorer data is **daily granularity only** (24–48h lag).
* Supports **AWS only** (Azure/GCP planned).
* Retention currently **180 days**.

---

## 🔮 Future Enhancements

* Multi-cloud support (**Azure, GCP**).
* Cost anomaly detection + Slack/Teams alerts.
* Multi-account cost aggregation across AWS Organizations.
* Backfill & analyze **12 months historical data**.

---

## 👥 Team

* **Backend:** [@Sadanki](https://github.com/Sadanki) (Flask, MongoDB, Kubernetes, APIs)
* **Frontend:** [@tanujbhatia24](https://github.com/tanujbhatia24) (csv-watcher, Grafana, InfluxDB, Lambda)

---

## 📚 References

* [AWS Cost Explorer API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-explorer-what-is.html)
* [InfluxDB Flux Query Language](https://docs.influxdata.com/flux/)
* [Grafana Docs](https://grafana.com/docs/)

---

✨ With this dashboard, DevOps teams move from **reactive cost management → proactive cost optimization**.
It provides **clear insights, real-time alerts, and drill-down analysis** for better decision-making.

---
