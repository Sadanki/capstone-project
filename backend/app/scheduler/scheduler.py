from apscheduler.schedulers.background import BackgroundScheduler
from app.services.aws_service import fetch_and_store_cost  # Changed import

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_cost, 'interval', days=1)  # Use existing function
    scheduler.start()