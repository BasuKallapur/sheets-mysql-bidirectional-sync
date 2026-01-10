# Superjoin Sync MVP

**Simple bidirectional sync between Google Sheets and MySQL**

## 🚀 Quick Start

1. **Create Virtual Environment**

```bash
cd superjoin-sync
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Setup MySQL**

```bash
# Create database
mysql -u root -p
CREATE DATABASE superjoin_sync;
```

4. **Get Google Credentials**

- Go to Google Cloud Console
- Enable Sheets API
- Create Service Account
- Download JSON → save as `credentials.json`

5. **Run**

```bash
python -m uvicorn app.main:app --reload
```

6. **Test**

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## 📝 Usage

**Create sync:**

```bash
curl -X POST "http://localhost:8000/sync" \
-H "Content-Type: application/json" \
-d '{
  "sheet_id": "your_sheet_id",
  "sheet_name": "Sheet1",
  "table_name": "my_table",
  "column_mapping": {"Name": "name", "Email": "email"}
}'
```

**List syncs:**

```bash
curl "http://localhost:8000/sync"
```

## ✅ What it does

- ✅ Reads Google Sheets data
- ✅ Creates MySQL tables automatically
- ✅ Syncs data every 5 seconds
- ✅ Simple REST API
- ✅ Works with any sheet structure

That's it! No complexity, just working sync.

## 🛑 To Stop

```bash
# Deactivate virtual environment when done
deactivate
```
