from flask import Flask, render_template, redirect, url_for, session,flash, request

from database import insert_vehicles, fetch_vehicle, fetch_vehicles, update_vehicles, insert_vehicle_images, fetch_vehicle_images, insert_purchases, fetch_purchases,insert_user, fetch_user, check_user

from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "hdwsbdbewhdb"

bcrypt = Bcrypt(app)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/buy")
def buy():
    vehicles = fetch_vehicles()
    return render_template("buy.html", vehicles = vehicles)

@app.route("/sell")
def sell():
    return render_template("sell.html")

@app.route("/add_vehicles")
def add_vehicle():
    if request.method == "POST":
        make = request.form['make']
        model = request.form['make']
        year = request.form['year']
        new_vehicle = (make, model, year)
        insert_vehicles(new_vehicle)
        return redirect(url_for('home'))
    
@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['pass']
        role = request.form['role']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = check_user(email)
        
        if not user:
            new_user = (full_name, email, phone,hashed_password, role)
            insert_user(new_user)
            return redirect(url_for('home'))
        else:
            flash("Already Registered, Please Log in")
            return redirect(url_for('login'))
    return render_template('regsiter.html')

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        
        user = check_user(email)
        
        if not user:
            flash("Please regsiter to be a user", "error")
            return redirect(url_for('register'))
        else:
            if bcrypt.check_password_hash(user[3], password):
                session['email'] = email
                flash("Logged in successfully", "success")
                return redirect(url_for('home'))
            else:
                flash("Wrong password, Try again", "error")
                return redirect(url_for('login'))
    return render_template('login.html') 
        
app.run(debug=True)