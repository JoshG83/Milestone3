# Milestone 3 - Enhanced PTO Management System

An enterprise-grade Paid Time Off (PTO) management system built with Flask, featuring RDS database integration, email notifications, and schedule generation.

## ✨ Features

- **Employee Sign-In** - Secure authentication via Employee ID
- **PTO Request Submission** - Submit time off requests with start/end dates and reason
- **Request History** - View all submitted PTO requests with status tracking
- **Email Notifications** - Automatic confirmation emails sent on submission
- **Schedule Generation** - Download company-wide schedule showing all employee PTO
- **Automatic Backup** - All schedules backed up to RDS for auditing

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (`.venv`)
- AWS RDS database access
- Gmail account (for email notifications)

### 1. Set Up Email (Optional but Recommended)

```bash
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"  # Generate at https://myaccount.google.com/apppasswords
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
```

### 2. Start the Application

```bash
cd /Users/joshuagoyette/Documents/Milestone3
.venv/bin/python app.py
```

### 3. Access the Application

- **Sign In:** http://localhost:5000/
- **PTO Form:** http://localhost:5000/pto
- **View Requests:** http://localhost:5000/requests
- **Download Schedule:** http://localhost:5000/schedule

## 📚 Documentation

- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Complete setup guide and feature overview
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Detailed technical implementation
- **[FEATURES_IMPLEMENTED.md](FEATURES_IMPLEMENTED.md)** - Feature descriptions and workflow
- **[CODE_CHANGES.md](CODE_CHANGES.md)** - Before/after code comparisons
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command and route reference
- **[DATABASE_SCHEMA.sql](DATABASE_SCHEMA.sql)** - SQL schema and useful queries

## 🗄️ Database Schema

### Requests Table
```sql
CREATE TABLE "UKG"."Requests" (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending'
);
```

### Backup_Storage Table
```sql
CREATE TABLE "UKG"."Backup_Storage" (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50),
    backup_data JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Workflow

```
1. Employee signs in with Employee ID
2. Fills out PTO form (dates + reason)
3. Submits request
   ├─ Stored in RDS PTO_Requests table
   ├─ Confirmation email sent
   └─ Success message displayed
4. Employee can view/manage requests
5. Download company schedule (JSON)
6. Schedule automatically backed up
```

## 📧 Email Setup (Free via Gmail)

1. Enable 2-Factor Authentication on Gmail
2. Generate App Password at https://myaccount.google.com/apppasswords
3. Set `SENDER_PASSWORD` environment variable to the generated password
4. Employees must have email on file in Employee table

## 📊 Schedule Format

Downloaded schedule is JSON with employee PTO dates:

```json
{
  "1001": {
    "name": "Alice Johnson",
    "pto_dates": ["2025-12-24", "2025-12-25"]
  },
  "1002": {
    "name": "Bob Smith",
    "pto_dates": []
  }
}
```

## 🛠️ Project Structure

```
Milestone3/
├── app.py                          # Flask application
├── static/
│   ├── css/
│   │   ├── formpage.scss          # Styles (source)
│   │   └── formpage.css           # Compiled styles
│   └── js/
│       └── formpage.js            # Client-side logic
├── templates/
│   ├── index.html                 # Sign-in page
│   ├── pto.html                   # PTO form
│   └── requests.html              # View requests
├── requirements.txt               # Python dependencies
└── [Documentation files]
```

## 🧪 Testing

1. Start the app: `.venv/bin/python app.py`
2. Sign in with an employee ID
3. Submit a PTO request
4. Check `/requests` to see all your submissions
5. Download schedule from `/schedule`
6. Verify data in RDS:
   ```sql
   SELECT * FROM "UKG"."Requests";
   SELECT * FROM "UKG"."Backup_Storage" WHERE backup_type='schedule';
   ```

## 📝 Environment Variables

```bash
# Email (Required for notifications)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Flask (Optional)
FLASK_SECRET=your-secret-key
```

## 🐛 Troubleshooting

**Email not sending?**
- Verify 2FA enabled and App Password generated correctly
- Check that employee has email in Employee table
- Look at Flask logs for SMTP errors

**Can't see requests?**
- Ensure you're signed in
- Verify PTO_Requests table exists in RDS
- Submit at least one request first

**Database connection issues?**
- Check RDS credentials in app.py
- Verify network access to RDS endpoint
- Run `init_db()` manually if tables missing

## 📦 Dependencies

- Flask 3.1.2
- psycopg2-binary 2.9.11 (PostgreSQL driver)
- sass (SCSS compiler)
- Built-in: smtplib, email, json, datetime

## 📄 License

Internal use for MIST4020 Systems Analysis and Design course

## 👤 Author

Joshua Goyette

## 🎯 Next Steps

See [FEATURES_IMPLEMENTED.md](FEATURES_IMPLEMENTED.md) for optional enhancement ideas including:
- Admin dashboard for request management
- Manager approval workflow
- Calendar view of schedules
- SMS notifications (Twilio)
