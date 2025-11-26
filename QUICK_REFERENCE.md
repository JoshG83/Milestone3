# Quick Reference: New Features

## Routes Added

| Route | Method | Purpose |
|-------|--------|---------|
| `/requests` | GET | View all your submitted PTO requests |
| `/schedule` | GET | Generate and download JSON schedule with all employees' PTO |

## Database Tables Created

| Table | Columns | Purpose |
|-------|---------|---------|
| `UKG.Requests` | id, employee_id, start_date, end_date, reason, created_at, status | Stores all PTO requests |
| `UKG.Backup_Storage` | id, backup_type, backup_data, created_at | Stores backups of schedules |

## Environment Variables (for Email)

```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## What Happens on PTO Submit

1. ✅ Request is saved to `UKG.PTO_Requests` table
2. ✅ Employee's email is fetched from `UKG.Employee`
3. ✅ Confirmation email is sent automatically
4. ✅ Success message displays on page

## Schedule JSON Structure

```json
{
  "1001": {
    "name": "Alice Johnson",
    "pto_dates": ["2025-12-24", "2025-12-25", "2025-12-26"]
  },
  "1002": {
    "name": "Bob Smith",
    "pto_dates": []
  }
}
```

## User Navigation

```
Sign In (/) 
  ↓
PTO Form (/pto) 
  ├─→ View Your Requests (/requests)
  ├─→ Download Schedule (/schedule)
  └─→ Sign Out (/)
```

## Testing Commands

```bash
# 1. Start the app
python app.py

# 2. Test PTO storage
curl -X POST http://localhost:5000/pto \
  -d "start_date=2025-12-24&end_date=2025-12-26&reason=Holiday"

# 3. View requests
curl http://localhost:5000/requests

# 4. Download schedule
curl http://localhost:5000/schedule -o schedule.json
```
