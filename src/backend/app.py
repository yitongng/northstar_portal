import sqlite3
from pathlib import Path

from flask import (
    Flask, jsonify, render_template, g
)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_TEMPLATES = PROJECT_ROOT / "frontend" / "templates"

from portal_routes import portal_bp

app = Flask(__name__, template_folder=str(FRONTEND_TEMPLATES))
app.register_blueprint(portal_bp)

USERS_FILE_PATH = BASE_DIR / "sensitive.json"

from initialise_db import DB_PATH, init_db


# database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

# =========================================================
# Home page
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# Health check and startup
# =========================================================

@app.route("/health")
def health():
    return jsonify(status="ok")


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)