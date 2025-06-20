from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector as ms
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Database Connection Function
def get_db_connection():
    return ms.connect(host="localhost", user="root", password="nya@123", database="ngo_management")

# Login Required Decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']  # 'staff' or 'donor'
        email = request.form['email']
        password = request.form['password']

        con = get_db_connection()
        cur = con.cursor(dictionary=True)

        if user_type == 'staff':
            cur.execute("SELECT * FROM staff WHERE email = %s AND password = %s", (email, password))
        else:
            cur.execute("SELECT * FROM donors WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        con.close()

        if user:
            # Save user ID based on type
            session['user_id'] = user['staff_id'] if user_type == 'staff' else user['donor_id']
            session['user_type'] = user_type
            # Redirect staff to dashboard, donors to donation selection
            if user_type == 'staff':
                return redirect(url_for('staff_dashboard'))
            else:
                return redirect(url_for('donate'))
        else:
            return "Invalid email or password"

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------------------
# STAFF DASHBOARD AND INVENTORY (Protected Routes)
# ------------------------------

# Staff Dashboard (for staff only)
@app.route('/staff_dashboard')
@login_required
def staff_dashboard():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    
    con = get_db_connection()
    cur = con.cursor(dictionary=True)

    # Total monetary donations
    cur.execute("SELECT SUM(amount) AS total_donations FROM donations WHERE donation_type = 'monetary'")
    total_donations = cur.fetchone()['total_donations'] or 0

    # Total in-kind donation count
    cur.execute("SELECT COUNT(*) AS total_inkind FROM donations WHERE donation_type = 'in-kind'")
    total_inkind = cur.fetchone()['total_inkind'] or 0

    # Total inventory items
    cur.execute("SELECT COUNT(*) AS total_inventory_items FROM inventory;")
    total_items = cur.fetchone()['total_inventory_items'] or 0

    # Active donors count (distinct donor_id in donations)
    cur.execute("SELECT COUNT(DISTINCT donor_id) AS active_donors FROM donations")
    active_donors = cur.fetchone()['active_donors'] or 0

    # Recent 5 donations
    cur.execute("SELECT donor_id, donation_type, category, item, quantity, amount FROM donations ORDER BY donation_id DESC LIMIT 5")
    recent_donations = cur.fetchall()

    con.close()

    return render_template('staff_dashboard.html',
                           total_donations=total_donations,
                           total_inkind=total_inkind,
                           total_inventory=total_items,
                           active_donors=active_donors,
                           recent_donations=recent_donations)

# Display all inventory items (Staff Only)
@app.route('/')
@login_required
def index():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM inventory")
    data = cur.fetchall()
    con.close()
    return render_template('index.html', inventory=data)

# Add inventory item (Staff Only)
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        item_name = request.form['item_name']
        category = request.form['category']
        quantity = request.form['quantity']
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("INSERT INTO inventory (item_name, category, quantity) VALUES (%s, %s, %s)",
                    (item_name, category, quantity))
        con.commit()
        con.close()
        return redirect(url_for('index'))
    return render_template('add.html')

# Update inventory item (Staff Only)
@app.route('/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM inventory WHERE item_id = %s", (item_id,))
    item = cur.fetchone()
    con.close()
    if request.method == 'POST':
        quantity = request.form['quantity']
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("UPDATE inventory SET quantity = %s WHERE item_id = %s", (quantity, item_id))
        con.commit()
        con.close()
        return redirect(url_for('index'))
    return render_template('update.html', item=item)

# Delete inventory item (Staff Only)
@app.route('/delete/<int:item_id>')
@login_required
def delete_item(item_id):
    if session.get('user_type') != 'staff':
        return redirect(url_for('login'))
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM inventory WHERE item_id = %s", (item_id,))
    con.commit()
    con.close()
    return redirect(url_for('index'))

# ------------------------------
# DONOR DONATION ROUTES (Protected for Donors)
# ------------------------------

# Donation Selection Page (Donors Only)
@app.route('/donate')
@login_required
def donate():
    if session.get('user_type') != 'donor':
        return redirect(url_for('login'))
    return render_template('donate.html')

# In-Kind Donation (Donors Only)
@app.route('/donate/kind', methods=['GET', 'POST'])
@login_required
def donate_kind():
    if session.get('user_type') != 'donor':
        return redirect(url_for('login'))
    if request.method == 'POST':
        category = request.form['category']
        item = request.form['item']
        quantity = int(request.form['quantity'])
        anonymous = 'anonymous' in request.form

        con = get_db_connection()
        cur = con.cursor()

        # Insert donation record
        cur.execute("""
            INSERT INTO donations (donor_id, donation_type, category, item, quantity, anonymous)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session.get('user_id'), 'in-kind', category, item, quantity, anonymous))

        # Update inventory: Check if item exists
        cur.execute("SELECT quantity FROM inventory WHERE item_name = %s AND category = %s", (item, category))
        existing_item = cur.fetchone()
        if existing_item:
            new_quantity = existing_item[0] + quantity
            cur.execute("UPDATE inventory SET quantity = %s WHERE item_name = %s AND category = %s",
                        (new_quantity, item, category))
        else:
            cur.execute("INSERT INTO inventory (item_name, category, quantity) VALUES (%s, %s, %s)",
                        (item, category, quantity))

        con.commit()
        con.close()
        return redirect(url_for('donate'))
    return render_template('donate_kind.html')

# Monetary Donation (Donors Only)
@app.route('/donate/money', methods=['GET', 'POST'])
@login_required
def donate_money():
    if session.get('user_type') != 'donor':
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = request.form.get('amount')  
        payment_done = request.form.get('payment_done')  # Check if payment is confirmed
        
        if not amount:
            return "Error: Amount missing!"

        anonymous = 1 if 'anonymous' in request.form else 0

        # Debugging logs to check form data
        print("Received POST request:", request.form)

        if payment_done == "true":
            try:
                con = get_db_connection()
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO donations (donor_id, donation_type, amount, anonymous) 
                    VALUES (%s, %s, %s, %s)
                """, (session.get('user_id'), 'monetary', amount, anonymous))
                con.commit()
                con.close()
                
                return redirect(url_for('thank_you'))
            except Exception as e:
                print("Database Error:", e)
                return "Database Error!"

    return render_template('donate_money.html')




# Thank You Page
@app.route('/thank_you')
@login_required
def thank_you():
    return render_template('thank_you.html')


if __name__ == '__main__':
    app.run(debug=True)
