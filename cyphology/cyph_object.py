import json
from .cyph_attribute import CyphAttribute

class CyphObject:
    def __init__(self, string_representation):
        self.uid = None
        self.type = None
        self.properties = {}

        self.attributes = []
        
        string_representation = string_representation.strip()
        parts = string_representation.split()

        # we need at least a type and a uid
        if len(parts) < 2:
            raise Exception(f"Error 01: in line: '{string_representation}' seems to be an error")

        self.type = parts[0]
        self.uid = parts[1]

        # add properties if we have any
        if len(parts) > 2:
            rest_string = " ".join(parts[2:])
            try:
                self.properties = json.loads(rest_string)
            except:
                print(string_representation)

        self.properties["uid"] = self.uid

    def __str__(self):
        as_string = f"Type: {self.type}\nUID:{self.uid}\nProperties:{self.properties}"

        for attribute in self.attributes:
            as_string += f"\n{attribute}"

        return as_string

    def add_attribute(self, attribute):
        self.attributes.append(attribute)

    def create_cypher(self, tx):
        # this will produce a node with arbitrary properties
        if len(self.properties):
            property_string = "{"
            first = True

            for field, _ in self.properties.items():
                if not first:
                    property_string += ", "
                else:
                    first = False

                property_string += f"{field}: ${field}"

            property_string += "}"
        else:
            property_string = ""
        
        query_string = f"MERGE (:{self.type} {property_string})"

        tx.run(query_string, self.properties)

        # add relationships to other nodes

        for attribute in self.attributes:
            query_string = f"MATCH (source {{uid:$uid_source}}) OPTIONAL MATCH (destination {{uid:$uid_destination}}) MERGE (source)-[:{attribute.type}]->(destination)"
            tx.run(query_string, uid_source=self.uid, uid_destination=attribute.uid)
