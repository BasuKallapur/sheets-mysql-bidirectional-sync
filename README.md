# Superjoin Sync MVP

**Bidirectional sync between Google Sheets and SQLite Database**

A clean, working implementation of real-time data synchronization for the Superjoin internship project.

## 🎯 Current Status: WORKING ✅

- ✅ **Google Sheets ↔ SQLite Database** bidirectional sync
- ✅ **Real-time sync** with manual trigger scripts
- ✅ **Database Browser** integration for testing
- ✅ **FastAPI backend** with REST endpoints
- ✅ **Clean project structure** ready for submission

## 🚀 Quick Start

### 1. **Setup Environment**

```bash
# Clone and navigate to project
cd sheets-mysql-bidirectional-sync

# Activate virtual environment (already created)
venv\Scripts\activate  # Windows
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Setup Google Credentials**

- Place your `credentials.json` file in the project root
- Ensure Google Sheets API is enabled for your service account

### 4. **Database Setup**

The project uses **SQLite** (not MySQL) for simplicity:

- Database file: `superjoin_sync.db`
- Tables created automatically
- Use **DB Browser for SQLite** to view/edit data

## 🔄 How to Test Sync

### **Method 1: Manual Sync Scripts**

**Test Google Sheet → Database:**

```bash
python debug_sheet_to_db.py
```

**Test Database → Google Sheet:**

```bash
python debug_db_to_sheet.py
```

**Test Both Directions:**

```bash
python test_sync_now.py
```

### **Method 2: Using DB Browser**

1. **Open DB Browser for SQLite**
2. **Open Database:** `superjoin_sync.db`
3. **Browse Data:** View/edit the `employees` table
4. **Run sync script** to see changes in Google Sheet
5. **Edit Google Sheet** and run sync to see changes in DB Browser

## 📊 Current Sync Configuration

- **Sheet ID:** `1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI`
- **Sheet Name:** `Sheet1`
- **Table Name:** `employees`
- **Column Mapping:**
  ```json
  {
    "Name": "name",
    "Email": "email",
    "Age": "age",
    "City": "city"
  }
  ```

## 🛠️ Project Structure

```
📁 sheets-mysql-bidirectional-sync/
├── 📁 app/
│   ├── __init__.py           # Package init
│   ├── config.py            # Configuration settings
│   ├── database.py          # SQLite connection
│   ├── main.py             # FastAPI application
│   ├── models.py           # Database models
│   ├── mysql.py            # Database service (SQLite)
│   ├── sheets.py           # Google Sheets service
│   └── sync.py             # Bidirectional sync logic
├── 📁 frontend/            # React frontend (optional)
├── 📁 venv/               # Virtual environment
├── .env                   # Environment variables
├── .env.example          # Environment template
├── credentials.json       # Google service account
├── superjoin_sync.db     # SQLite database
├── test_sync_now.py      # Test both sync directions
├── debug_sheet_to_db.py  # Test Sheet → DB sync
├── debug_db_to_sheet.py  # Test DB → Sheet sync
└── README.md            # This file
```

## 🎯 Features Implemented

### ✅ **Core Functionality**

- **Bidirectional Sync:** Google Sheets ↔ Database
- **Automatic Table Creation:** Based on sheet headers
- **Column Mapping:** Flexible field mapping
- **Data Validation:** Ensures data integrity
- **Error Handling:** Robust error management

### ✅ **Technical Features**

- **FastAPI Backend:** Modern async Python framework
- **SQLite Database:** Lightweight, file-based database
- **Google Sheets API:** Official Google integration
- **Async Operations:** Non-blocking sync operations
- **Clean Architecture:** Modular, maintainable code

### ✅ **Testing & Debugging**

- **Manual Sync Scripts:** For testing and debugging
- **DB Browser Integration:** Visual database management
- **Detailed Logging:** Track sync operations
- **Error Reporting:** Clear error messages

## 🚀 API Endpoints

**Start the server:**

```bash
python -m uvicorn app.main:app --reload
```

**Available endpoints:**

- `GET /` - Health check
- `POST /sync` - Create new sync configuration
- `GET /sync` - List all sync configurations
- `GET /docs` - API documentation

## 🧪 Testing Workflow

1. **Edit Google Sheet** → Add/modify data
2. **Run:** `python debug_sheet_to_db.py`
3. **Check DB Browser** → Verify changes synced
4. **Edit in DB Browser** → Add/modify records
5. **Run:** `python debug_db_to_sheet.py`
6. **Check Google Sheet** → Verify changes synced

## 🎉 Demo Ready

This project is **submission-ready** for the Superjoin internship with:

- ✅ **Working bidirectional sync**
- ✅ **Clean, professional codebase**
- ✅ **Comprehensive documentation**
- ✅ **Easy testing and demonstration**
- ✅ **Modern tech stack**
- ✅ **Scalable architecture**

## 🛑 Notes

- Uses **SQLite** instead of MySQL for simplicity
- **Manual sync triggers** for reliable testing
- **DB Browser for SQLite** recommended for database management
- All test files and unnecessary code removed for clean submission
