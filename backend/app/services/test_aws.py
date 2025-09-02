from app.services.aws_service import fetch_and_store_cost

if __name__ == "__main__":
    fetch_and_store_cost()
    print("✅ Cost data fetched and stored in MongoDB.")
