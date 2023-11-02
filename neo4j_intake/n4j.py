from neo4j import GraphDatabase
from neo4j_intake.logger import ModuleLogger

# TODO: Test connection

def execute_query(creds: (str, str, str), query: str, params: dict={}):
    print(f'creds: {creds}')
    host, user, password = creds

    # Returns a tuple of records, summary, keys
    with GraphDatabase.driver(host, auth=(user, password)) as driver:
        records, summary, keys =  driver.execute_query(query, params)
        # Only interested in list of result records
        ModuleLogger().debug(f'query: {query}: summary: {summary}, keys: {keys}, number of records: {len(records)}')
        return records

def reset(host:str, user: str, password:str):
    # Clears nodes and relationships - but labels remain and can only be cleared via GUI
    query = """
    MATCH (n)
    DETACH DELETE n
    """
    # TODO: Confirm reset complete
    execute_query(host, user, password, query, params = {})
