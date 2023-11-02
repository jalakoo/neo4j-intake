from pydantic import BaseModel

class Neo4jNode(BaseModel):
    labels: list[str] = []
    properties: dict = None
    
class Neo4jRelationship(BaseModel):
    type: str
    from_node: Neo4jNode
    to_node: Neo4jNode
    properties: dict = None