import pathlib
import sqlite3

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_material import Material
from flask_sqlalchemy import SQLAlchemy

# App initialization
# app = Flask("my_web_app")

# 1. Get the path to the directory containing this file (main.py)
BASE_DIR = pathlib.Path(__file__).parent.resolve()

# 2. Explicitly tell Flask where to find the templates folder.
#    The path will be something like '/workspace/src/my_web_app/templates'
app = Flask(__name__, template_folder=BASE_DIR / "templates")

Material(app)

# # Database configuration
# basedir = os.path.abspath(os.path.dirname(__file__))
# db_path = os.path.join(basedir, "my_web_app", "database.db")
# print("Database path:", db_path)

# 1. Get the absolute path to the project's root directory (/workspace)
#    Since main.py is in /workspace/src/my_web_app/, we go up three levels.
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()

# 2. Define the path to your data directory and database file
DB_DIR = PROJECT_ROOT / "data"
DB_FILE = DB_DIR / "app.db"

# 3. IMPORTANT: Ensure the data directory exists before trying to connect
DB_DIR.mkdir(parents=True, exist_ok=True)

db_path = str(DB_FILE)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def init_db():
    print("init.db says Hi!")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""    
    drop table if exists event;
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        start TEXT NOT NULL,
        end TEXT NULL,
        allDay BOOLEAN NOT NULL,
        user TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()


init_db()


db = SQLAlchemy(app)

# In-memory store for vote counts
votes = {
    "image1": 0,
    "image2": 0,
    "image3": 0,
}


# --- Models ---
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start = db.Column(db.String(100), nullable=False)
    end = db.Column(db.String(100), nullable=True)
    allDay = db.Column(db.Boolean, default=True)
    user = db.Column(db.String(50), default="default_user")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start,
            "end": self.end,
            "allDay": self.allDay,
            "user": self.user,
        }


# --- Standard Routes ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/cats")
def cats():
    return render_template("cats.html", votes=votes)


@app.route("/vote/<image_id>/<direction>")
def vote(image_id, direction):
    if image_id in votes:
        if direction == "up":
            votes[image_id] += 1
        elif direction == "down":
            votes[image_id] -= 1
    return redirect(url_for("cats"))


@app.route("/calendar")
def calendar():
    return render_template("calendar.html")


# --- API Routes for Calendar ---
@app.route("/api/events", methods=["GET"])
def get_events():
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events])


@app.route("/api/events", methods=["POST"])
def create_event():
    data = request.get_json()
    print("Received event data:", data)  # Add this line
    new_event = Event(
        title=data.get("title"),
        start=data.get("start"),
        end=data.get("end"),
        allDay=data.get("allDay", True),
        user=data.get("user", "default_user"),
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify(new_event.to_dict()), 201


@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    data = request.get_json()
    event = Event.query.get_or_404(event_id)
    event.title = data.get("title", event.title)
    event.start = data.get("start", event.start)
    event.end = data.get("end", event.end)
    event.allDay = data.get("allDay", event.allDay)
    db.session.commit()
    return jsonify(event.to_dict())


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Event deleted"}), 200


# @app.cli.command("init-db")
# @with_appcontext
# def init_db():
#     db.create_all()
#     print("Database and tables created!")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
