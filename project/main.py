from bson import ObjectId
from flask import Flask, render_template, request, redirect, session
import pymongo
import os.path
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
FOOD_ITEMS_PATH = APP_ROOT + "/static/food_items/"
RESTAURANT_PROFILE_PATH = APP_ROOT + "/static/restaurant_profile/"
conn = pymongo.MongoClient("mongodb://localhost:27017/")
my_database = conn["restaurant_food_ordering"]
admin_collection = my_database["admin"]
food_categories_collection = my_database["food_categories"]
food_sub_categories_collection = my_database["food_sub_categories"]
locations_collection = my_database["locations"]
restaurants_collection = my_database["restaurants"]
customers_collection = my_database["customers"]
food_items_collection = my_database["food_items"]
orders_collection = my_database["orders"]
order_items_collection = my_database["order_items"]
payment_details_collection = my_database["payment_details"]
delivery_boys_collection = my_database["delivery_boys"]

app = Flask(__name__)
app.secret_key = "online_shopping"

query = {}
count = admin_collection.count_documents(query)
if count == 0:
    query = {"username": "admin", "password": "admin"}
    admin_collection.insert_one(query)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = admin_collection.count_documents(query)
    if count > 0:
        admin = admin_collection.find_one(query)
        session['admin_id'] = str(admin['_id'])
        session['role'] = "admin"
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid Login")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/food_categories")
def food_categories():
    message = request.args.get("message")
    query = {}
    food_categories = food_categories_collection.find(query)
    food_categories = list(food_categories)
    print(food_categories)
    return render_template("food_categories.html", food_categories=food_categories)


@app.route("/food_categories_action", methods=['post'])
def food_categories_action():
    category_name = request.form.get("category_name")
    query = {"category_name": category_name}
    count = food_categories_collection.count_documents(query)
    if count == 0:
        food_categories_collection.insert_one(query)
        return redirect("/food_categories")
    else:
        return redirect("food_categories? message=Category Already Exists")


@app.route("/food_sub_categories")
def food_sub_categories():
    message = request.args.get("message")
    food_category_id = request.args.get("food_category_id")
    query = {}
    food_categories = food_categories_collection.find(query)
    food_categories = list(food_categories)
    if message== None:
        message = ""
    if food_category_id == None:
        food_category_id = ""
    if food_category_id == "":
        food_sub_categories = food_sub_categories_collection.find({})
    else:
        query = {"food_category_id": ObjectId(food_category_id)}
        food_sub_categories = food_sub_categories_collection.find(query)
    food_sub_categories = list(food_sub_categories)
    print(food_sub_categories)
    return render_template("food_sub_categories.html", food_categories=food_categories, food_sub_categories=food_sub_categories,food_category_id=food_category_id, message=message, str=str,get_food_category_by_category_id=get_food_category_by_category_id)


@app.route("/food_sub_categories_action",methods=['post'])
def food_sub_categories_action():
    food_category_id = request.form.get("food_category_id")
    food_sub_category_name = request.form.get("food_sub_category_name")
    query = {"food_category_id":ObjectId(food_category_id),"food_sub_category_name":food_sub_category_name}
    count = food_sub_categories_collection.count_documents(query)
    if count > 0:
        return redirect("food_sub_categories?message= Duplicate Sub Category")
    else:
        food_sub_categories_collection.insert_one(query)
        return redirect("food_sub_categories?message=Sub Category Added Successfully")
def get_food_category_by_category_id(food_category_id):
    query = {"_id": food_category_id}
    food_categories = food_categories_collection.find_one(query)
    return food_categories


@app.route("/view_restaurants")
def view_restaurants():
    query = {}
    restaurants = restaurants_collection.find(query)
    restaurants = list(restaurants)
    return render_template("view_restaurant.html", restaurants= restaurants,get_location_by_location_id=get_location_by_location_id)


@app.route("/verify")
def verify():
    restaurant_id = request.args.get("restaurant_id")
    query1 = {"_id": ObjectId(restaurant_id)}
    query2 = {"$set": {"status": "Verifed"}}
    restaurants_collection.update_one(query1, query2)
    return redirect("/view_restaurants")


@app.route("/view_customers")
def view_customers():
    query = {}
    customers = customers_collection.find(query)
    customers = list(customers)
    return render_template("view_customers.html", customers= customers,get_location_by_location_id=get_location_by_location_id)


@app.route("/view_delivary_boy")
def view_delivary_boy():
    query = {}
    delivery_boys = delivery_boys_collection.find(query)
    delivery_boys = list(delivery_boys)
    return render_template("view_delivary_boy.html", delivery_boys= delivery_boys,get_location_by_location_id=get_location_by_location_id)


@app.route("/locations")
def locations():
    message = request.args.get("message")
    query = {}
    locations = locations_collection.find(query)
    locations = list(locations)
    print(locations)
    return render_template("location.html", locations=locations)


@app.route("/location_action", methods=['post'])
def location_action():
    location_name = request.form.get("location_name")
    query = {"location_name": location_name}
    count = locations_collection.count_documents(query)
    if count == 0:
        locations_collection.insert_one(query)
        return redirect("/locations")
    else:
        return redirect("locations? message=Category Already Exists")


@app.route("/admin_logout")
def admin_logout():
    return redirect("/")


