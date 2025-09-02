import os
from datetime import date, timedelta
from dotenv import load_dotenv
import boto3
from flask import current_app
import logging

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "ap-south-1")

client_ce = boto3.client(
    "ce",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

def format_service_name(service):
    """Map AWS internal names to display-friendly names."""
    service_mapping = {
        "Amazon Elastic Compute Cloud - Compute": "Amazon EC2",
        "Amazon Simple Storage Service": "Amazon S3",
        "Amazon Elastic Block Store": "Amazon EBS",
        "Amazon RDS Service": "Amazon RDS",
        "Amazon DynamoDB": "Amazon DynamoDB",
        "Amazon CloudWatch": "Amazon CloudWatch",
    }
    return service_mapping.get(service, service)

def normalize_aws_cost_record(raw_record):
    """Normalize raw AWS cost record to a flat dict for MongoDB."""
    date_val = raw_record["date"]
    group_keys = raw_record.get("group_keys", [])

    # Extract keys with safe defaults
    raw_service = group_keys[0] if len(group_keys) > 0 else "Unknown"
    service = format_service_name(raw_service)
    region = group_keys[1] if len(group_keys) > 1 else "Unknown"
    usage_type = group_keys[2] if len(group_keys) > 2 else "Unknown"
    operation = group_keys[3] if len(group_keys) > 3 else "Unknown"

    metrics = raw_record.get("metrics", {})
    amortized_cost = float(metrics.get("AmortizedCost", {}).get("Amount", 0))
    blended_cost = float(metrics.get("BlendedCost", {}).get("Amount", 0))
    unblended_cost = float(metrics.get("UnblendedCost", {}).get("Amount", 0))
    usage_quantity = float(metrics.get("UsageQuantity", {}).get("Amount", 0))

    normalized_doc = {
        "date": date_val,
        "service": service,
        "region": region,
        "usage_type": usage_type,
        "operation": operation,
        "amortized_cost": round(amortized_cost, 5),
        "blended_cost": round(blended_cost, 5),
        "unblended_cost": round(unblended_cost, 5),
        "usage_quantity": round(usage_quantity, 5),
    }
    return normalized_doc

def fetch_and_store_cost():
    try:
        end = date.today()
        start = end - timedelta(days=7)

        metrics = ["AmortizedCost", "BlendedCost", "UnblendedCost", "UsageQuantity"]
        group_by = [
            {"Type": "DIMENSION", "Key": "SERVICE"},
            {"Type": "DIMENSION", "Key": "REGION"},
            {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
            {"Type": "DIMENSION", "Key": "OPERATION"},
        ]

        logger.info(f"Fetching AWS costs from {start} to {end}")
        response = client_ce.get_cost_and_usage(
            TimePeriod={"Start": str(start), "End": str(end)},
            Granularity="DAILY",
            Metrics=metrics,
            GroupBy=group_by,
            Filter={
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": ["Amazon Elastic Compute Cloud - Compute"]
                }
            }
        )

        cost_collection = current_app.db["aws_costs"]
        inserted_count = 0

        for result in response["ResultsByTime"]:
            date_val = result["TimePeriod"]["Start"]
            for group in result["Groups"]:
                raw_record = {
                    "date": date_val,
                    "group_keys": group["Keys"],
                    "metrics": group["Metrics"],
                }

                normalized_doc = normalize_aws_cost_record(raw_record)

                # Skip zero cost records
                if normalized_doc["amortized_cost"] == 0.0:
                    continue

                # Use all keys to uniquely identify a record
                filter_query = {
                    "date": normalized_doc["date"],
                    "service": normalized_doc["service"],
                    "region": normalized_doc["region"],
                    "usage_type": normalized_doc["usage_type"],
                    "operation": normalized_doc["operation"],
                }

                cost_collection.update_one(
                    filter_query,
                    {"$set": normalized_doc},
                    upsert=True
                )
                inserted_count += 1

        logger.info(f"Stored {inserted_count} new/updated records.")
        return True

    except Exception as e:
        logger.error(f"Error fetching AWS cost data: {str(e)}")
        raise
