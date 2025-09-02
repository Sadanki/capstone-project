from flask import jsonify
from app.services.aws_service import fetch_and_store_cost
from .db.mongo import cost_collection# Add this import

def register_routes(app):
    @app.route("/", methods=["GET"])
    def home():
        return """
        <html>
        <head>
            <title>DevOps Dashboard</title>
            <style>
                body {
                    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
                    color: #fff;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    text-align: center;
                    padding-top: 100px;
                }
                .bounce {
                    animation: bounce 2s infinite;
                    font-size: 3em;
                    margin-bottom: 20px;
                }
                @keyframes bounce {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-20px); }
                }
                .emoji {
                    font-size: 5em;
                }
            </style>
        </head>
        <body>
            <div class="emoji">🛠️🚀</div>
            <div class="bounce">DevOps Dashboard Backend Running</div>
            <p>Welcome to the automated world of CI/CD ✨</p>
        </body>
        </html>
        """

    @app.route("/fetch-costs", methods=["GET"])
    def fetch_costs():
        try:
            # Directly query MongoDB instead of using get_all_service_costs
            cost_data = list(cost_collection.find({}, {"_id": 0}))
            return jsonify({
                "success": True,
                "data": cost_data
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "data": []
            }), 500