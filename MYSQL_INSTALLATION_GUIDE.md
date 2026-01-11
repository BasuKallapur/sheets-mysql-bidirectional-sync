# MySQL Installation Guide for Windows

## 🎯 You Need MySQL Server for the Assignment

The Superjoin assignment specifically requires MySQL database. Here's how to install it on Windows:

---

## 📥 Step 1: Download MySQL

1. **Go to:** https://dev.mysql.com/downloads/installer/
2. **Download:** `mysql-installer-community-8.0.xx.x.msi` (larger file ~400MB)
3. **Click:** "No thanks, just start my download"

---

## 🔧 Step 2: Install MySQL

1. **Run the installer** as Administrator
2. **Choose Setup Type:** "Developer Default" (recommended)
3. **Check Requirements:** Install any missing requirements
4. **Installation:** Click "Execute" to install all components
5. **Configuration:**
   - **Config Type:** Development Computer
   - **Authentication:** Use Strong Password Encryption
   - **Root Password:** Set to `password` (or remember what you set)
   - **Windows Service:** Keep default settings
6. **Apply Configuration:** Click "Execute"
7. **Complete Installation**

---

## ✅ Step 3: Verify Installation

### **Option 1: MySQL Workbench**

1. Open "MySQL Workbench" from Start Menu
2. Click on "Local instance MySQL80"
3. Enter password: `password`
4. If it connects, MySQL is working!

### **Option 2: Command Line**

```cmd
mysql -u root -p
# Enter password: password
# You should see: mysql>
```

### **Option 3: Windows Services**

1. Press `Win + R`, type `services.msc`
2. Look for "MySQL80" service
3. Status should be "Running"

---

## 🚀 Step 4: Run Your Application

Once MySQL is installed and running:

```bash
# Test MySQL connection
python test_mysql_connection.py

# Setup database and application
python setup_mysql.py

# Start your application
python -m uvicorn app.main:app --reload
```

---

## 🔧 Troubleshooting

### **Error: "Access denied for user 'root'"**

**Solution 1:** Update your `.env` file with correct password:

```env
DATABASE_URL=mysql+aiomysql://root:YOUR_ACTUAL_PASSWORD@localhost:3306/superjoin_sync
```

**Solution 2:** Reset MySQL root password:

1. Open MySQL Workbench
2. Go to Server → Users and Privileges
3. Select root user
4. Set password to `password`

### **Error: "Can't connect to MySQL server"**

**Solutions:**

1. **Start MySQL Service:**

   - Press `Win + R`, type `services.msc`
   - Find "MySQL80", right-click → Start

2. **Check if MySQL is running:**
   ```cmd
   netstat -an | findstr 3306
   ```
   Should show: `0.0.0.0:3306`

### **Error: "MySQL command not found"**

**Solution:** Add MySQL to PATH:

1. Find MySQL installation (usually `C:\Program Files\MySQL\MySQL Server 8.0\bin`)
2. Add to Windows PATH environment variable
3. Restart command prompt

---

## 🎯 Alternative: Quick MySQL with XAMPP

If you want a simpler installation:

1. **Download XAMPP:** https://www.apachefriends.org/download.html
2. **Install XAMPP** (includes MySQL)
3. **Start MySQL** from XAMPP Control Panel
4. **Default credentials:** root (no password)
5. **Update .env:**
   ```env
   DATABASE_URL=mysql+aiomysql://root:@localhost:3306/superjoin_sync
   ```

---

## ✅ Once MySQL is Running

Your assignment will work perfectly with:

- ✅ **MySQL Database** (as required by assignment)
- ✅ **Live 2-way sync** between Google Sheets and MySQL
- ✅ **Production-quality code**
- ✅ **Web interface for testing**

**This meets the exact assignment requirements! 🎯**
