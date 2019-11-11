# Cyphology

A library to create ontologies for Neo4J in a human readable way.  
Cyphology is able to read and insert ontologies written in "cyphol".  

`
# Example data
GraphDb neo4j

Language cypher {"created_in":2011, "written_by":"Andrés Taylor"}	
	used_for > neo4j
  
Language cyphol {"created_in":2019, "written_by": "Philipp Sodmann"}
	used_for > neo4j
	inspired_by > cypher
`

Cyphologie is also capable to validate the Data before inserting it into Neo4J.  
It is in early development for my private project.
