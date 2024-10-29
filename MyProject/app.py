from flask import Flask, request, jsonify
from db import neo4j_conn

app = Flask(__name__)

# Endpoint to create a new car
@app.route('/create_car', methods=['POST'])
def create_car():
    data = request.json
    query = """
    CREATE (c:Car {car_id: $car_id, make: $make, model: $model, year, location: $location, status: $status})
    RETURN c
    """
    params = {
        "car_id": data["car_id"],
        "make": data["make"],
        "model": data["model"],
        "year": data["year"],
        "location": data["location"],
        "status": data["status"]
    }
    result = neo4j_conn.query(query, params)
    return jsonify({"car": result[0]["c"] if result else None}), 201

# Endpoint to book a car
@app.route('/book_car', methods=['POST'])
def book_car():
    data = request.json
    query = """
    MATCH (cust:Customer {customer_id: $customer_id}), (car:Car {car_id: $car_id, status: 'Available'})
    CREATE (cust)-[:BOOKED_BY {date_booked: date()}]->(car)
    SET car.status = 'booked'
    RETURN car
    """
    params = {"customer_id": data['customer_id'], "car_id": data['car_id']}
    result = neo4j_conn.query(query, params)
    return jsonify({"car": result[0]["car"] if result else None}), 200

# Endpoint to rent a booked car
@app.route('/rent_car', methods=['POST'])
def rent_car():
    data = request.json
    query = """
    MATCH (cust:Customer {customer_id: $customer_id})-[:BOOKED_BY]->(car:Car {car_id: $car_id, status: 'booked'})
    CREATE (cust)-[:RENTED_BY {date_rented: date()}]->(car)
    SET car.status = 'rented'
    RETURN car
    """
    params = {"customer_id": data['customer_id'], "car_id": data['car_id']}
    result = neo4j_conn.query(query, params)
    return jsonify({"car": result[0]["car"] if result else None}), 200

# Endpoint to return a rented car
@app.route('/return_car', methods=['POST'])
def return_car():
    data = request.json
    query = """
    MATCH (cust:Customer {customer_id: $customer_id})-[:RENTED_BY]->(car:Car {car_id: $car_id})
    CREATE (cust)-[:RETURNED_BY {date_returned: date(), status_on_return: $status_on_return}]->(car)
    SET car.status = CASE $status_on_return WHEN 'ok' THEN 'available' ELSE 'damaged' END
    return car
    """
    params = {"customer_id": data['customer_id'], "car_id": data['car_id'], "status_on_return": data["status_on_return"]}
    result = neo4j_conn.query(query, params)
    return jsonify({"car": result[0]["car"] if result else None}), 200

if __name__== '__main__':
    app.run(debug=True)