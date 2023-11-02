# Neo4j Intake
Generic processor for creating Neo4j nodes and relationships from .json or dictionary specifications.

# Install
```
pip install neo4j-intake
```

# Usage
```
import neo4j_intake as ni

neo4j_creds = ("<db_uri>", "<db_user>", "<db_password>")
new_nodes = [
    {
        "labels" : ["Person"],
        "properties" : { name: "John" }
    },
    {
        "labels" : ["Person"],
        "properties" : { name: "Jane" }
    },
]

ni.create_nodes(
    creds = neo4j_creds,
    nodes = new_nodes
)

new_relationships: [
    {
        "type" : "LOVES",
        "from_node: {
            "labels" : ["Person"]
            "properties": {
                "name": "John"
            }
        },
        "to_node: {
            "labels" : ["Person"]
            "properties": {
                "name": "Jane"
            }
        },
        "properties": {
            "since" : "2023-01-01"
        }
    }
]

ni.create_relationships(
    creds = neo4j_creds,
    relationships = new_relationships
)

```

# Specifications
The .json or dictionary argument for specifying Neo4j Node or Relationship details.

| Required Variables | Description | Value | Example |
|--|--| --| --|
| creds | A tuple of strings specifying the target Neo4j database uri, user, and password | tuple of strings | ("neo4j+s://2B7f7325.databases.neo4j.io", "neo4j", "kQu4oT2-FTBhhWxgSQ3Zn9-3n_b3vVRCF6gPg8g0zHE")


Key-value options for specifying Nodes.
| Node Variable | Description | Value | Required? |
|--|--| --| --|
| labels | Named category or Node type (ie Person, Company, etc.) | list of strings | No
| properties | Node attribute or properties | dictionary | No

Key-value options for specifying Relationships
| Relationship Variables | Description | Value | Required? |
|--|--| --| --|
| from_node | Source Node details (See Node Variables for options) | dictionary | Yes
| to_node | Target Node details (See Node Variables for options) | dictionary | Yes
| type | The name of the Relationship (ie WORKS_AT, OWNS, etc) | string | No
| properties | dictionary | No