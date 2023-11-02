import pytest
from neo4j_intake.models import Neo4jNode, Neo4jRelationship
from neo4j_intake.database import get_neo4j_nodes_query, create_neo4j_node_query, create_neo4j_nodes_list_query,create_neo4j_relationship_query, create_neo4j_relationship_list_query


# @pytest.fixture(scope="module")
# def get_nodes():
#     return {
#     }

class TestDatabaseGetNodes():
    def test_get_neo4j_nodes_query_no_labels_or_props(self):
        node = Neo4jNode()
        expected = 'MATCH (n)'
        
        query = get_neo4j_nodes_query(node)

        assert expected == query

    def test_get_neo4j_nodes_query_single_label(self):
        node = Neo4jNode(labels=["Person"])
        expected = 'MATCH (n)\nWHERE n:Person'

        query = get_neo4j_nodes_query(node)

        assert expected == query

    def test_get_neo4j_nodes_query_multiple_labels(self):
        node = Neo4jNode(labels=["Person", "Employee"])
        expected = 'MATCH (n)\nWHERE n:Person OR n:Employee'

        query = get_neo4j_nodes_query(node)

        assert expected == query

    def test_get_neo4j_nodes_query_properties(self):
        node = Neo4jNode(properties={"name": "Alice"})
        expected = 'MATCH (n { name: "Alice" })'

        query = get_neo4j_nodes_query(node)

        assert expected == query

class TestDatabaseCreateSingleNodes():

    def test_create_neo4j_node_query_single_label(self):
        node = Neo4jNode(
            labels=["Person"],
            properties={"name": "John"}
        )
        expected = 'MERGE(n0:Person { name: "John" })'
        
        query = create_neo4j_node_query(node)

        assert expected == query

    def test_create_neo4j_node_query_multiple_labels(self):
        node = Neo4jNode(
            labels=["Person", "Employee"], 
            properties={"name": "Jane"}
        )
        expected = 'MERGE(n0:Person { name: "Jane" })\nSET n0:Employee'
        
        query = create_neo4j_node_query(node)

        assert expected == query

    def test_create_neo4j_node_query_properties(self):
        node = Neo4jNode(
            labels=["Car"],
            properties={"make": "Toyota", "model": "Prius"}
        )
        expected = 'MERGE(n0:Car { make: "Toyota", model: "Prius" })'

        query = create_neo4j_node_query(node)

        assert expected == query

    def test_create_neo4j_node_query_no_properties(self):
        node = Neo4jNode(
            labels=["Fish"]
        )
        expected = 'MERGE(n0:Fish)'

        query = create_neo4j_node_query(node)

        assert expected == query

class TestCreateMultipleNodes():
    def test_create_neo4j_nodes_list_query_single_node(self):
        nodes = [
            Neo4jNode(labels=["Person"], properties={"name": "Alice"})
        ]
        expected = 'MERGE(n0:Person { name: "Alice" })'

        query = create_neo4j_nodes_list_query(nodes)

        assert expected == query

    def test_create_neo4j_nodes_list_query_multiple_nodes(self):
        nodes = [
            Neo4jNode(labels=["Person"], properties={"name": "Bob"}),
            Neo4jNode(labels=["City"], properties={"name": "London"})
        ]
        expected = """MERGE(n0:Person { name: "Bob" })\nMERGE(n1:City { name: "London" })"""

        query = create_neo4j_nodes_list_query(nodes)

        assert expected == query  


class TestCreateRelationship():

    def test_create_neo4j_relationship_query_basic(self):
        start_node = Neo4jNode(labels=["Person"], properties={"name":"Alice"})
        end_node = Neo4jNode(labels=["City"], properties={"name":"London"})
        rel = Neo4jRelationship(type="LIVES_IN", from_node=start_node, to_node=end_node)

        expected_match = 'MATCH (sn0:Person { name: "Alice" })\nOPTIONAL MATCH (tn0:City { name: "London" })'
        expected_create = '\nCREATE (sn0)-[:LIVES_IN]->(tn0)'
        match, create = create_neo4j_relationship_query(rel)

        assert expected_match == match
        assert expected_create == create

    def test_create_neo4j_relationship_query_properties(self):
        start_node = Neo4jNode(labels=["Person"], properties={"name":"Bob"})
        end_node = Neo4jNode(labels=["Car"], properties={"make":"Toyota"})
        rel = Neo4jRelationship(from_node=start_node, to_node=end_node, type="OWNS", properties={"since": 2022})

        expected_match = 'MATCH (sn0:Person { name: "Bob" })\nOPTIONAL MATCH (tn0:Car { make: "Toyota" })'
        expected_create = '\nCREATE (sn0)-[:OWNS { since: 2022 }]->(tn0)'
        match, create = create_neo4j_relationship_query(rel)

        assert expected_match == match
        assert expected_create == create

class TestCreateRelationships():
    def test_create_neo4j_relationship_list_query_single_rel(self):
        start_node = Neo4jNode(labels=["Person"], properties={"name":"Alice"})
        end_node = Neo4jNode(labels=["City"], properties={"name":"London"})
        rel = Neo4jRelationship(from_node=start_node, to_node=end_node, type="LIVES_IN")
        relationships = [rel]

        expected = """MATCH (sn0:Person { name: "Alice" })\nOPTIONAL MATCH (tn0:City { name: "London" })\nCREATE (sn0)-[:LIVES_IN]->(tn0)"""

        query = create_neo4j_relationship_list_query(relationships)

        assert expected == query

    def test_create_neo4j_relationship_list_query_multiple_rels(self):
        # Define nodes and relationships
        start_node1 = Neo4jNode(labels=["Person"], properties={"name":"Alice"})
        end_node1 = Neo4jNode(labels=["City"], properties={"name":"London"})
        rel1 = Neo4jRelationship(from_node=start_node1, to_node=end_node1, type="LIVES_IN")

        start_node2 = Neo4jNode(labels=["Person"], properties={"name":"Bob"})
        end_node2 = Neo4jNode(labels=["Car"], properties={"make":"Toyota"})
        rel2 = Neo4jRelationship(from_node=start_node2, to_node=end_node2, type="OWNS")
        
        relationships = [rel1, rel2]

        # Expected query string
        expected = """MATCH (sn0:Person { name: "Alice" })\nOPTIONAL MATCH (tn0:City { name: "London" })\nMATCH (sn1:Person { name: "Bob" })\nOPTIONAL MATCH (tn1:Car { make: "Toyota" })\nCREATE (sn0)-[:LIVES_IN]->(tn0)\nCREATE (sn1)-[:OWNS]->(tn1)"""

        query = create_neo4j_relationship_list_query(relationships)

        assert expected == query