# For our Milestone 3 to work properly on the web, we will need to install many packages
# like Pythonk Flash, SASS, and Psycopg2 to connect with our AWS EC2 server that works with
# the AWS RDS that stores all of our information on employees, logins, requests etc.
# Some other libraries were added later to assist with email notifications as well as making downloads of time off requests
# possible with CSV and JSON formats being imported.

# NOTE: Our Enhanced Scheduling System application is actively hosted at http://schedulingsystem.xyz/

import os
import json
import csv
import io
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sass
import psycopg2
import psycopg2.extras
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
# Basic starting code for our flask app to get up and running properly.

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')

# AWS credentials that our program must have in order to access our EC2 server and in-turn our RDS database.
# Made a later change in my code to use these enviornment variables for a more secure connection to the AWS EC2 server.
# These environment variables look on the local storage device for the credentials to access the server, so they don't have to be stored in memory.
# Defaults can be set for less sensitive fields.

# ------------- Amazon Web Services RDS CONFIG  ------------- #
DB_HOST = os.environ.get("DB_HOST", "database-1.cluoyi622s3s.us-east-2.rds.amazonaws.com")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME", "UKG_DB")
DB_USER = os.environ.get("DB_USER", "JoshG83")
DB_PASSWORD = os.environ.get("DB_PASSWORD")  # no default for password

# Same situation as above in order for emails to get sent out. 
# As far as emails go, I'm using a newly created Gmail account to send out request confirmations using SMTP.
# This function requires the use of an app password which can be an easy way to lose a Gmail account if not managed correctly.

# ------------- Email CONFIG (for notifications) ------------- #
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "4020schedulingsystem@gmail.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")  # no default for password

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

# We also define a basic email function that includes the recipients email, their name, and the start-end date of their PTO.
# An email layout is then given where some fields are automatically filled with the variables inside of the function.

def send_email(recipient_email, employee_name, start_date, end_date):
    """Send a confirmation email to the employee after PTO request submission."""
    try:
        subject = "PTO Request Confirmation"
        body = f"""
Dear {employee_name},

Your PTO request has been successfully submitted.

Request Details:
- Start Date: {start_date}
- End Date: {end_date}
- Status: Pending

You can view all your PTO requests by logging into your account.

Best regards,
UKG Enhanced Scheduling System
        """
        # We reference the SMTP library here to send out the email using variables defined earlier.

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # This section is where the sendoff of the email occurs utilizing SMTP.
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        # Simple check to ensure that the email was sent successfully and greets the user with a success message.
        # The opposite happens if the email fails to send for any reason.

        app.logger.info(f"Email sent to {recipient_email}")
        return True
    except Exception as e:
        app.logger.error(f"Error sending email: {e}")
        return False

#  This is a function we defined that initializes our database tables if they do not exist in the RDS database for any reason.

