from neo4j import GraphDatabase

class CarRental:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]
        
neo4j_conn =CarRental(uri="neo4j+ssc://bd8bc315.databases.neo4j.io", user="neo4j", password="tYoiiWvG2OfR1l2i2yV6ewiEJVqeUOZ4KcORVcHt7uI")