@app.route("/restaurant_login")
def restaurant_login():
    return render_template("restaurant_login.html")


@app.route("/restaurant_login_action",methods=['post'])
def restaurant_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email":email,"password":password}
    count = restaurants_collection.count_documents(query)
    if count > 0:
        restaurant =restaurants_collection.find_one(query)
        if restaurant['status'] == "Not verified":
            return render_template("message.html",message="Restaurant Is Not verified")
        else:
            session['restaurant_id'] = str(restaurant['_id'])
            session['role'] = "restaurant"
            return redirect("/restaurant_home")

def get_location_by_location_id(location_id):
    query = {"_id": location_id}
    locations = locations_collection.find_one(query)
    return locations


@app.route("/restaurant_home")
def restaurant_home():
    restaurant_id = session['restaurant_id']
    query = {"_id": ObjectId(restaurant_id)}
    restaurant = restaurants_collection.find_one(query)
    return render_template("restaurant_home.html",restaurant=restaurant)


@app.route("/restaurant_logout")
def restaurant_logout():
    return redirect("/")


@app.route("/restaurant_registration_action", methods=["post"])
def restaurant_registration_action():
    name =  request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    password = request.form.get("password")
    location_id = request.form.get("location_id")
    address = request.form.get("address")
    about = request.form.get("about")
    status = request.form.get("status")
    restaurant_profile = request.files.get("restaurant_profile")
    path = RESTAURANT_PROFILE_PATH +""+ restaurant_profile.filename
    restaurant_profile.save(path)
    query = {"email":email}
    count = restaurants_collection.count_documents(query)
    if count == 0:
        query = {"name":name, "phone":phone, "email":email, "password":password, "restaurant_profile": restaurant_profile.filename,"location_id":ObjectId(location_id), "address":address, "about":about, "status":"Not verified"}
        restaurants_collection.insert_one(query)
        return render_template("message.html", message="Restaurant Added Susseccfully")
    else:
        return render_template("message.html",message="Duplicate Entry")



@app.route("/restaurant_registration")
def restaurant_registration():
    locations = locations_collection.find({})
    locations = list(locations)
    print(locations)
    return render_template("restaurant_registration.html",locations=locations)


@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")


@app.route("/customer_login_action",methods=['post'])
def customer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email":email,"password":password}
    count = customers_collection.count_documents(query)
    if count > 0:
        customer = customers_collection.find_one(query)
        session['customer_id'] = str(customer['_id'])
        session['role'] = "customer"
        return redirect("/customer_home")
    else:
        return render_template("message.html", message="Invalid Login")
def get_location_by_location_id(location_id):
    query = {"_id": location_id}
    locations = locations_collection.find_one(query)
    return locations


@app.route("/customer_home")
def customer_home():
    return render_template("customer_home.html")


@app.route("/customer_logout")
def customer_logout():
    return redirect("/")


@app.route("/customer_registration")
def customer_registration():
    locations = locations_collection.find({})
    locations = list(locations)
    return render_template("customer_registration.html",locations = locations)


@app.route("/customer_registration_action", methods=["post"])
def customer_registration_action():
    name =  request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    password = request.form.get("password")
    location_id = request.form.get("location_id")
    address = request.form.get("address")
    query = {"email":email}
    count = customers_collection.count_documents(query)
    if count == 0:
        query = {"name":name, "phone":phone, "email":email, "password":password ,"location_id":ObjectId(location_id), "address":address}
        customers_collection.insert_one(query)
        return render_template("message.html", message="Customer Added Susseccfully")
    else:
        return render_template("message.html",message="Duplicate Entry")


@app.route("/delivary_boy_login")
def delivary_boy_login():
    return render_template("delivary_boy_login.html")


@app.route("/delivary_boy_login_action",methods=['post'])
def delivary_boy_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email":email,"password":password}
    count = delivery_boys_collection.count_documents(query)
    if count > 0:
        delivary_boy = delivery_boys_collection.find_one(query)
        session['delivary_boy_id'] = str(delivary_boy['_id'])
        session['role'] = "delivary_boy"
        return redirect("/delivary_boy_home")
    else:
        return render_template("message.html", message="Invalid Login")
def get_location_by_location_id(location_id):
    query = {"_id": location_id}
    locations = locations_collection.find_one(query)
    return locations


@app.route("/delivary_boy_home")
def delivary_boy_home():
    return render_template("delivary_boy_home.html")


@app.route("/delivary_boy_logout")
def delivary_boy_logout():
    return redirect("/")


@app.route("/delivary_boy_registration")
def delivary_boy_registration():
    locations = locations_collection.find({})
    locations = list(locations)
    return render_template("delivary_boy_registration.html",locations = locations)

@app.route("/delivary_boy_registration_action", methods=["post"])
def delivary_boy_registration_action():
    name =  request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    password = request.form.get("password")
    location_id = request.form.get("location_id")
    address = request.form.get("address")
    query = {"email":email}
    count = delivery_boys_collection.count_documents(query)
    if count == 0:
        query = {"name":name, "phone":phone, "email":email, "password":password ,"location_id":ObjectId(location_id), "address":address}
        delivery_boys_collection.insert_one(query)
        return render_template("message.html", message="Delivary Boy Added Susseccfully")
    else:
        return render_template("message.html",message="Duplicate Entry")



app.run(debug=True)
