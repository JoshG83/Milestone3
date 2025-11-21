import os
from flask import Flask, render_template, request, redirect, url_for, session
import sass

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')

# Simple in-memory employee store for demo purposes
employees = {
    '1001': 'Alice Johnson',
    '1002': 'Bob Smith',
    '12345': 'Charlie Example'
}

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
        emp_id = request.form.get('employee_id', '').strip()
        if emp_id and emp_id in employees:
            session['employee_id'] = emp_id
            return redirect(url_for('pto'))
        error = 'Invalid employee ID. Please try again.'
        return render_template('index.html', error=error)

    return render_template('index.html')


@app.route('/pto', methods=['GET', 'POST'])
def pto():
    emp_id = session.get('employee_id')
    if not emp_id:
        return redirect(url_for('home'))

    employee_name = employees.get(emp_id, 'Unknown')

    if request.method == 'POST':
        start = request.form.get('start_date', '').strip()
        end = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()
        if not start or not end:
            error = 'Please provide both start and end dates.'
            return render_template('pto.html', employee_name=employee_name, error=error)
        # Save request (demo)
        pto_requests.append({'employee_id': emp_id, 'employee_name': employee_name, 'start': start, 'end': end, 'reason': reason})
        success = 'PTO request submitted.'
        return render_template('pto.html', employee_name=employee_name, success=success)

    return render_template('pto.html', employee_name=employee_name)


@app.route('/logout')
def logout():
    session.pop('employee_id', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)