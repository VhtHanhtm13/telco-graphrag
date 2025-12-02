# import_telecom_to_neo4j.py
import json
import os
from neo4j import GraphDatabase
from itertools import islice

# ----- CONFIG -----
URI = os.environ.get("NEO4J_URI", "neo4j+s://<YOUR_AURA_ENDPOINT>")
USER = os.environ.get("NEO4J_USER", "<USERNAME>")
PASSWORD = os.environ.get("NEO4J_PASSWORD", "<PASSWORD>")

# File paths (in the same folder)
ACM_FILE = "acmbalance_raw_llm_output.json"   # :contentReference[oaicite:4]{index=4}
BAL_FILE = "balance_raw_llm_output.json"      # :contentReference[oaicite:5]{index=5}
SUB_FILE = "subscriber_raw_llm_output.json"   # :contentReference[oaicite:6]{index=6}
PROD_FILE = "product_raw_llm_output.json"     # :contentReference[oaicite:7]{index=7}

BATCH_SIZE = 200

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD), max_connection_lifetime=3600)

def chunked(iterable, size):
    it = iter(iterable) # convert ITERABLE to INTERATOR 
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk

# ----- 1) CREATE CONSTRAINTS / INDEXS -----
def create_constraints(tx):
    tx.run("""
    CREATE CONSTRAINT subscriber_subId_unique IF NOT EXISTS
    FOR (s:Subscriber) REQUIRE s.subId IS UNIQUE;
    """)
    tx.run("""
    CREATE CONSTRAINT product_id_unique IF NOT EXISTS
    FOR (p:Product) REQUIRE p.id IS UNIQUE;
    """)
    tx.run("""
    CREATE CONSTRAINT balance_id_unique IF NOT EXISTS
    FOR (b:Balance) REQUIRE b.id IS UNIQUE;
    """)
    tx.run("""
    CREATE CONSTRAINT acmbalance_id_unique IF NOT EXISTS
    FOR (a:AcmBalance) REQUIRE a.id IS UNIQUE;
    """)
    # Bạn có thể thêm index cho property khác nếu cần

def ensure_constraints():
    with driver.session() as s:
        s.write_transaction(create_constraints)
    print("Constraints created/ensured.")

# ----- 2) Import node types -----
def import_products():
    with open(PROD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f).get("product", [])
    print(f"Products to import: {len(data)}")
    cypher = """
    MERGE (p:Product {id: $id})
    SET p.productOfferingID = $productOfferingID,
        p.effDate = $effDate,
        p.expDate = $expDate,
        p.updateDate = $updateDate,
        p.state = $state,
        p.level = $level,
        p.of = $of,
        p.recurringDay = $recurringDay
    """
    with driver.session() as s:
        for chunk in chunked(data, BATCH_SIZE):
            tx = s.begin_transaction()
            for item in chunk:
                tx.run(cypher, **item)
            tx.commit()
    print("Products imported.")

def import_balances():
    with open(BAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f).get("balance", [])
    print(f"Balances to import: {len(data)}")
    cypher = """
    MERGE (b:Balance {id: $id})
    SET b.balType = $balType,
        b.effDate = $effDate,
        b.expDate = $expDate,
        b.updateDate = $updateDate,
        b.gross = $gross,
        b.consume = $consume,
        b.reserve = $reserve,
        b.state = $state,
        b.level = $level,
        b.of = $of
    """
    with driver.session() as s:
        for chunk in chunked(data, BATCH_SIZE):
            tx = s.begin_transaction()
            for item in chunk:
                tx.run(cypher, **item)
            tx.commit()
    print("Balances imported.")

def import_acm_balances():
    with open(ACM_FILE, "r", encoding="utf-8") as f:
        data = json.load(f).get("acmBalance", [])
    print(f"AcmBalances to import: {len(data)}")
    cypher = """
    MERGE (a:AcmBalance {id: $id})
    SET a.balType = $balType,
        a.effDate = $effDate,
        a.expDate = $expDate,
        a.updateDate = $updateDate,
        a.state = $state,
        a.value = $value,
        a.billingCycleId = $billingCycleId,
        a.level = $level,
        a.of = $of
    """
    with driver.session() as s:
        for chunk in chunked(data, BATCH_SIZE):
            tx = s.begin_transaction()
            for item in chunk:
                tx.run(cypher, **item)
            tx.commit()
    print("AcmBalances imported.")

