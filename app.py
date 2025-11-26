# For our Milestone 3 to work properly on the web, we will need to install many packages
# like Pythonk Flash, SASS, and Psycopg2 to connect with our AWS EC2 server that works with
# the AWS RDS that stores all of our information on employees, logins, requests etc.

# NOTE: Our Enhanced Scheduling System application is actively hosted at http://schedulingsystem.xyz/

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sass
import psycopg2
import psycopg2.extras

# Basic starting code for our flask app to get up and running properly.

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')

# AWS credentials that our program must have in order to access our EC2 server and in-turn our RDS database.

# ------------- Amazon Web Services RDS CONFIG  ------------- #
DB_HOST = "database-1.cluoyi622s3s.us-east-2.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "UKG_DB"
DB_USER = "JoshG83"
DB_PASSWORD = "K1E%*$zc7VF6YppVsYpG"

# We define a function that makes our connection to AWS EC2 possible and secure.

def AWS_connection():
    """Create a new DB connection to your AWS RDS Postgres."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


# In memory list of PTO requests, we will use this to test our PTO form submissions
pto_requests = []

# Another simple function that we declare which compiles our SCSS into CSS, since flask can
# only read CSS file format, but using SCSS makes writing CSS styles much easier.

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

# This function should run before any request on a webpage to help ensure our SCSS is correctly
# compiled to CSS formatting for the page. It's also important that this is happening in debug mode
# so that this is not running in production or during the websites uptime.

@app.before_request
def maybe_compile_assets():
    if app.debug:
        compile_scss_if_needed()

# This is the main way that our website functions, defining a homepage page route (http://schedulingsystem.xyz/)
# The if statement is there to check if the employee is already signed in to the website,
# and if they are they can be re-directed to the PTO page

@app.route('/', methods=['GET', 'POST'])
def homepage():
    # If already signed in, we will send the user to PTO page
    if session.get('employee_id'):
        return redirect(url_for('pto'))

# This if statement would double-check if the request method is POST, and if it is, it means that the Sign-in button
# has been selected. Then the employee ID is taken from the form and removing any unecessary spaces for good measure.
    if request.method == 'POST':
        emp_id_raw = request.form.get('employee_id', '').strip()

# If the form does not receive a proper employee ID either with invalid characters or a non-existent Id.
# The program sends back an error message to let the user know to try again.

        if not emp_id_raw:
            error = 'Please enter your Employee ID.'
            return render_template('index.html', error=error)

# This try statement is checking that the employee ID is actually a number and not in text format.
# If that is correct, the program continues to the next function, but will be thrown a ValueError if the ID
# is of the wrong data type. An error message is shwon to the user to try once more.

        try:
            emp_id = int(emp_id_raw)
        except ValueError:
            error = 'Employee ID must be a number.'
            return render_template('index.html', error=error)

        # Look up this employee in your RDS Employee table
    # We start by using our previously defined helper function to successfully make a connection to our AWS EC2 server
    # that allows us to access our RDS database. We then use something called a cursor to let us use SQL on our database.
    # Using our psycop2 library we can access DictCursor which allows us to get our SQL query results in the dictionary format.
        try:
            conn = AWS_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Here is the query that we run on our database in the SQL language that returns the employee ID and double check that
    # it matches with the employee ID previously entered into the form.

            query = """
                SELECT "Employee_ID",
                       "First_Name",
                       "Last_Name"
                FROM "UKG"."Employee"
                WHERE "Employee_ID" = %s;
            """
    # We run this query using the cursor that we defined, and we also pass the emp_id variable given by the user earlier.
    # The results are retrieved using the fetchone function since we will only need one result to match.
            cur.execute(query, (emp_id,))
            row = cur.fetchone()
    # Once we are finished with the database work, it's important to close the cursor and connection.
            cur.close()
            conn.close()
    # We make sure to place an except statement to catch errors that could possibly occur during the database connection.
        except Exception as e:
            app.logger.error("Database error during login: %s", e)
            error = 'Server/database error. Please try again later.'
            return render_template('index.html', error=error)
    # Simple if-statement to see if there was an employee matching an ID that was found in the database.
        if row:
            # Found a matching employee → log them in
            full_name = f"{row['First_Name']} {row['Last_Name']}"
            session['employee_id'] = row['Employee_ID']
            session['employee_name'] = full_name
            return redirect(url_for('pto'))
    # Else catch if the employee ID is not found and outputs an error onto the sign-in page.
        else:
            error = 'Employee ID not found. Please try again.'
            return render_template('index.html', error=error)

    # If for some reason the request method is anything other than post, we re-render the homepage.
    return render_template('index.html')

# This is the way that the PTO page route is defined and can be located at http://schedulingsystem.xyz/pto/
@app.route('/pto', methods=['GET', 'POST'])
# We define a function called pto that is responsible for handling all the PTO logic.
def pto():
# The first step of the PTO function is checking if the employee is signed in by searching for their ID in the session.
# If the employee is signed in at that time, the emp_id variable becomes the employee ID from the session.
    emp_id = session.get('employee_id')
    if not emp_id:
        return redirect(url_for('homepage'))

# We want to get the employee's name from the existing session so it can be displayed on the PTO page.

    employee_name = session.get('employee_name', 'Unknown')
# We first check if the request method is post, which means that the employee has submitted a PTO request.
    if request.method == 'POST':
        start = request.form.get('start_date', '').strip()
        end = request.form.get('end_date', '').strip()
        reason = request.form.get('reason', '').strip()
# We want to do a simple validation to make sure a valid start date and end date are provided.
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
        # Once the PTO request is submitted through the form, the user is given a success message.
        success = 'PTO request submitted.'
        return render_template('pto.html', employee_name=employee_name, success=success)

    return render_template('pto.html', employee_name=employee_name)

# Finally, we make sure to have a logout route made so employees can securely exit their PTO page session.
@app.route('/logout')
def logout():
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    return redirect(url_for('homepage'))

# Boilerplate code that needs to exist for the webpage to run on Flask.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)