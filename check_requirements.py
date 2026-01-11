#!/usr/bin/env python3
"""
Check what's needed for Superjoin assignment
"""
import subprocess
import sys

def check_mysql():
    """Check if MySQL is available"""
    print("🔍 Checking MySQL...")
    
    try:
        import mysql.connector
        print("✅ MySQL connector installed")
        
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password'
            )
            if connection.is_connected():
                print("✅ MySQL server is running and accessible")
                connection.close()
                return True
            else:
                print("❌ Cannot connect to MySQL server")
                return False
        except Exception as e:
            print(f"❌ MySQL connection failed: {e}")
            return False
            
    except ImportError:
        print("❌ MySQL connector not installed")
        return False

def check_python_deps():
    """Check Python dependencies"""
    print("\n🐍 Checking Python dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'sqlalchemy',
        'aiomysql',
        'google-api-python-client',
        'google-auth',
        'python-dotenv',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0

def check_frontend():
    """Check frontend setup"""
    print("\n🎨 Checking frontend...")
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm version: {result.stdout.strip()}")
            
            # Check if node_modules exists
            import os
            if os.path.exists('frontend/node_modules'):
                print("✅ Frontend dependencies installed")
                return True
            else:
                print("❌ Frontend dependencies not installed")
                print("   Run: cd frontend && npm install")
                return False
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False

def check_google_credentials():
    """Check Google credentials"""
    print("\n🔑 Checking Google credentials...")
    
    import os
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found")
        return True
    else:
        print("❌ credentials.json not found")
        return False

def main():
    """Main check function"""
    print("🔍 SUPERJOIN ASSIGNMENT - REQUIREMENTS CHECK")
    print("="*50)
    
    mysql_ok = check_mysql()
    python_ok = check_python_deps()
    frontend_ok = check_frontend()
    creds_ok = check_google_credentials()
    
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    if mysql_ok:
        print("✅ MySQL: Ready")
    else:
        print("❌ MySQL: NEEDS INSTALLATION")
        print("   📋 Install MySQL Server:")
        print("   Windows: https://dev.mysql.com/downloads/installer/")
        print("   Or use XAMPP: https://www.apachefriends.org/")
    
    if python_ok:
        print("✅ Python Dependencies: Ready")
    else:
        print("❌ Python Dependencies: Run 'pip install -r requirements.txt'")
    
    if frontend_ok:
        print("✅ Frontend: Ready")
    else:
        print("❌ Frontend: Run 'cd frontend && npm install'")
    
    if creds_ok:
        print("✅ Google Credentials: Ready")
    else:
        print("❌ Google Credentials: Add credentials.json file")
    
    print("\n" + "="*50)
    
    if mysql_ok and python_ok and frontend_ok and creds_ok:
        print("🎉 ALL REQUIREMENTS MET!")
        print("Run: python setup_mysql.py")
    else:
        print("⚠️ SOME REQUIREMENTS MISSING")
        print("Fix the issues above, then run this script again")
    
    return mysql_ok and python_ok and frontend_ok and creds_ok

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)