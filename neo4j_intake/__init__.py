import neo4j_intake.database as db
from neo4j_intake.models import Neo4jNode, Neo4jRelationship
from pydantic import parse_obj_as
import json

def get_nodes(creds: (str, str, str), node: dict | str) -> list[Neo4jNode]:
    """
    Retrieves nodes from a target Neo4j database
    
    Arguments:
        creds: tuple of (uri, username, password) for target database
        node: Dictionary or stringified .json representation of a Neo4jNode object that specifies labels and properties to match against.

    Returns:
        List of dictionaries representing Neo4jNode objects

    Raises:
        Exception if .json conversion or query fails
    """
    if isinstance(node, str):
        node = json.loads(node)
        
    converted_nodes = parse_obj_as(Neo4jNode, node)
    return db.get_nodes(creds, converted_nodes)

def create_nodes(creds: (str, str, str), nodes: list[dict]) -> bool:
    """
    Creates nodes to a target Neo4j database
    
    Arguments:
        creds: tuple of (uri, username, password) for target database
        nodes: list of dictionaries or stringified .json representation of a list of Neo4jNode objects.

    Returns:
        Bool if query successfully ran.

    Raises:
        Exception if query fails
    """
    if isinstance(nodes, str):
        nodes = json.loads(nodes)
    converted_nodes = parse_obj_as(list[Neo4jNode], nodes)
    return db.create_nodes(creds, converted_nodes)


def create_relationships(creds: (str, str, str), relationships: list[dict], dedupe: bool = False) -> bool:
    """
    Creates Relationships to a target Neo4j database

    Arguments:
        creds: tuple of (uri, username, password) for target database
        relationships: list of dictionaries or stringified .json representation of a list of Neo4jRelationships objects. Note that these must also contain Neo4jNode objects for specifying from and to nodes.
        dedupe: Bool to dedupe relationships if they already exist.

    Returns:
        Bool if query successfully ran.

    Raises:
        Exception if query fails
    """
    converted_nodes = parse_obj_as(list[Neo4jRelationship], relationships)
    return db.create_relationships(creds, converted_nodes, dedupe=dedupe)