# MySQL Setup Guide - Superjoin Assignment

## 🎯 Assignment Requirement: MySQL Database

The assignment specifically requires **MySQL database**, not SQLite. Here's how to set it up.

---

## 📋 Prerequisites

### **1. Install MySQL Server**

#### **Windows:**

1. Download MySQL Installer: https://dev.mysql.com/downloads/installer/
2. Run installer and select "MySQL Server"
3. Choose "Development Computer" setup
4. Set root password as: `password` (or update .env file)
5. Complete installation

#### **macOS:**

```bash
# Using Homebrew
brew install mysql
brew services start mysql

# Set root password
mysql_secure_installation
```

#### **Linux (Ubuntu):**

```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

### **2. Verify MySQL Installation**

```bash
mysql --version
mysql -u root -p
```

---

## 🚀 Quick Setup

### **Step 1: Install Dependencies**

```bash
# Activate virtual environment
venv\Scripts\activate

# Install updated requirements (includes MySQL connector)
pip install -r requirements.txt
```

### **Step 2: Configure Database Connection**

Your `.env` file is already configured:

```env
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/superjoin_sync
GOOGLE_CREDENTIALS_FILE=credentials.json
```

**Update the password if different:**

- Change `password` to your MySQL root password

### **Step 3: Setup MySQL Database**

```bash
python setup_mysql.py
```

**Expected Output:**

```
🔧 Setting up MySQL database...
✅ Database 'superjoin_sync' created/verified
✅ MySQL connection test successful
✅ MySQL setup completed successfully!
📊 Initializing application database...
✅ Application database initialized
⚙️ Creating sample sync configuration...
✅ Created sync configuration: [config-id]
🔄 Testing initial sync...
✅ Initial Sheet→DB sync completed
✅ Initial DB→Sheet sync completed
🎉 MySQL setup completed successfully!
```

---

## 🧪 Test MySQL Connection

### **Test 1: Quick Connection Test**

```bash
python -c "
import mysql.connector
try:
    conn = mysql.connector.connect(host='localhost', user='root', password='password', database='superjoin_sync')
    print('✅ MySQL connection successful')
    conn.close()
except Exception as e:
    print(f'❌ MySQL connection failed: {e}')
"
```

### **Test 2: Application Test**

```bash
python quick_test.py
```

---

## 🖥️ View MySQL Database

### **Option 1: MySQL Workbench (Recommended)**

1. Download: https://dev.mysql.com/downloads/workbench/
2. Install and open
3. Connect to: `localhost:3306`
4. Username: `root`, Password: `password`
5. Navigate to `superjoin_sync` database
6. View `employees` table

### **Option 2: Command Line**

```bash
mysql -u root -p
USE superjoin_sync;
SHOW TABLES;
SELECT * FROM employees;
```

### **Option 3: phpMyAdmin (Web Interface)**

1. Install XAMPP or WAMP (includes phpMyAdmin)
2. Access: http://localhost/phpmyadmin
3. Login with root credentials
4. Navigate to `superjoin_sync` database

---

## 🔄 Test Bidirectional Sync

### **Test 1: Sheet → MySQL**

1. Edit Google Sheet: https://docs.google.com/spreadsheets/d/1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI/edit
2. Run: `python quick_test.py`
3. Check MySQL database in Workbench
4. Verify changes appear

### **Test 2: MySQL → Sheet**

1. Edit data in MySQL Workbench
2. Run: `python quick_test.py`
3. Refresh Google Sheet
4. Verify changes appear

---

## 🚀 Start Application

### **Backend:**

```bash
python -m uvicorn app.main:app --reload
```

### **Frontend:**

```bash
cd frontend
npm run dev
```

### **Access:**

- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 🔧 Troubleshooting

### **Error: "Access denied for user 'root'"**

**Solution:**

```bash
# Reset MySQL root password
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

### **Error: "Can't connect to MySQL server"**

**Solutions:**

1. Start MySQL service:

   - Windows: Services → MySQL → Start
   - macOS: `brew services start mysql`
   - Linux: `sudo systemctl start mysql`

2. Check if MySQL is running:

   ```bash
   # Windows
   net start mysql

   # macOS/Linux
   sudo systemctl status mysql
   ```

### **Error: "Unknown database 'superjoin_sync'"**

**Solution:**

```bash
python setup_mysql.py  # This creates the database
```

### **Error: "Module 'aiomysql' not found"**

**Solution:**

```bash
pip install -r requirements.txt  # Reinstall dependencies
```

---

## ✅ Verification Checklist

- [ ] MySQL server installed and running
- [ ] Database `superjoin_sync` created
- [ ] Python dependencies installed
- [ ] `python setup_mysql.py` completed successfully
- [ ] `python quick_test.py` shows ✅ for both sync directions
- [ ] Web dashboard accessible at http://localhost:3000
- [ ] MySQL Workbench can connect and view data

---

## 🎯 Assignment Compliance

**Now your system uses:**

- ✅ **MySQL Database** (as required)
- ✅ **Google Sheets API**
- ✅ **Live 2-way sync**
- ✅ **Production-quality code**
- ✅ **Web interface for testing**

**Perfect for Superjoin assignment submission! 🚀**
