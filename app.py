from flask import Flask, render_template, request, redirect, url_for, g, abort
import sqlite3
import os
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, 'dispatch.db')
TEMPLATES_DIR = os.path.join(APP_DIR, 'templates')
STATIC_DIR = os.path.join(APP_DIR, 'static')

app = Flask(__name__)
app.config['DATABASE'] = DB_PATH
app.config['TEMPLATES_AUTO_RELOAD'] = True

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(app.config['DATABASE'])
    cur = db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS dispatches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dispatch_no TEXT,
        today_nepali_date TEXT,
        subject TEXT,
        license_no TEXT,
        name TEXT,
        nagrita_no TEXT,
        father_name TEXT,
        dob TEXT,
        issue_date TEXT,
        expire_date TEXT,
        license_category TEXT,
        created_at TEXT
    )''')
    db.commit()
    db.close()

def ensure_files():
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    with open(os.path.join(TEMPLATES_DIR, 'form.html'), 'w', encoding='utf-8') as f:
        f.write(FORM_HTML)
    with open(os.path.join(TEMPLATES_DIR, 'list.html'), 'w', encoding='utf-8') as f:
        f.write(LIST_HTML)
    with open(os.path.join(TEMPLATES_DIR, 'report.html'), 'w', encoding='utf-8') as f:
        f.write(REPORT_HTML)
    with open(os.path.join(STATIC_DIR, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(STYLE_CSS)

FORM_HTML = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ 'Edit Record' if record else 'New Dispatch' }}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <div class="container">
    <h1>{{ 'Edit Record' if record else 'Dispatch Form' }}</h1>
    <form method="POST" action="{{ url_for('update_record', rec_id=record.id) if record else url_for('submit') }}">
      <label>Dispatch No:</label>
      <input type="text" name="dispatch_no" value="{{ record.dispatch_no if record else '' }}" required>

      <label>Today (Nepali Date):</label>
      <input type="text" name="today_nepali_date" value="{{ record.today_nepali_date if record else '' }}" required>

      <label>Subject:</label>
      <input type="text" name="subject" value="{{ record.subject if record else '' }}">

      <label>License No:</label>
      <input type="text" name="license_no" value="{{ record.license_no if record else '' }}">

      <label>Name:</label>
      <input type="text" name="name" value="{{ record.name if record else '' }}">

      <label>Nagrita No:</label>
      <input type="text" name="nagrita_no" value="{{ record.nagrita_no if record else '' }}">

      <label>Father Name:</label>
      <input type="text" name="father_name" value="{{ record.father_name if record else '' }}">

      <label>Date of Birth:</label>
      <input type="date" name="dob" value="{{ record.dob if record else '' }}">

      <label>Issue Date:</label>
      <input type="date" name="issue_date" value="{{ record.issue_date if record else '' }}">

      <label>Expire Date:</label>
      <input type="date" name="expire_date" value="{{ record.expire_date if record else '' }}">

      <label>License Category:</label>
      <input type="text" name="license_category" value="{{ record.license_category if record else '' }}">

      <button type="submit">{{ 'Update Record' if record else 'Save Record' }}</button>
      <a href="{{ url_for('list_records') }}" class="button">Back</a>
    </form>
  </div>
</body>
</html>'''

LIST_HTML = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>All Dispatch Records</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <div class="container">
    <h1>All Dispatch Records</h1>
    <a href="{{ url_for('index') }}" class="button">+ New Dispatch</a>
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Dispatch No</th><th>Name</th><th>License No</th><th>Nepali Date</th><th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for r in rows %}
        <tr>
          <td>{{ r.id }}</td>
          <td>{{ r.dispatch_no }}</td>
          <td>{{ r.name }}</td>
          <td>{{ r.license_no }}</td>
          <td>{{ r.today_nepali_date }}</td>
          <td>
            <a href="{{ url_for('view_record', rec_id=r.id) }}" target="_blank">View</a> |
            <a href="{{ url_for('edit_record', rec_id=r.id) }}">Edit</a> |
            <a href="{{ url_for('print_record', rec_id=r.id) }}" target="_blank">Print</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</body>
