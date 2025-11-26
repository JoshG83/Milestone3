# Implementation Guide: Complete PTO System

## Features Implemented

### 1. **PTO Request Storage in RDS**
- **Table:** `UKG.Requests`
- **Columns:** id, employee_id, start_date, end_date, reason, created_at, status
- **Functionality:** When an employee submits a PTO request on `/pto`, it's now stored in the RDS database instead of in-memory
- **Auto-created:** Tables are automatically created on app startup via `init_db()`

### 2. **View Your PTO Requests**
- **Route:** `/requests`
- **Template:** `templates/requests.html`
- **Features:**
  - Displays all PTO requests submitted by the logged-in employee
  - Shows start date, end date, reason, status, and submission timestamp
  - Status badges indicate `pending`, `approved`, or `denied`
  - Links to submit new requests and download schedules

### 3. **Email Notifications**
- **Functionality:** When a PTO request is submitted, an email confirmation is automatically sent to the employee's registered email in the `UKG.Employee` table
- **Configuration:** Uses SMTP (Gmail by default, free via App Passwords)
- **Environment Variables Required:**
  ```bash
  export SMTP_SERVER=smtp.gmail.com
  export SMTP_PORT=587
  export SENDER_EMAIL=your-email@gmail.com
  export SENDER_PASSWORD=your-app-password
  ```
- **Setup Instructions (Gmail):**
  1. Enable 2-Factor Authentication on your Gmail account
  2. Generate an App Password at https://myaccount.google.com/apppasswords
  3. Use that password in `SENDER_PASSWORD` env var

### 4. **Schedule Generation & Export**
- **Route:** `/schedule`
- **Output:** JSON file with all employees and their PTO dates
- **Features:**
  - Fetches all employees from `UKG.Employee`
  - Fetches all approved/pending PTO requests
  - Generates a day-by-day breakdown of who is out
  - Downloads as `schedule.json`
- **JSON Structure:**
  ```json
  {
    "1001": {
      "name": "Alice Johnson",
      "pto_dates": ["2025-12-25", "2025-12-26"]
    },
    "1002": {
      "name": "Bob Smith",
      "pto_dates": []
    }
  }
  ```

### 5. **Schedule Backups to RDS**
- **Table:** `UKG.Backup_Storage`
- **Columns:** id, backup_type, backup_data (JSON), created_at
- **Functionality:** Every time a schedule is generated, a backup is automatically stored in the RDS database
- **Retrieval:** You can query the backups table later to view historical snapshots

---

## Database Schema

Run these SQL commands in your RDS to verify/create the tables manually (if needed):

```sql
-- Requests Table
CREATE TABLE IF NOT EXISTS "UKG"."Requests" (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending'
);

-- Backups Table
CREATE TABLE IF NOT EXISTS "UKG"."Backups" (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50),
    backup_data JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## File Changes Summary

### `app.py`
- **Added imports:** `json`, `csv`, `io`, `datetime`, `send_file`, `smtplib`, `email.mime`
- **Added functions:**
  - `send_email()` — sends confirmation emails via SMTP
  - `init_db()` — creates PTO_Requests and Backups tables on startup
- **Updated route `/pto` (POST):**
  - Now inserts PTO requests into RDS instead of in-memory
  - Fetches employee email and sends notification
- **New routes:**
  - `GET /requests` — displays all user's PTO requests
  - `GET /schedule` — generates and downloads JSON schedule, stores backup

### `templates/requests.html` (NEW)
- Shows a table of all employee's submitted PTO requests
- Displays status, dates, reason, and submission time
- Links to submit new requests and download schedules

### `templates/pto.html`
- Added navigation links to view requests and download schedule
- Added email confirmation message to success message

---

## Testing the Features

### 1. Test PTO Storage in RDS
```bash
# Sign in with an employee ID
# Submit a PTO request
# Check RDS: SELECT * FROM "UKG"."PTO_Requests";
```

### 2. Test View Requests Page
```bash
# After signing in and submitting a PTO request
# Click "View Your Requests" link on the PTO page
# Should see all your submitted requests
```

### 3. Test Email Notifications
- Ensure `SENDER_EMAIL`, `SENDER_PASSWORD` env vars are set correctly
- Submit a PTO request
- Check the employee's inbox for confirmation email

### 4. Test Schedule Generation
```bash
# Click "Download Schedule" on the PTO page
# Should download a schedule.json file
   # Check RDS: SELECT * FROM "UKG"."Backup_Storage" WHERE backup_type='schedule';
```

---

## Configuration Checklist

- [ ] Set environment variables for email (SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD)
- [ ] Verify RDS database has Employee table with "Email" column
- [ ] Test sign-in with an employee ID
- [ ] Submit a test PTO request
- [ ] Check that email was sent
- [ ] Visit `/requests` to see submitted requests
- [ ] Download schedule and verify JSON format
- [ ] Check RDS Backups table for stored schedule

---

## Optional Enhancements

1. **SMS Notifications**: Integrate Twilio (paid) or AWS SNS for SMS alerts
2. **CSV Export**: Add CSV format option alongside JSON
3. **Schedule UI**: Create a calendar view instead of JSON download
4. **Admin Dashboard**: Create an admin route to view all PTO requests and approve/deny them
5. **Status Updates**: Allow employees to receive email notifications when their request is approved/denied

---

## Troubleshooting

**Email not sending?**
- Verify SENDER_PASSWORD is an App Password, not your Gmail password
- Check that 2FA is enabled on Gmail account
- Verify employee has an email in the Employee table

**Schedule generation error?**
- Ensure all employees have Employee_IDs in the Employee table
- Check that PTO dates are in valid DATE format (YYYY-MM-DD)

**Can't see requests?**
- Verify you're signed in (session['employee_id'] is set)
- Check that PTO_Requests table exists in RDS
- Query: `SELECT * FROM "UKG"."PTO_Requests" WHERE employee_id = <your_id>;`
