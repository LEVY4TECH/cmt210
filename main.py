import os
import uuid
from werkzeug.utils import secure_filename

from flask import Flask, render_template, redirect, url_for, session,flash, request

from database import insert_vehicles, fetch_vehicle, fetch_vehicles, insert_vehicle_images, fetch_vehicle_images, insert_user, fetch_user, check_user, fetch_vehicle_options, search_vehicles, insert_feedback

from flask_bcrypt import Bcrypt

from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'levy4tech@gmail.com'

mail = Mail(app)

app.secret_key = "hdwsbdbewhdb"

bcrypt = Bcrypt(app)

@app.route("/")
def home():

    makes, models, years = fetch_vehicle_options()

    return render_template(
        'home.html',
        makes=makes,
        models=models,
        years=years
    )

@app.route("/buy")
def buy():

    make = request.args.get('make', '').strip()
    model = request.args.get('model', '').strip()
    year = request.args.get('year', '').strip()

    year_filter = int(year) if year.isdigit() else None

    vehicles = search_vehicles(make, model, year_filter)

    makes, models, years = fetch_vehicle_options()

    return render_template(
        "buy.html",
        vehicles=vehicles,
        makes=makes,
        models=models,
        years=years,
        selected_make=make,
        selected_model=model,
        selected_year=year
    )

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
@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        rating = request.form.get('rating', '')
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not full_name or not email or not rating or not message:
            flash("Please fill in all required fields.")
            return redirect(url_for('contact'))

        try:
            rating = int(rating)

            if rating < 1 or rating > 5:
                flash("Please select a rating between 1 and 5.")
                return redirect(url_for('contact'))

        except ValueError:
            flash("Invalid rating selected.")
            return redirect(url_for('contact'))

        values = (full_name, email, rating, subject, message)

        insert_feedback(values)

        flash("Thank you! Your feedback has been submitted.")
        return redirect(url_for('contact'))

    return render_template('contact.html')

# REGISTER ROUTE
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        full_name = request.form['name']
        email = request.form['email'].strip().lower()
        phone = request.form['phone']
        password = request.form['pass']
        role = request.form['role']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = check_user(email)

        if user:
            flash("Email already registered. Please log in.", "error")
            return redirect(url_for('login'))

        try:
            new_user = (full_name, email, phone, hashed_password, role)
            insert_user(new_user)

            try:
                msg = Message(
                    subject="Welcome to CarListings!",
                    recipients=[email]
                )

                msg.body = f"""
Hello {full_name},

Welcome to CarListings!

Your account has been successfully created.

You can now log in and explore the vehicles listed on our platform.

Thank you for joining CarListings.

Best regards,
CarListings Team
                """

                mail.send(msg)

                flash("Account created successfully! Confirmation email sent.", "success")

            except Exception:
                app.logger.exception("Email sending failed.")
                flash("Account created, but confirmation email could not be sent.", "warning")

            return redirect(url_for('login'))

        except Exception:
            app.logger.exception("Registration failed.")
            flash("Registration could not be completed. Please try again.", "error")
            return redirect(url_for('register'))

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