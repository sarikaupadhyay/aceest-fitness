"""
ACEest Fitness & Gym - Flask Web Application
Assignment 1 - Introduction to DevOps
"""

from flask import Flask, request, jsonify, render_template_string
import sqlite3
import random
from datetime import date

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

# ─────────────────────────────────────────────
# Program data (from original Tkinter versions)
# ─────────────────────────────────────────────
PROGRAMS = {
    "Fat Loss": {
        "workout": (
            "Mon: Back Squat 5x5 + Core\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: Deadlift + Box Jumps\n"
            "Fri: Zone 2 Cardio 30min"
        ),
        "diet": (
            "Breakfast: Egg Whites + Oats\n"
            "Lunch: Grilled Chicken + Brown Rice\n"
            "Dinner: Fish Curry + Millet Roti\n"
            "Target: ~2000 kcal"
        ),
        "calories": 2000,
    },
    "Muscle Gain": {
        "workout": (
            "Mon: Squat 5x5\n"
            "Tue: Bench 5x5\n"
            "Wed: Deadlift 4x6\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "Breakfast: Eggs + Peanut Butter Oats\n"
            "Lunch: Chicken Biryani\n"
            "Dinner: Mutton Curry + Rice\n"
            "Target: ~3200 kcal"
        ),
        "calories": 3200,
    },
    "Beginner": {
        "workout": (
            "Full Body Circuit:\n"
            "- Air Squats\n"
            "- Ring Rows\n"
            "- Push-ups\n"
            "Focus: Technique & Consistency"
        ),
        "diet": (
            "Balanced Tamil Meals\n"
            "Idli / Dosa / Rice + Dal\n"
            "Protein Target: 120g/day"
        ),
        "calories": 2600,
    },
}