</html>'''

REPORT_HTML = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Dispatch Report</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body class="a4page">
  <div class="print-header">
    <h2>Office of Transport Management</h2>
    <p>Kathmandu, Nepal</p>
    <hr>
  </div>
  <div class="report-body">
    <h3>Dispatch Report</h3>
    <table class="report-table">
      <tr><th>Dispatch No:</th><td>{{ row.dispatch_no }}</td></tr>
      <tr><th>Today (Nepali Date):</th><td>{{ row.today_nepali_date }}</td></tr>
      <tr><th>Subject:</th><td>{{ row.subject }}</td></tr>
      <tr><th>License No:</th><td>{{ row.license_no }}</td></tr>
      <tr><th>Name:</th><td>{{ row.name }}</td></tr>
      <tr><th>Nagrita No:</th><td>{{ row.nagrita_no }}</td></tr>
      <tr><th>Father Name:</th><td>{{ row.father_name }}</td></tr>
      <tr><th>Date of Birth:</th><td>{{ row.dob }}</td></tr>
      <tr><th>Issue Date:</th><td>{{ row.issue_date }}</td></tr>
      <tr><th>Expire Date:</th><td>{{ row.expire_date }}</td></tr>
      <tr><th>License Category:</th><td>{{ row.license_category }}</td></tr>
    </table>
    <div class="signature">
      <p>Officer Signature: ______________________</p>
    </div>
  </div>
</body>
</html>'''

STYLE_CSS = '''body { font-family: Arial; margin: 0; padding: 0; }
.container { width: 90%; margin: 20px auto; }
label { display: block; margin-top: 10px; }
input { width: 100%; padding: 8px; }
button, .button { margin-top: 10px; padding: 8px 12px; background: #007bff; color: white; border: none; border-radius: 4px; text-decoration: none; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
.a4page { width: 210mm; min-height: 297mm; margin: auto; padding: 20mm; }
.print-header { text-align: center; }
.report-table { width: 100%; border-collapse: collapse; }
.report-table th { text-align: left; background: #f2f2f2; width: 40%; }
.signature { margin-top: 40px; text-align: right; }'''

@app.route('/')
def index():
    return render_template('form.html', record=None)

@app.route('/submit', methods=['POST'])
def submit():
    db = get_db()
    cur = db.cursor()
    data = {k: request.form.get(k) for k in ['dispatch_no','today_nepali_date','subject','license_no','name','nagrita_no','father_name','dob','issue_date','expire_date','license_category']}
    now = datetime.utcnow().isoformat()
    cur.execute('''INSERT INTO dispatches (dispatch_no,today_nepali_date,subject,license_no,name,nagrita_no,father_name,dob,issue_date,expire_date,license_category,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', tuple(data.values()) + (now,))
    db.commit()
    return redirect(url_for('list_records'))

@app.route('/records')
def list_records():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM dispatches ORDER BY id DESC')
    rows = cur.fetchall()
    return render_template('list.html', rows=rows)

@app.route('/edit/<int:rec_id>')
def edit_record(rec_id):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM dispatches WHERE id=?', (rec_id,))
    record = cur.fetchone()
    if not record:
        abort(404)
    return render_template('form.html', record=record)

@app.route('/update/<int:rec_id>', methods=['POST'])
def update_record(rec_id):
    db = get_db()
    cur = db.cursor()
    data = {k: request.form.get(k) for k in ['dispatch_no','today_nepali_date','subject','license_no','name','nagrita_no','father_name','dob','issue_date','expire_date','license_category']}
    cur.execute('''UPDATE dispatches SET dispatch_no=?, today_nepali_date=?, subject=?, license_no=?, name=?, nagrita_no=?, father_name=?, dob=?, issue_date=?, expire_date=?, license_category=? WHERE id=?''', tuple(data.values()) + (rec_id,))
    db.commit()
    return redirect(url_for('list_records'))

@app.route('/record/<int:rec_id>')
def view_record(rec_id):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM dispatches WHERE id=?', (rec_id,))
    row = cur.fetchone()
    if not row:
        abort(404)
    return render_template('report.html', row=row)

@app.route('/print/<int:rec_id>')
def print_record(rec_id):
    return view_record(rec_id)


if __name__ == "__main__":
    import os
    ensure_files()
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
