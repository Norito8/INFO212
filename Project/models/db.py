from neo4j import GraphDatabase, Driver, AsyncGraphDatabase, AsyncDriver
import re

URI = "neo4j+ssc://bd8bc315.databases.neo4j.io"
AUTH = ("neo4j", "tYoiiWvG2OfR1l2i2yV6ewiEJVqeUOZ4KcORVcHt7uI")

def _get_connection() -> Driver:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()

    return driver

class Car:
    def __init__(self, make, model, year, location, status):
        self.make = make
        self.model = model
        self.year = year
        self.location = location
        self.status = status

    def create_car(make, model, year, location, status, car_id):
        data = _get_connection().execute_query("CREATE (c:Car {make: $make, model: $model, year: $year, location: $location, status: $status, car_id: $car_id})",
                                                make=make, model=model, year=year, location=location, status=status, car_id=car_id)
        return data
        
    def find_car(car_id):
        data = _get_connection().execute_query("MATCH (c:Car {car_id: $car_id}) RETURN c", car_id=car_id)
        if data and len(data.records) > 0:
            car_node = data.records[0][0]
            properties = car_node.items()
            car_properties = {key: value for key, value in properties}
            return Car(
                make=car_properties['make'],
                model=car_properties['model'],
                year=car_properties['year'],
                location=car_properties['location'],
                status=car_properties['status']
            )
        return None
    
    def update_car(car_id, new_status, customer_id=None):
        with _get_connection().session() as session:
            query = """
            MATCH (c:Car {car_id: $car_id})
            SET c.status = $new_status
            RETURN c
            """
            result = session.run(query, car_id=car_id, new_status=new_status)
            car = result.single()[0] if result else None

            if car and customer_id:
                if new_status == "booked":
                    session.run("""
                    MATCH (c:Car {car_id: $car_id}), (cust:Customer {customer_id: $customer_id})
                    MERGE (c)-[:BOOKED_BY]->(cust)
                    """, car_id=car_id, customer_id=customer_id)
                elif new_status == "rented":
                    session.run("""
                    MATCH (c:Car {car_id: $car_id})-[r:BOOKED_BY]->(:Customer)
                    DELETE r
                    """, car_id=car_id)
                    session.run("""
                    MATCH (c:Car {car_id: $car_id}), (cust:Customer {customer_id: $customer_id})
                    MERGE (c)-[:RENTED_BY]->(cust)
                    """, car_id=car_id, customer_id=customer_id)
            return car

    def delete_car(car_id):
        data = _get_connection().execute_query("MATCH (c:Car {car_id: $car_id}) DETACH DELETE c", car_id=car_id)
        return data
    
    def find_car_by_status(customer_id, statuses):
        data = _get_connection().execute_query("""
        MATCH (c:Car)-[:BOOKED_BY|RENTED_BY]->(cust:Customer {customer_id: $customer_id})
        WHERE c.status IN $statuses
        RETURN c
        """, customer_id=customer_id, statuses=statuses)
        if data and len(data.records) > 0:
            return data.records[0][0]
        return None

class Customer:
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address

    def create_customer(name, age, address, customer_id):
        data = _get_connection().execute_query("CREATE (a:Customer {name: $name, age: $age, address: $address, customer_id: $customer_id})",
                                                name=name, age=age, address=address, customer_id=customer_id)
        return data

    def find_customer(customer_id):
        data = _get_connection().execute_query("MATCH (a:Customer {customer_id: $customer_id}) RETURN a", customer_id=customer_id)
        if data and len(data.records) > 0:
            customer_node = data.records[0][0]
            properties = customer_node.items()
            customer_properties = {key: value for key, value in properties}
            return Customer(
                name=customer_properties['name'],
                age=customer_properties['age'],
                address=customer_properties['address']
            )
        print(f"No car found with car_id: {customer_id}")
        return None

    def update_customer(customer_id, new_address):
        data = _get_connection().execute_query("""
        MATCH (a:Customer {customer_id: $customer_id})
        SET a.status = $new_address
        RETURN a
        """, customer_id=customer_id, new_address=new_address)
        return data

    def delete_customer(customer_id):
        data = _get_connection().execute_query("MATCH (a:Customer {customer_id: $customer_id}) DETACH DELETE a", customer_id=customer_id)
        return data
    
class Employee:
    def __init__(self, name, address, branch):
        self.name = name
        self.address = address
        self.branch = branch

    def create_employee(name, address, branch):
        data = _get_connection().execute_query("CREATE (e:Employee {name: $name, address: $address, branch: $branch})", name=name, address=address, branch=branch)
        return data
    
    def find_employee(employee_id):
        data = _get_connection().execute_query("MATCH (e:Employee {employee_id: $employee_id}) RETURN e", employee_id=employee_id)
        if data:
            employee_node = data[0][0]
            return Employee(
                name = employee_node['name'],
                address = employee_node['address'],
                branch = employee_node['branch']
            )
        return None
    
    def update_employee(employee_id, new_address):
        data = _get_connection().execute_query("""
        MATCH (e:Employee {employee_id: $employee_id})
        SET e.address = $new_address
        RETURN e
        """, employee_id=employee_id, new_address=new_address)
        return data
    
    def delete_employee(employee_id):
        data = _get_connection().execute_query("MATCH (e:Employee {employee_id: $employee_id}) DELETE e", employee_id=employee_id)
        return data

# Car.create_car(make="Toyota", model="Camry", year=2021, location="Branch Bergen", status="available", car_id="123")
# Customer.create_customer(name="John Doe", age=30, address="Fyllingsdalen, Bergn", customer_id="E1")
# Customer.create_customer(name="Samir Yebok", age=24, address="Åsane, Bergen", customer_id="E2")
# Car.create_car(make="Honda", model="Civic", year=2020, location="Branch Bergen", status="available", car_id="124")
# Car.create_car(make="Ford", model="Focus", year=2019, location="Branch Bergen", status="available", car_id="125")
# Car.create_car(make="BMW", model="3 Series", year=2022, location="BBranch Bergen", status="available", car_id="126")
# Car.create_car(make="Audi", model="A4", year=2021, location="Branch Bergen", status="available", car_id="127")
# Car.create_car(make="Mercedes", model="C-Class", year=2023, location="Branch Bergen", status="available", car_id="128")
# Car.create_car(make="Volkswagen", model="Golf", year=2020, location="Branch Bergen", status="available", car_id="129")
# Car.create_car(make="Tesla", model="Model 3", year=2023, location="Branch Bergen", status="available", car_id="130")
# Car.create_car(make="Nissan", model="Altima", year=2019, location="Branch Bergen", status="available", car_id="131")
# Customer.delete_customer(customer_id="E2")