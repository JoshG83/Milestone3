import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sass
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')

# ------------- RDS CONFIG (FILL THESE IN) -------------
DB_HOST = "database-1.cluoyi622s3s.us-east-2.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "UKG_DB"
DB_USER = "JoshG83"
DB_PASSWORD = "K1E%*$zc7VF6YppVsYpG"


def get_db_connection():
    """Create a new DB connection to your AWS RDS Postgres."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


# In-memory list of PTO requests (demo)
pto_requests = []


def compile_scss_if_needed():
    scss = os.path.join(app.root_path, 'static', 'css', 'formpage.scss')
    css = os.path.join(app.root_path, 'static', 'css', 'formpage.css')
    try:
        if not os.path.exists(css) or os.path.getmtime(scss) > os.path.getmtime(css):
            compiled = sass.compile(filename=scss, output_style='expanded')
            with open(css, 'w', encoding='utf-8') as f:
                f.write(compiled)
    except Exception as e:
        app.logger.error('SCSS compile error: %s', e)


@app.before_request
def maybe_compile_assets():
    # Only compile automatically in debug mode (development)
    if app.debug:
        compile_scss_if_needed()


@app.route('/', methods=['GET', 'POST'])
def home():
    # If already signed in, send to PTO page
    if session.get('employee_id'):
        return redirect(url_for('pto'))

    # Handle sign-in POST
    if request.method == 'POST':
        emp_id_raw = request.form.get('employee_id', '').strip()

        if not emp_id_raw:
            error = 'Please enter your Employee ID.'
            return render_template('index.html', error=error)

        # Employee_ID column is integer, so convert
        try:
            emp_id = int(emp_id_raw)
        except ValueError:
            error = 'Employee ID must be a number.'
            return render_template('index.html', error=error)

        # Look up this employee in your RDS Employee table
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            query = """
                SELECT "Employee_ID",
                       "First_Name",
                       "Last_Name"
                FROM "UKG"."Employee"
                WHERE "Employee_ID" = %s;
            """
            cur.execute(query, (emp_id,))
            row = cur.fetchone()

            cur.close()
            conn.close()

        except Exception as e:
            app.logger.error("Database error during login: %s", e)
            error = 'Server/database error. Please try again later.'
            return render_template('index.html', error=error)

        if row:
            # Found a matching employee → log them in
            full_name = f"{row['First_Name']} {row['Last_Name']}"
            session['employee_id'] = row['Employee_ID']
            session['employee_name'] = full_name
            return redirect(url_for('pto'))
        else:
            error = 'Employee ID not found. Please try again.'
            return render_template('index.html', error=error)

    # GET request
    return render_template('index.html')


@app.route('/pto', methods=['GET', 'POST'])
def pto():
    emp_id = session.get('employee_id')
    if not emp_id:
        return redirect(url_for('home'))

    employee_name = session.get('employee_name', 'Unknown')

    if request.method == 'POST':
        start = request.form.get('start_date', '').strip()
        end = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()
        if not start or not end:
            error = 'Please provide both start and end dates.'
            return render_template('pto.html', employee_name=employee_name, error=error)
        # Save request (demo)
        pto_requests.append({
            'employee_id': emp_id,
            'employee_name': employee_name,
            'start': start,
            'end': end,
            'reason': reason
        })
        success = 'PTO request submitted.'
        return render_template('pto.html', employee_name=employee_name, success=success)

    return render_template('pto.html', employee_name=employee_name)


@app.route('/logout')
def logout():
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)