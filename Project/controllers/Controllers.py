from Project import app
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from Project.models.db import Car, Customer 

app.secret_key = 'your_secret_key'

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('home.html')


@app.route('/order-car', methods=['GET', 'POST'])
def order_car():
    if request.method == 'POST':
        customer_id = request.form.get("customer_id")
        car_id = request.form.get("car_id")

        customer = Customer.find_customer(customer_id)
        car = Car.find_car(car_id)

        if not customer:
            flash("Customer not found", "error")
            return redirect(url_for('home'))
        if not car:
            flash("Car not found", "error")
            return redirect(url_for('home'))

        booked_or_rented_car = Car.find_car_by_status(customer_id, ["booked", "rented"])
        if booked_or_rented_car:
            flash(f"Customer {customer.name}, id: {customer_id} already has a car booked or rented.", "error")
            return redirect(url_for('home'))

        if car.status == "available":
            Car.update_car(car_id, "booked", customer_id)
            flash(f"Car ({car.make} {car.model}, {car.year}) id:{car_id} has been booked by customer {customer.name}, id: {customer_id}.", "success")
            return redirect(url_for('home'))
        else:
            flash(f"Car ({car.make} {car.model}, {car.year}) id:{car_id} is already booked.", "error")
            return redirect(url_for('home'))
    
    return render_template('order_car.html')


@app.route('/cancel-order-car', methods=['GET', 'POST'])
def cancel_order_car():
    if request.method == 'POST':
        car_id = request.form.get("car_id")
        
        car = Car.find_car(car_id)

        if not car:
            flash("Car not found", "error")

        if car.status == "booked":
            Car.update_car(car_id, "available")
            flash(f"Booking for car ({car.make} {car.model}, id:{car.year}) {car_id} has been canceled.", "success")
            return redirect(url_for('home'))
        else:
            flash(f"Car ({car.make} {car.model}, {car.year}) id:{car_id} is not booked.", "error")
            return redirect(url_for('home'))
    
    return render_template('cancel_order_car.html')


# Rent Car Route
@app.route('/rent-car', methods=['GET', 'POST'])
def rent_car():
    if request.method == 'POST':
        car_id = request.form.get("car_id")

        car = Car.find_car(car_id)
        if not car:
            flash("Car not found", "error")

        if car.status == "booked":
            Car.update_car(car_id, "rented")
            flash(f"Car ({car.make} {car.model}, {car.year}) id:{car_id} has been rented.", "success")
            return redirect(url_for('home'))
        else:
            flash(f"Car ({car.make} {car.model}, {car.year}) id:{car_id} must be booked before renting.", "error")
            return redirect(url_for('home'))
    
    return render_template('rent_car.html')


# Return Car Route
@app.route('/return-car', methods=['GET', 'POST'])
def return_car():
    if request.method == 'POST':
        customer_id = request.form.get("customer_id")
        car_id = request.form.get("car_id")
        return_status = request.form.get("return_status")

        customer = Customer.find_customer(customer_id)
        car = Car.find_car(car_id)

        if not customer:
            flash("Customer not found", "error")
        if not car:
            flash("Car not found", "error")

        if car.status == "rented":
            new_status = "available" if return_status == "available" else "damaged"
            Car.update_car(car_id, new_status)
            flash(f"Car ({car.make} {car.model}, {car.year}) id:{car_id} returned by customer {customer.name}, id: {customer_id} and marked as '{new_status}'.", "success")
            return redirect(url_for('home'))
        else:
            flash(f"Car ({car.make} {car.model}, {car.year}) id:{car_id} was not rented by customer {customer.name}, id: {customer_id}.", "error")

    return render_template('return_car.html')