def init_db():
    """Initialize database tables if they don't exist."""
    try:
        conn = AWS_connection()
        cur = conn.cursor()
        
        # This cursor function call creates a Requests table if it doesn't exist, and several columns are defined for the Requests table.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "UKG"."Requests" (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'pending'
            );
        """)
        
        # This cursor function call creates a Backup_Storage table if it doesn't exist and also fills in the table with several necesssary columns.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "UKG"."Backup_Storage" (
                id SERIAL PRIMARY KEY,
                backup_type VARCHAR(50),
                backup_data JSON,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # We use a few function calls to commit the changes to the database as well as closing both the cursor and the connection.
        # We log a success message when and if the tables are successfully created or picked up by the cursor function, and an error message is given if something goes wrong.
        conn.commit()
        cur.close()
        conn.close()
        app.logger.info("Database tables initialized successfully")
    except Exception as e:
        app.logger.error(f"Database initialization error: {e}")


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
        
        # This code block is going to ensure that PTO requests submitted are legitimate and at least 1 day ahead of the system time/date.
        # This prevents bad data from being entered and stored into the EC2 server and also the AWS RDS.
        # The try statement achieves just that, defining clear start and end dates, as well as today and tomorrow variables using system time.
        # The rest are simple if statements that check if the start date is at the very least one day ahead of when the report is being submitted.
        # If not, the user will be presented an error and must enter valid dates.
        try:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            if start_date < tomorrow:
                error = 'PTO requests must be submitted at least 1 day in advance. Please select a start date no earlier than tomorrow.'
                return render_template('pto.html', employee_name=employee_name, error=error)
            
            if end_date < start_date:
                error = 'End date cannot be before start date.'
                return render_template('pto.html', employee_name=employee_name, error=error)
        except ValueError:
            error = 'Invalid date format. Please use the date picker.'
            return render_template('pto.html', employee_name=employee_name, error=error)
        
        # Insert PTO request into RDS database
        try:
            conn = AWS_connection()
            cur = conn.cursor()
        # We create a variables called insert_query to act as SQL code that is tasked with inserting the PTO request into the Requests table.
            insert_query = """
                INSERT INTO "UKG"."Requests" (employee_id, start_date, end_date, reason, status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id;
            """
        # We execute the query using the cursor and filling in necessary variables for successful execution.
            cur.execute(insert_query, (emp_id, start, end, reason))
            conn.commit()
            
            # Get employee email from UKG.Employee table to send notification, matches the employee ID.
            email_query = """
                SELECT "Email"
                FROM "UKG"."Employee"
                WHERE "Employee_ID" = %s;
            """
            # Execute the email query passing in necessary variables, and also using fetchone to get the result.
            cur.execute(email_query, (emp_id,))
            email_row = cur.fetchone()
            employee_email = email_row[0] if email_row else None
            
            cur.close()
            conn.close()
            
            # Send email notification if email exists
            if employee_email:
                send_email(employee_email, employee_name, start, end)
            
            # Once the PTO request is submitted through the form, the user is given a success message.
            success = 'PTO request submitted successfully. A confirmation email has been sent.'
            return render_template('pto.html', employee_name=employee_name, success=success)
            
        ## Error catching statement in case something goes wrong while the database is being accessed.
        ## We utilize traceback to get a full error log for debugging purposes.

        except Exception as e:
            app.logger.error(f"Error inserting PTO request: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
            error = f'Error submitting PTO request: {str(e)}'
            return render_template('pto.html', employee_name=employee_name, error=error)

    return render_template('pto.html', employee_name=employee_name)


# Route to view all PTO requests submitted by the logged-in employee
# The view_requests function is defined that deals with the logic of viewing the created PTO requests.
# emp_id receives the employee ID that is stored in the session, and if there is no employee ID the user is redirected.

@app.route('/requests')
def view_requests():
    emp_id = session.get('employee_id')
    if not emp_id:
        return redirect(url_for('homepage'))
    
# employee_name receives the employee name from the session, which would use the employee ID to receive the employee name from the database.

    employee_name = session.get('employee_name', 'Unknown')
    requests_list = []
    
    # We connect to the AWS RDS database to fetch all of the TPO requests that match the employee ID of the logged in user.

    try:
        conn = AWS_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = """
            SELECT id, start_date, end_date, reason, status, created_at
            FROM "UKG"."Requests"
            WHERE employee_id = %s
            ORDER BY created_at DESC;
        """
        # The query is executed using the cursor and passed variables.
        cur.execute(query, (emp_id,))
        requests_list = cur.fetchall()
        
        # We close the cursor and connection and adding a standard error catcher for debugging.
        cur.close()
        conn.close()
    except Exception as e:
        app.logger.error(f"Error fetching PTO requests: {e}")
        flash('Error loading your requests.', 'error')
    
    return render_template('requests.html', employee_name=employee_name, requests=requests_list)


# Route to generate schedule (CSV/JSON) with all employees and their PTO
@app.route('/schedule')
def generate_schedule():
    emp_id = session.get('employee_id')
    if not emp_id:
        flash('Please log in to download the schedule.', 'error')
        return redirect(url_for('homepage'))
    
    try:
        conn = AWS_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Fetch all PTO requests with employee information joined
        pto_query = """
            SELECT 
                e."Employee_ID",
                e."First_Name",
                e."Last_Name",
                r.start_date,
                r.end_date,
                r.reason,
                r.status
            FROM "UKG"."Requests" r
            JOIN "UKG"."Employee" e ON r.employee_id = e."Employee_ID"
            WHERE r.status = 'pending' OR r.status = 'approved'
            ORDER BY e."Employee_ID", r.start_date;
        """
        cur.execute(pto_query)
        pto_requests = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Create CSV file in memory (probably wouldn't be good in production but works for now with small databases)
        output = io.StringIO()
        csv_writer = csv.writer(output)
        
        # Write header row (writing a proper header for the CSV file)
        csv_writer.writerow(['Employee ID', 'Employee Name', 'Start Date', 'End Date', 'Reason', 'Status'])
        
        # Write each PTO request as a row
        for req in pto_requests:
            employee_name = f"{req['First_Name']} {req['Last_Name']}"
            csv_writer.writerow([
                req['Employee_ID'],
                employee_name,
                req['start_date'],
                req['end_date'],
                req['reason'] or 'N/A',
                req['status'].capitalize()
            ])
        
        # Convert StringIO to BytesIO for sending
        output.seek(0)
        bytes_output = io.BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        
        # Return the CSV file as a downloadable file for the user
        return send_file(
            bytes_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='pto_schedule.csv'
        )
    except Exception as e:
        import traceback
        app.logger.error(f"Error generating schedule: {e}")
        app.logger.error(traceback.format_exc())
        flash(f'Error generating schedule: {str(e)}', 'error')
        return redirect(url_for('pto'))

# Finally, we make sure to have a logout route made so employees can securely exit their PTO page session.
@app.route('/logout')
def logout():
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    return redirect(url_for('homepage'))

# Boilerplate code that needs to exist for the webpage to run on Flask.
if __name__ == '__main__':
    # Initialize database tables on startup
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)