def import_subscribers():
    with open(SUB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f).get("subscriber", [])
    print(f"Subscribers to import: {len(data)}")
    cypher = """
    MERGE (s:Subscriber {subId: $subId})
    SET s.msisdn = $msisdn,
        s.custId = $custId,
        s.mainProductId = $mainProductId,
        s.isDefault = $isDefault,
        s.precharge = $precharge,
        s.subType = $subType,
        s.stateSet = $stateSet,
        s.effDate = $effDate,
        s.expDate = $expDate,
        s.updateDate = $updateDate,
        s.langId = $langId,
        s.imsi = $imsi,
        s.iccid = $iccid
    """
    with driver.session() as s:
        for chunk in chunked(data, BATCH_SIZE):
            tx = s.begin_transaction()
            for item in chunk:
                # remove lists from SET, keep lists stored as properties if you want
                # We'll use lists to create relationships later
                params = dict(item)
                tx.run(cypher, **params)
            tx.commit()
    print("Subscribers imported.")

# ----- 3) Create relationships -----
# We'll iterate subscriber file and create pairs for each list then UNWIND inside Cypher in batches.

def create_subscriber_product_relationships():
    with open(SUB_FILE, "r", encoding="utf-8") as f:
        subs = json.load(f).get("subscriber", [])
    pairs = []
    for s in subs:
        subId = s.get("subId")
        for pid in s.get("productIdList", []) or []:
            pairs.append({"subId": subId, "pid": pid})
    print(f"Subscriber-Product pairs: {len(pairs)}")
    cypher = """
    UNWIND $rows as row
    MATCH (s:Subscriber {subId: row.subId})
    MATCH (p:Product {id: row.pid})
    MERGE (s)-[:SUBSCRIBE]->(p)
    """
    with driver.session() as s:
        for chunk in chunked(pairs, BATCH_SIZE):
            s.write_transaction(lambda tx: tx.run(cypher, rows=chunk))
    print("Subscriber->Product relationships created.")

def create_subscriber_balance_relationships():
    with open(SUB_FILE, "r", encoding="utf-8") as f:
        subs = json.load(f).get("subscriber", [])
    pairs = []
    for s in subs:
        subId = s.get("subId")
        for bid in s.get("balanceIdList", []) or []:
            pairs.append({"subId": subId, "bid": bid})
    print(f"Subscriber-Balance pairs: {len(pairs)}")
    cypher = """
    UNWIND $rows as row
    MATCH (s:Subscriber {subId: row.subId})
    MATCH (b:Balance {id: row.bid})
    MERGE (s)-[:HAS_BALANCE]->(b)
    MERGE (b)-[:BELONG_TO]->(s)
    """
    with driver.session() as s:
        for chunk in chunked(pairs, BATCH_SIZE):
            s.write_transaction(lambda tx: tx.run(cypher, rows=chunk))
    print("Subscriber->Balance relationships created.")

def create_subscriber_acmbalance_relationships():
    with open(SUB_FILE, "r", encoding="utf-8") as f:
        subs = json.load(f).get("subscriber", [])
    pairs = []
    for s in subs:
        subId = s.get("subId")
        for aid in s.get("acmBalanceIdList", []) or []:
            pairs.append({"subId": subId, "aid": aid})
    print(f"Subscriber-AcmBalance pairs: {len(pairs)}")
    cypher = """
    UNWIND $rows as row
    MATCH (s:Subscriber {subId: row.subId})
    MATCH (a:AcmBalance {id: row.aid})
    MERGE (s)-[:HAS_ACM_BALANCE]->(a)
    MERGE (a)-[:BELONG_TO]->(s)
    """
    with driver.session() as s:
        for chunk in chunked(pairs, BATCH_SIZE):
            s.write_transaction(lambda tx: tx.run(cypher, rows=chunk))
    print("Subscriber->AcmBalance relationships created.")

# ----- MAIN -----
def main():
    print("Start import pipeline")
    ensure_constraints()
    import_products()
    import_balances()
    import_acm_balances()
    import_subscribers()
    # relationships (after nodes exist)
    create_subscriber_product_relationships()
    create_subscriber_balance_relationships()
    create_subscriber_acmbalance_relationships()
    print("Import finished.")

if __name__ == "__main__":
    main()
