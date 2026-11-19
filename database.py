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
    insert = "insert into vehicles(seller_id, make, model, year)values(%s, %s, %s, %s)"
    cur.execute(insert, values)
    conn.commit()
    
def fetch_vehicles():
    cur.execute("select * from vehicles;")
    vehicles = cur.fetchall()
    return vehicles

def fetch_vehicle(vehicle_id):
    query = "SELECT * FROM vehicles WHERE vehicle_id = %s;"
    cur.execute(query, (vehicle_id,))
    vehicle = cur.fetchone()
    return vehicle
    
def update_vehicles(values):
    cur.execute("update vehicles set make = %s, model = %s, year = %s where vehicle_id = %s", values)
    conn.commit()

def insert_vehicle_images(values):
    insert = "insert into vehcile_images(vehicle_id, image_url, created_at)values(%s, %s, now())"
    cur.execute(insert, values)
    conn.commit()
    
def fetch_vehicle_images():
    cur.execute("select * from vehicle_images;")
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

def insert_user(values):
    insert="insert into users(full_name, email, phone, password, role, created_at)values(%s, %s, %s, %s, %s, %s)"
    cur.execute(insert,values)
    conn.commit()

def fetch_user(user_id):
    query = "SELECT * FROM users WHERE user_id = %s;"
    cur.execute(query, (user_id,))
    user = cur.fetchone()
    return user

def check_user(email):
    query="select * from users where email = %s"
    cur.execute(query,(email,))
    user=cur.fetchone()
    return user