import psycopg2

conn = psycopg2.connect(
    user = "postgres",
    password = "leshan1234",
    host = "localhost",
    port = "5432",
    database = "carlistings"
)

cur = conn.cursor()

def insert_vehicles(values):
    insert = "insert into vehicles(seller_id, make, model, year, price)values(%s, %s, %s, %s, %s) RETURNING vehicle_id"
    cur.execute(insert, values)
    vehicle_id = cur.fetchone()[0]
    conn.commit()
    return vehicle_id
    


def fetch_vehicles():
    query = """
        SELECT
            v.vehicle_id,
            v.make,
            v.model,
            v.year,
            v.price,
            (
                SELECT vi.image_url
                FROM vehicle_images vi
                WHERE vi.vehicle_id = v.vehicle_id
                AND vi.image_type = 'front'
                LIMIT 1
            ) AS front_image
        FROM vehicles v;
    """

    cur.execute(query)
    vehicles = cur.fetchall()

    return vehicles

def fetch_vehicle(vehicle_id):
    query = "SELECT * FROM vehicles WHERE vehicle_id = %s;"
    cur.execute(query, (vehicle_id,))
    vehicle = cur.fetchone()
    return vehicle

def fetch_vehicle_options():

    cur.execute("SELECT DISTINCT make FROM vehicles ORDER BY make;")
    makes = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT model FROM vehicles ORDER BY model;")
    models = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT year FROM vehicles ORDER BY year DESC;")
    years = [row[0] for row in cur.fetchall()]

    return makes, models, years


def search_vehicles(make=None, model=None, year=None):

    query = """
        SELECT
            v.vehicle_id,
            v.make,
            v.model,
            v.year,
            v.price,
            (
                SELECT vi.image_url
                FROM vehicle_images vi
                WHERE vi.vehicle_id = v.vehicle_id
                AND vi.image_type = 'front'
                LIMIT 1
            ) AS front_image
        FROM vehicles v
    """

    conditions = []
    values = []

    if make:
        conditions.append("v.make = %s")
        values.append(make)

    if model:
        conditions.append("v.model = %s")
        values.append(model)

    if year:
        conditions.append("v.year = %s")
        values.append(year)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, tuple(values))
    vehicles = cur.fetchall()

    return vehicles
    

def insert_vehicle_images(values):
    insert = "insert into vehicle_images(vehicle_id, image_url, image_type)values(%s, %s, %s)"
    cur.execute(insert, values)
    conn.commit()
    


def fetch_vehicle_images(vehicle_id):
    query = """
        SELECT image_url, image_type
        FROM vehicle_images
        WHERE vehicle_id = %s
    """

    cur.execute(query, (vehicle_id,))
    vehicle_images = cur.fetchall()

    return vehicle_images

def insert_purchases(values):
    insert = "insert into purchases(price)values(%s)"
    cur.execute(insert, values)
    conn.commit()

def fetch_purchases():
    cur.execute("select * from purchases;")
    purchases = cur.fetchall()
    return purchases

# def insert_user(values):
#     insert="insert into users(full_name, email, phone, password, role)values(%s, %s, %s, %s, %s)"
#     cur.execute(insert,values)
#     conn.commit()



def insert_user(values):

    try:
        # Prevent simultaneous registrations from both becoming admins
        cur.execute("LOCK TABLE users IN EXCLUSIVE MODE")

        # Check how many users already exist
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]

        # Check whether an administrator already exists
        cur.execute("SELECT COUNT(*) FROM admins")
        admin_count = cur.fetchone()[0]

        # Only the first registered user can become admin
        is_admin = user_count == 0 and admin_count == 0

        insert = """
            INSERT INTO users
            (full_name, email, phone, password, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id
        """

        cur.execute(insert, values)
        user_id = cur.fetchone()[0]

        if is_admin:
            cur.execute(
                "INSERT INTO admins (user_id) VALUES (%s)",
                (user_id,)
            )

        conn.commit()

        return is_admin

    except Exception:
        conn.rollback()
        raise



def fetch_user(user_id):
    query = "SELECT * FROM users WHERE user_id = %s;"
    cur.execute(query, (user_id,))
    user = cur.fetchone()
    return user

def check_user(email):
    query = "SELECT * FROM users WHERE LOWER(email) = %s"
    cur.execute(query, (email.strip().lower(),))
    user = cur.fetchone()
    return user

def insert_feedback(values):

    query = """
        INSERT INTO feedback
        (full_name, email, rating, subject, message)
        VALUES (%s, %s, %s, %s, %s);
    """

    cur.execute(query, values)
    conn.commit()