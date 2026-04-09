import sys
import os
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

load_dotenv()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", debug=True, port=int(os.environ.get("PORT", "5000")))