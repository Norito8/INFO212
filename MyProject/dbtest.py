from neo4j import GraphDatabase

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+ssc://bd8bc315.databases.neo4j.io"
AUTH = ("neo4j", "tYoiiWvG2OfR1l2i2yV6ewiEJVqeUOZ4KcORVcHt7uI")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()