import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from utils import load_data_from_json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hw16.db"
app.config["JSON_AS_ASCII"] = False
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # customer = relationship("User", foreign_keys=[customer_id])
    # executor = relationship("User", foreign_keys=[executor_id])
    # offers = relationship("Offer")


class Offer(db.Model):
    __tablename__ = "offer"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # order = relationship("Order", overlaps="offers")
    # executor = relationship("User")


def main():
    db.drop_all()
    db.create_all()
    insert_data()
    app.run()


def insert_data():
    users_data = load_data_from_json("users.json")
    users_list = []
    for user_data in users_data:
        users_list.append(
            User(
                id=user_data["id"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                age=user_data["age"],
                email=user_data["email"],
                role=user_data["role"],
                phone=user_data["phone"]))

        with db.session.begin():
            db.session.add_all(users_list)

    offers_data = load_data_from_json("offers.json")
    offers_list = []
    for offer_data in offers_data:
        offers_list.append(
            Offer(
                id=offer_data["id"],
                order_id=offer_data["order_id"],
                executor_id=offer_data["executor_id"]
            ))
        with db.session.begin():
            db.session.add_all(offers_list)

    orders_list = []
    orders_data = load_data_from_json("orders.json")
    for order_data in orders_data:
        orders_list.append(
            Order(id=order_data["id"],
                  name=order_data["name"],
                  description=order_data["description"],
                  start_date=datetime.strptime(order_data["start_date"], "%m/%d/%Y"),
                  end_date=datetime.strptime(order_data["end_date"], "%m/%d/%Y"),
                  address=order_data["address"],
                  price=order_data["price"],
                  customer_id=order_data["customer_id"],
                  executor_id=order_data["executor_id"]
                  ))
        with db.session.begin():
            db.session.add_all(orders_list)


@app.route("/users", methods=["GET", "POST"])
def users_index():
    if request.method == "GET":
        users_list = []
        for user in User.query.all():
            users_list.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "age": user.age,
                "email": user.email,
                "role": user.role,
                "phone": user.phone
            })
        return jsonify(users_list)

    elif request.method == "POST":
        data = request.get_json()
        new_user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            email=data["email"],
            role=data["role"],
            phone=data["phone"]
        )
        with db.session.begin():
            db.session.add(new_user)
        return "", 200


@app.route("/users/<int:id>", methods=["GET", "PUT", "DELETE"])
def users_by_id(id):

    if request.method == "GET":
        user = User.query.get(id)
        any_user = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age,
            "email": user.email,
            "role": user.role,
            "phone": user.phone
        }
        return jsonify(any_user)

    elif request.method == "PUT":
        data = request.get_json()
        user = User.query.get(id)
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.age = data["age"]
        user.email = data["email"]
        user.role = data["role"]
        user.phone = data["phone"]
        db.session.add(user)
        db.session.commit()
        return "", 203

    elif request.method == "DELETE":
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return "", 203


@app.route("/orders", methods=["GET", "POST"])
def index_orders():
    orders_list = []

    if request.method == "GET":
        for order in Order.query.all():
            customer = User.query.get(order.customer_id).first_name if User.query.get(order.customer_id) else order.customer_id
            executer = User.query.get(order.executor_id).first_name if User.query.get(order.executor_id) else order.executor_id
            orders_list.append(
                {
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": customer,
                "executor_id": executer
                }
            )
        return jsonify(orders_list)

    elif request.method == "POST":
        data = request.get_json()
        new_order = Order(
            # id=data["id"],
            name=data["name"],
            description=data["description"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            address=data["address"],
            price=data["price"],
            customer_id=data["customer_id"],
            executor_id=data["executor_id"]
        )
        with db.session.begin():
            db.session.add(new_order)
        return "", 200

@app.route("/orders/<int:id>", methods=["GET", "PUT", "DELETE"])
def order_by_id(id):

    if request.method == "GET":
        order = Order.query.get(id)
        any_order = {
            "id": order.id,
            "name": order.name,
            "description": order.description,
            "start_date": order.start_date,
            "end_date": order.end_date,
            "address": order.address,
            "price": order.price,
            "customer_id": order.customer_id,
            "executor_id": order.executor_id
        }
        return jsonify(any_order)

    elif request.method == "PUT":
        data = request.get_json()
        order = Order.query.get(id)
        order.name = data["name"]
        order.description = data["description"]
        order.start_date = data["start_date"]
        order.end_date = data["end_date"]
        order.price = data["price"]
        order.customer_id = data["customer_id"]
        order.executor_id = data["executor_id"]

        db.session.add(order)
        db.session.commit()
        return "", 203

    elif request.method == "DELETE":
        order = Order.query.get(id)
        db.session.delete(order)
        db.session.commit()
        return "", 203


@app.route("/offers", methods=["GET", "POST"])
def index_offers():

    if request.method == "GET":
        offers_list = []
        for offer in Offer.query.all():
            offers_list.append({
                "id": offer.id,
                "order_id": offer.order_id,
                "executor_id": offer.executor_id
            })
        return jsonify(offers_list)

    elif request.method == "POST":
        data = request.get_json()
        new_offer = Offer(
            # id=data["id"],
            order_id=data["order_id"],
            executor_id=data["executor_id"]
        )
        with db.session.begin():
            db.session.add(new_offer)
        return "", 200


@app.route("/offers/<int:id>", methods=["GET", "PUT", "DELETE"])
def offer_by_id(id):

    if request.method == "GET":
        offer = Offer.query.get(id)
        any_offer = {
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id
            }
        return jsonify(any_offer)

    elif request.method == "PUT":
        data = request.get_json()
        offer = Offer.query.get(id)
        offer.order_id = data["order_id"]
        offer.executor_id = data["executor_id"]
        db.session.add(offer)
        db.session.commit()
        return "", 203

    elif request.method == "DELETE":
        offer = Offer.query.get(id)
        db.session.delete(offer)
        db.session.commit()



if __name__ == '__main__':
    main()
