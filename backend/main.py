from app import create_app

app = create_app()

from app.scheduler.scheduler import start_scheduler

start_scheduler()

if __name__ == "__main__":
    app.run(debug=True)