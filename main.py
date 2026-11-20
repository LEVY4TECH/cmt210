import os
import uuid
from werkzeug.utils import secure_filename

from flask import Flask, render_template, redirect, url_for, session,flash, request

from database import insert_vehicles, fetch_vehicle, fetch_vehicles, insert_vehicle_images, fetch_vehicle_images, insert_user, fetch_user, check_user

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

@app.route('/vehicle/<int:vehicle_id>')
def vehicle_details(vehicle_id):

    vehicle = fetch_vehicle(vehicle_id)

    if not vehicle:
        flash("Vehicle not found.")
        return redirect(url_for('buy'))

    images = fetch_vehicle_images(vehicle_id)

    seller = fetch_user(vehicle[1])

    return render_template(
        'vehicle_details.html',
        vehicle=vehicle,
        images=images,
        seller=seller
    )

@app.route("/sell")
def sell():
    return render_template("sell.html")

# UPLOADING A VEHICLE IN THE SELL'S PAGE
@app.route("/add_vehicles", methods=['GET', 'POST'])
def add_vehicle():

    if 'email' not in session:
        flash("Please log in before selling a vehicle.")
        return redirect(url_for('login'))

    if request.method == 'POST':

        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        price = request.form['price']

        # Connect each frontend input to its image category
        image_fields = {
            'front_image': 'front',
            'rear_image': 'rear',
            'left_image': 'left',
            'right_image': 'right',
            'engine_image': 'engine',
            'boot_image': 'boot'
        }

        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}

        uploaded_images = []

        # Collect and validate the selected pictures
        for field, image_type in image_fields.items():

            image = request.files.get(field)

            if image and image.filename:

                filename = secure_filename(image.filename)

                if '.' not in filename:
                    flash("Invalid image file.")
                    return redirect(url_for('sell'))

                extension = filename.rsplit('.', 1)[-1].lower()

                if extension not in allowed_extensions:
                    flash("Only JPG, JPEG, PNG and WEBP images are allowed.")
                    return redirect(url_for('sell'))

                uploaded_images.append((image, image_type, extension))

        # Front picture is compulsory
        if not any(image_type == 'front' for _, image_type, _ in uploaded_images):
            flash("Please upload a front picture of the vehicle.")
            return redirect(url_for('sell'))

        user = check_user(session['email'])
        seller_id = user[0]

        new_vehicle = (seller_id, make, model, year, price)

        # Save vehicle details and retrieve its ID
        vehicle_id = insert_vehicles(new_vehicle)

        # Create a folder for this vehicle
        upload_folder = os.path.join(
            app.root_path, 'static', 'images', 'vehicles', str(vehicle_id)
        )

        os.makedirs(upload_folder, exist_ok=True)

        # Save pictures and their database records
        for image, image_type, extension in uploaded_images:

            unique_filename = f"{uuid.uuid4().hex}.{extension}"

            image.save(os.path.join(upload_folder, unique_filename))

            image_path = f"images/vehicles/{vehicle_id}/{unique_filename}"

            insert_vehicle_images(
                (vehicle_id, image_path, image_type)
            )

        flash("Vehicle and pictures successfully listed!")
        return redirect(url_for('buy'))

    return render_template('sell.html')
   
         

     
# CONTACT PAGE ROUTE
@app.route("/contact")
def contact():
    return render_template('contact.html')

# REGISTER ROUTE
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
            return redirect(url_for('login'))
        else:
            flash("Already Registered, Please Log in", "error")
            return redirect(url_for('login'))
    return render_template('register.html')

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
            if bcrypt.check_password_hash(user[4], password):
                session['email'] = email
                flash("Logged in successfully", "success")
                return redirect(url_for('home'))
            else:
                flash("Wrong password, Try again", "error")
                return redirect(url_for('login'))
    return render_template('login.html') 
        
app.run(debug=True)