# ─────────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            weight REAL,
            program TEXT,
            membership_status TEXT DEFAULT 'Active',
            membership_end TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT NOT NULL,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            week TEXT NOT NULL,
            adherence INTEGER
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# HTML template (single-file, no templates dir)
# ─────────────────────────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ACEest Fitness & Gym</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; background: #1a1a1a; color: #eee; }
  header { background: #d4af37; color: #111; text-align: center; padding: 18px;
           font-size: 1.6rem; font-weight: bold; letter-spacing: 1px; }
  nav { background: #222; display: flex; gap: 4px; padding: 8px 20px; flex-wrap: wrap; }
  nav a { color: #d4af37; text-decoration: none; padding: 6px 14px;
          border: 1px solid #d4af37; border-radius: 4px; font-size: 0.9rem; }
  nav a:hover { background: #d4af37; color: #111; }
  main { max-width: 900px; margin: 30px auto; padding: 0 20px; }
  h2 { color: #d4af37; margin-bottom: 16px; }
  .card { background: #2a2a2a; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
  label { display: block; margin-top: 12px; margin-bottom: 4px; color: #bbb; font-size: 0.9rem; }
  input, select, textarea { width: 100%; padding: 8px 10px; border-radius: 4px;
    border: 1px solid #444; background: #333; color: #eee; font-size: 0.95rem; }
  button, .btn { background: #d4af37; color: #111; border: none; padding: 9px 20px;
    border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.95rem; margin-top: 12px; }
  button:hover, .btn:hover { background: #c9a227; }
  .btn-danger { background: #c0392b; color: #fff; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #d4af37; color: #111; padding: 8px 12px; text-align: left; }
  td { padding: 8px 12px; border-bottom: 1px solid #333; }
  tr:hover td { background: #333; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; }
  .badge-active { background: #1e8449; color: #fff; }
  .badge-inactive { background: #7b241c; color: #fff; }
  .alert { padding: 12px; border-radius: 6px; margin-bottom: 16px; }
  .alert-success { background: #1e4d2b; color: #a9dfbf; }
  .alert-error   { background: #4a1010; color: #f1948a; }
  .program-box { background: #1a1a1a; border-left: 4px solid #d4af37;
    padding: 12px 16px; white-space: pre-line; font-size: 0.9rem; border-radius: 4px; }
  footer { text-align: center; padding: 20px; color: #555; font-size: 0.8rem; }
</style>
</head>
<body>
<header>ACEest Fitness &amp; Gym Management</header>
<nav>
  <a href="/">Dashboard</a>
  <a href="/clients">Clients</a>
  <a href="/clients/add">Add Client</a>
  <a href="/workouts">Workouts</a>
  <a href="/programs">Programs</a>
</nav>
<main>
  {% if msg %}
    <div class="alert alert-{{ msg_type }}">{{ msg }}</div>
  {% endif %}
  {{ body }}
</main>
<footer>ACEest Fitness &amp; Gym &mdash; DevOps Assignment 1</footer>
</body>
</html>
"""

def render(body, msg=None, msg_type="success"):
    from markupsafe import Markup
    return render_template_string(
        HTML,
        body=Markup(body),
        msg=msg,
        msg_type=msg_type,
    )


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/")
def dashboard():
    conn = get_db()
    total_clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    active_clients = conn.execute(
        "SELECT COUNT(*) FROM clients WHERE membership_status='Active'"
    ).fetchone()[0]
    total_workouts = conn.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]
    conn.close()

    body = f"""
    <h2>Dashboard</h2>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px;">
      <div class="card" style="text-align:center;">
        <div style="font-size:2.4rem;color:#d4af37;font-weight:bold;">{total_clients}</div>
        <div style="color:#aaa;">Total Clients</div>
      </div>
      <div class="card" style="text-align:center;">
        <div style="font-size:2.4rem;color:#2ecc71;font-weight:bold;">{active_clients}</div>
        <div style="color:#aaa;">Active Members</div>
      </div>
      <div class="card" style="text-align:center;">
        <div style="font-size:2.4rem;color:#3498db;font-weight:bold;">{total_workouts}</div>
        <div style="color:#aaa;">Workouts Logged</div>
      </div>
    </div>
    <div class="card">
      <h2 style="margin-bottom:10px;">Gym Capacity Reference</h2>
      <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Capacity</td><td>150 members</td></tr>
        <tr><td>Floor Area</td><td>10,000 sq ft</td></tr>
        <tr><td>Break-even</td><td>250 members</td></tr>
      </table>
    </div>
    """
    return render(body)


# ── Clients ──────────────────────────────────

@app.route("/clients")
def clients():
    conn = get_db()
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()

    rows_html = ""
    for r in rows:
        badge = "active" if r["membership_status"] == "Active" else "inactive"
        rows_html += f"""
        <tr>
          <td>{r['name']}</td>
          <td>{r['age'] or '-'}</td>
          <td>{r['weight'] or '-'}</td>
          <td>{r['program'] or '-'}</td>
          <td><span class="badge badge-{badge}">{r['membership_status']}</span></td>
          <td>{r['membership_end'] or '-'}</td>
          <td>
            <a class="btn" href="/clients/{r['id']}">View</a>
            <a class="btn" href="/clients/{r['id']}/generate-program">Gen Program</a>
          </td>
        </tr>"""

    body = f"""
    <h2>All Clients</h2>
    <div class="card" style="overflow-x:auto;">
      <table>
        <tr>
          <th>Name</th><th>Age</th><th>Weight (kg)</th>
          <th>Program</th><th>Membership</th><th>Renewal</th><th>Actions</th>
        </tr>
        {rows_html if rows_html else '<tr><td colspan="7" style="text-align:center;color:#888;">No clients yet. <a href="/clients/add" style="color:#d4af37;">Add one!</a></td></tr>'}
      </table>
    </div>
    """
    return render(body)


@app.route("/clients/add", methods=["GET", "POST"])
def add_client():
    if request.method == "POST":
        name   = request.form.get("name", "").strip()
        age    = request.form.get("age", "").strip()
        weight = request.form.get("weight", "").strip()
        program = request.form.get("program", "").strip()
        membership_end = request.form.get("membership_end", "").strip()

        if not name:
            return render(_add_client_form(), msg="Name is required.", msg_type="error")

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO clients (name, age, weight, program, membership_status, membership_end) "
                "VALUES (?, ?, ?, ?, 'Active', ?)",
                (name, age or None, weight or None, program or None, membership_end or None),
            )
            conn.commit()
            conn.close()
            return render(_add_client_form(), msg=f"Client '{name}' added successfully!")
        except sqlite3.IntegrityError:
            return render(_add_client_form(), msg=f"Client '{name}' already exists.", msg_type="error")

    return render(_add_client_form())


def _add_client_form():
    options = "".join(f'<option value="{p}">{p}</option>' for p in PROGRAMS)
    return f"""
    <h2>Add New Client</h2>
    <div class="card">
      <form method="POST" action="/clients/add">
        <label>Full Name *</label>
        <input name="name" placeholder="e.g. Arjun Kumar" required>

        <label>Age</label>
        <input name="age" type="number" placeholder="e.g. 28">

        <label>Current Weight (kg)</label>
        <input name="weight" type="number" step="0.1" placeholder="e.g. 75.5">

        <label>Program</label>
        <select name="program">
          <option value="">-- Select Program --</option>
          {options}
        </select>

        <label>Membership Renewal Date</label>
        <input name="membership_end" type="date">

        <button type="submit">Add Client</button>
      </form>
    </div>
    """


@app.route("/clients/<int:client_id>")
def client_detail(client_id):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if not client:
        conn.close()
        return render("<h2>Client not found.</h2>", msg="Client not found.", msg_type="error")

    workouts = conn.execute(
        "SELECT * FROM workouts WHERE client_name=? ORDER BY date DESC LIMIT 10",
        (client["name"],),
    ).fetchall()
    conn.close()

    workout_rows = ""
    for w in workouts:
        workout_rows += f"<tr><td>{w['date']}</td><td>{w['workout_type']}</td><td>{w['duration_min']} min</td><td>{w['notes'] or '-'}</td></tr>"

    program_html = ""
    if client["program"] and client["program"] in PROGRAMS:
        p = PROGRAMS[client["program"]]
        program_html = f"""
        <h3 style="color:#d4af37;margin:16px 0 8px;">Current Program: {client['program']}</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div>
            <div style="color:#aaa;font-size:0.85rem;margin-bottom:4px;">WORKOUT PLAN</div>
            <div class="program-box">{p['workout']}</div>
          </div>
          <div>
            <div style="color:#aaa;font-size:0.85rem;margin-bottom:4px;">NUTRITION PLAN</div>
            <div class="program-box">{p['diet']}</div>
          </div>
        </div>
        """

    badge = "active" if client["membership_status"] == "Active" else "inactive"
    body = f"""
    <h2>{client['name']}</h2>
    <div class="card">
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
        <div><div style="color:#aaa;font-size:0.8rem;">AGE</div><div style="font-size:1.2rem;">{client['age'] or '-'}</div></div>
        <div><div style="color:#aaa;font-size:0.8rem;">WEIGHT</div><div style="font-size:1.2rem;">{client['weight'] or '-'} kg</div></div>
        <div><div style="color:#aaa;font-size:0.8rem;">MEMBERSHIP</div>
          <span class="badge badge-{badge}">{client['membership_status']}</span></div>
        <div><div style="color:#aaa;font-size:0.8rem;">RENEWAL</div><div style="font-size:1rem;">{client['membership_end'] or '-'}</div></div>
      </div>
      {program_html}
      <div style="margin-top:16px;">
        <a class="btn" href="/clients/{client_id}/generate-program">Generate Program</a>
        <a class="btn" href="/workouts/add?client={client['name']}" style="margin-left:8px;">Log Workout</a>
      </div>
    </div>
    <h2>Recent Workouts</h2>
    <div class="card" style="overflow-x:auto;">
      <table>
        <tr><th>Date</th><th>Type</th><th>Duration</th><th>Notes</th></tr>
        {workout_rows if workout_rows else '<tr><td colspan="4" style="color:#888;text-align:center;">No workouts logged yet.</td></tr>'}
      </table>
    </div>
    """
    return render(body)


@app.route("/clients/<int:client_id>/generate-program")
def generate_program(client_id):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    if not client:
        conn.close()
        return render("<h2>Client not found.</h2>", msg_type="error")

    new_program = random.choice(list(PROGRAMS.keys()))
    conn.execute("UPDATE clients SET program=? WHERE id=?", (new_program, client_id))
    conn.commit()
    conn.close()

    from flask import redirect, url_for
    return redirect(url_for("client_detail", client_id=client_id))


# ── Workouts ──────────────────────────────────

@app.route("/workouts")
def workouts():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM workouts ORDER BY date DESC LIMIT 50"
    ).fetchall()
    conn.close()

    rows_html = ""
    for w in rows:
        rows_html += f"<tr><td>{w['client_name']}</td><td>{w['date']}</td><td>{w['workout_type']}</td><td>{w['duration_min']} min</td><td>{w['notes'] or '-'}</td></tr>"

    body = f"""
    <h2>All Workouts</h2>
    <div style="margin-bottom:12px;">
      <a class="btn" href="/workouts/add">Log New Workout</a>
    </div>
    <div class="card" style="overflow-x:auto;">
      <table>
        <tr><th>Client</th><th>Date</th><th>Type</th><th>Duration</th><th>Notes</th></tr>
        {rows_html if rows_html else '<tr><td colspan="5" style="text-align:center;color:#888;">No workouts logged yet.</td></tr>'}
      </table>
    </div>
    """
    return render(body)


@app.route("/workouts/add", methods=["GET", "POST"])
def add_workout():
    conn = get_db()
    clients_list = conn.execute("SELECT name FROM clients ORDER BY name").fetchall()
    conn.close()

    prefill_client = request.args.get("client", "")

    if request.method == "POST":
        client_name  = request.form.get("client_name", "").strip()
        workout_date = request.form.get("date", str(date.today()))
        workout_type = request.form.get("workout_type", "").strip()
        duration     = request.form.get("duration_min", "60").strip()
        notes        = request.form.get("notes", "").strip()

        if not client_name:
            return render(_add_workout_form(clients_list, prefill_client),
                          msg="Client name is required.", msg_type="error")

        conn = get_db()
        conn.execute(
            "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?,?,?,?,?)",
            (client_name, workout_date, workout_type, duration or 60, notes or None),
        )
        conn.commit()
        conn.close()
        return render(_add_workout_form(clients_list, prefill_client),
                      msg="Workout logged successfully!")

    return render(_add_workout_form(clients_list, prefill_client))


def _add_workout_form(clients_list, prefill=""):
    client_options = "".join(
        f'<option value="{c["name"]}" {"selected" if c["name"]==prefill else ""}>{c["name"]}</option>'
        for c in clients_list
    )
    return f"""
    <h2>Log Workout</h2>
    <div class="card">
      <form method="POST" action="/workouts/add">
        <label>Client *</label>
        <select name="client_name" required>
          <option value="">-- Select Client --</option>
          {client_options}
        </select>

        <label>Date</label>
        <input name="date" type="date" value="{date.today()}">

        <label>Workout Type</label>
        <select name="workout_type">
          <option>Strength</option>
          <option>Hypertrophy</option>
          <option>Cardio</option>
          <option>HIIT</option>
          <option>Mobility</option>
          <option>Circuit</option>
        </select>

        <label>Duration (minutes)</label>
        <input name="duration_min" type="number" value="60" min="1">

        <label>Notes</label>
        <textarea name="notes" rows="3" placeholder="e.g. PB on squat, felt strong..."></textarea>

        <button type="submit">Log Workout</button>
      </form>
    </div>
    """


# ── Programs ──────────────────────────────────

@app.route("/programs")
def programs():
    cards = ""
    for name, data in PROGRAMS.items():
        cards += f"""
        <div class="card">
          <h3 style="color:#d4af37;margin-bottom:12px;">{name}</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <div style="color:#aaa;font-size:0.8rem;margin-bottom:4px;">WORKOUT</div>
              <div class="program-box">{data['workout']}</div>
            </div>
            <div>
              <div style="color:#aaa;font-size:0.8rem;margin-bottom:4px;">NUTRITION</div>
              <div class="program-box">{data['diet']}</div>
              <div style="margin-top:8px;color:#d4af37;">Target: {data['calories']} kcal/day</div>
            </div>
          </div>
        </div>"""

    body = f"<h2>Training Programs</h2>{cards}"
    return render(body)


# ── JSON API endpoints (for testing) ──────────

@app.route("/api/clients", methods=["GET"])
def api_get_clients():
    conn = get_db()
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/clients", methods=["POST"])
def api_add_client():
    data = request.get_json(force=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO clients (name, age, weight, program, membership_status) VALUES (?,?,?,?,?)",
            (name, data.get("age"), data.get("weight"), data.get("program"), "Active"),
        )
        conn.commit()
        client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
        conn.close()
        return jsonify(dict(client)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": f"Client '{name}' already exists"}), 409


@app.route("/api/clients/<int:client_id>", methods=["GET"])
def api_get_client(client_id):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
    conn.close()
    if not client:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(client))


@app.route("/api/programs", methods=["GET"])
def api_get_programs():
    return jsonify(list(PROGRAMS.keys()))


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "ACEest Fitness"})


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
