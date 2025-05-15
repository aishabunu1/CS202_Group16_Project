# CS202 Online Food Ordering System

## Setup Guide (For All Team Members)

### Prerequisites
1. **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
   - During installation:
     - Check "Add Python to PATH"
     - Select "Custom installation"
     - Enable "pip" and "for all users"

2. **MySQL**(we have already done this): [Download MySQL](https://dev.mysql.com/downloads/installer/)
   - Remember your root password
   - Install MySQL Workbench (optional but recommended)

3. **VS Code**: [Download VS Code](https://code.visualstudio.com/)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/CS202_Group16_Project.git
cd CS202_Group16_Project

### Step 2: 
Execute the DDL and DML scripts:
File > Open SQL Script > Select sql/OnlineFoodOrderingSystemDDL.sql > Run
Repeat for OnlineFoodOrderingSystemDML.sql

###Step 3: Install Dependencies
run in vscode terminal: python -m pip install -r requirements.txt

###Step 4: Run the application
run : python app.py
Access the site at: http://localhost:5000


Common Errors & Solutions
1. "ModuleNotFoundError: No module named 'flask'"
bash
# Reinstall dependencies
python -m pip uninstall flask mysql-connector-python
python -m pip install flask==2.1.3 mysql-connector-python==8.0.26

2. MySQL Connection Errors
Verify MySQL service is running (Windows: Services > MySQL)

Check credentials in db_connection.py

Test connection in MySQL Workbench first

3. "TemplateNotFound" Errors
Ensure all template files are in the exact templates/ folder

Case-sensitive names:

templates/auth/login.html ✅

Templates/Auth/Login.html ❌

4. Git Push Rejected
bash
git pull origin main
# Resolve any merge conflicts, then:
git push origin main

5. "Python not found" on Windows
Disable Microsoft Store alias:

Windows Search > "App Execution Aliases"

Turn off "Python" and "Python3" shortcuts

Reinstall Python with PATH enabled

First-Time Test
Register as a customer at http://localhost:5000/register

For Managers
Register as "restaurant_manager" account type

Access manager dashboard at http://localhost:5000/manager/dashboard
