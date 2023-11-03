from neo4j_intake.n4j import execute_query, reset
from neo4j_intake.models import Neo4jNode, Neo4jRelationship
from neo4j_intake.logger import ModuleLogger
from pydantic import parse_obj_as


# SHARED FUNCTIONS
def neo4j_props_query(properties: dict) -> str:
    # Need to specially format the props. Keys should not be quoted in Cypher.
    if properties is None:
        return ""
    
    prop_list = list(properties.keys())
    
    props = " {"
    for idx, k in enumerate(prop_list):
        v = properties[k]
        if isinstance(v, int | float):
            value = v
        else:
            value = f'"{v}"'
        
        if idx == 0:
            props += " "
        if idx > 0:
            props += ", "
        props += f'{k}: {value}'

    props += " }"
    return props

# NODES
def get_neo4j_nodes_query(node: Neo4jNode) -> str:
    """
    Generates a Cypher query string to retrieve all nodes matching properties of arg Neo4jNode passed in.
    
    Args:
        node: Neo4jNodes - Nodes with labels and proeprties matching this object will be retrieved. If no label or properties are specified, then every node in the target db will be returned.

    Returns:
        String containing Cypher query
    """
    props = neo4j_props_query(node.properties)

    query = f"MATCH (n{props})"

    if len(node.labels) > 0:
        query += f"\nWHERE "
        for idx, label in enumerate(node.labels):
            if idx == 0:
                query += f"n:{label}"
            else:
                query += f" OR n:{label}"
    return query


def create_neo4j_node_query(node: Neo4jNode, index=0) -> str:
    """
    Generates a Cypher query string to create a node in a Neo4j database
    
    Args:
        node: Neo4jNodes - Node to create

    Returns:
        String containing Cypher query
    """
    props = neo4j_props_query(node.properties)

    n_id = f'n{index}'
    result =  f"""MERGE({n_id}:{node.labels[0]}{props})"""
    if len(node.labels) > 1:
        for label in node.labels[1:]:
            result += f"\nSET {n_id}:{label}"
    return result

def create_neo4j_nodes_list_query(nodes: list[Neo4jNode]) -> str:
    """
    Generates a multi-line Cypher query string to create multiple nodes in a Neo4j database
    
    Args:
        nodes: List of Neo4jNodes objects

    Returns:
        String containing multi-line Cypher query
    """
    result = ""
    for idx, node in enumerate(nodes):
        if idx > 0:
            result += "\n"
        result += create_neo4j_node_query(node, idx)
    return result

def create_nodes(
    creds: (str, str, str),
    nodes: list[Neo4jNode]
) -> bool:
    """
    Creates nodes in a target Neo4j database
    
    Args:
        creds: (str, str, str) - (neo4j_uri, neo4j_user, neo4j_password)
        nodes: list[Neo4jNodes] - list of nodes to create

    Returns:
        Bool indicating success or failure

    Raises:
        Exception if query fails
    """

    query = create_neo4j_nodes_list_query(nodes)

    # TODO: Verify nodes were created
    records = execute_query(creds, query)

    return True

# TODO: Update to take multiple labels
def get_nodes(
    creds: (str, str, str),
    node: Neo4jNode,
    limit: int = 20,
) -> list[Neo4jNode]:
    """
    Retrieves nodes from a target Neo4j database
    
    Returns:
        List of Neo4jNode objects

    Raises:
        Exception if query fails
    """
        
    query = get_neo4j_nodes_query(node)

    query += f"""RETURN n, labels(n) as labels"""
    if limit > 0:
        query += f""" LIMIT 20"""

    results = execute_query(creds, query)
    nodes = []
    for result in results:
        # Because of `RETURN n` above, the result will be a dict with a single key `n`
        node_data = result.data()['n']
        labels = result.data()['labels']
        if node_data is None:
            ModuleLogger().error(f'node using an unknown variable: {result}')
            continue
        nodes.append(Neo4jNode(
            labels=labels,
            properties=node_data,
        ))
    return nodes

# RELATIONSHIPS
def create_neo4j_relationship_query(relationship: Neo4jRelationship, index=0) -> (str, str):
    """
    Generates a Cypher query string to create a relationhip in a Neo4j database
    
    Args:
        relationship: Neo4jRelationship object
        index: Int to distinguish between nodes

    Returns:
        Tuple containing Cypher match clause strings and create clauses
    """
    props = neo4j_props_query(relationship.properties)

    # Target node
    n2_node = relationship.to_node
    n2_label = n2_node.labels[0]
    n2_props = neo4j_props_query(n2_node.properties)
    n2_id = f'tn{index}'
    target_node_query = f"({n2_id}:{n2_label}{n2_props})"

    # Source node 
    n1_node = relationship.from_node
    n1_label = n1_node.labels[0]
    n1_props = neo4j_props_query(n1_node.properties)
    n1_id = f'sn{index}'
    source_node_query = f"({n1_id}:{n1_label}{n1_props})"

    # Construct query
    match = f"MATCH {source_node_query}\nOPTIONAL MATCH {target_node_query}"
    create = f"""\nCREATE ({n1_id})-[:{relationship.type}{props}]->({n2_id})"""

    return match, create

def create_neo4j_relationship_list_query(relationships: list[Neo4jRelationship]) -> str:
    """
    Generates a multi-line Cypher query string to create multiple relationships in a Neo4j database
    
    Args:
        relationships: List of Neo4jRelationship objects

    Returns:
        String containing multi-line Cypher query
    """
    matches = ""
    creates = ""
    for idx, element in enumerate(relationships):
        n_matches, n_creates = create_neo4j_relationship_query(element, idx)
        if idx > 0:
            matches += "\n"
        matches += n_matches
        creates += n_creates

    matches += creates
    return matches


def create_relationships(
    creds: (str, str, str),
    relationships: list[Neo4jRelationship]
) -> bool:
    """
    Creates relationships in a target Neo4j database. NOTE that from and to nodes must already exist or no relationship will be created
    
    Args:
        creds: (str, str, str) - (neo4j_uri, neo4j_user, neo4j_password)
        relationships: list[Neo4jRelationship] - list of relationships to create

    Returns:
        Bool indicating success or failure.

    Raises:
        Exception if query fails
    """

    query = create_neo4j_relationship_list_query(relationships)

    ModuleLogger().info(f'query: {query}')
    records = execute_query(creds, query)
    ModuleLogger().info(f'records: {records}')

    # TODO: Check query summary for success

    return True