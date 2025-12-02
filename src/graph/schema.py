# schema.py
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

print("======DEBUG - NEO4J_URI = ============", URI)

def connect_driver():
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        driver.verify_connectivity()
        print("✔ Connected to Neo4j Aura")
        return driver
    except Exception as e:
        print("❌ Cannot connect to Neo4j Aura:", e)
        exit(1)

driver = connect_driver()

def create_constraints(tx):
    tx.run("""
        CREATE CONSTRAINT subscriber_subId_unique IF NOT EXISTS
        FOR (s:Subscriber) REQUIRE s.subId IS UNIQUE;
    """)

    tx.run("""
        CREATE CONSTRAINT balance_id_unique IF NOT EXISTS
        FOR (b:Balance) REQUIRE b.id IS UNIQUE;
    """)

    tx.run("""
        CREATE CONSTRAINT acmbalance_id_unique IF NOT EXISTS
        FOR (a:AcmBalance) REQUIRE a.id IS UNIQUE;
    """)

    tx.run("""
        CREATE CONSTRAINT product_id_unique IF NOT EXISTS
        FOR (p:Product) REQUIRE p.id IS UNIQUE;
    """)

def ensure_constraints():
    with driver.session() as session:
        session.execute_write(create_constraints)
    print("Schema (constraints) created successfully.")

if __name__ == "__main__":
    print("Creating Neo4j schema (constraints)...")
    ensure_constraints()
    print("DONE: Schema created!")
