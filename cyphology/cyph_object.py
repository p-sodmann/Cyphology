import json
import re

regex_object_matcher = re.compile(r"(\S*) (\S*)( {.*})?")

class CyphObject:
    def __init__(self, string_representation):
        self.uid = None
        self.type = None
        self.properties = {}
        self.attributes = []
        
        string_representation = string_representation.strip()
        matches = re.match(regex_object_matcher, string_representation)
        
        if matches:
            parts = matches.groups()
            
            # we need at least a type and a uid
            if parts[0] is None or parts[1] is None:
                raise Exception(f"Object Error 01: in line: '{string_representation}' seems to be an error, at least Class and UID are required")
            
            self.type = parts[0]
            self.uid = parts[1]

            # add properties if we have any
            if len(parts) > 2:
                try:
                    self.properties = json.loads(parts[2])
                except:
                    pass
                    #print(string_representation)

            self.properties["uid"] = self.uid

        else:
            raise Exception(f"Object Error 01a: in line: '{string_representation}' seems to be an error, at least Class and UID are required")

    def __str__(self):
        as_string = f"Type: {self.type}\nUID:{self.uid}\nProperties:{self.properties}"

        for attribute in self.attributes:
            as_string += f"\n{attribute}"

        return as_string

    def add_attribute(self, attribute):
        self.attributes.append(attribute)

    @staticmethod
    def create_property_string(properties):
        if not properties:
            property_string = "{"
            first = True

            for field, value in properties.items():
                if not first:
                    property_string += ", "
                else:
                    first = False

                property_string += f"{field}: '{value}'"

            property_string += "}"
        else:
            property_string = ""
        
        return property_string

    def create_cypher(self, tx):
        # this will produce a node with arbitrary properties
        
        property_string = self.create_property_string(self.properties)
        query_string = f"MERGE (:{self.type} {property_string})"

        tx.run(query_string, self.properties)

        # add relationships to other nodes

        for attribute in self.attributes:
            attribute_property_string = self.create_property_string(attribute.properties)
            query_string = f"MATCH (source {{uid:$uid_source}}) OPTIONAL MATCH (destination {{uid:$uid_destination}}) MERGE (source)-[:{attribute.type} {attribute_property_string}]->(destination)"
            tx.run(query_string, uid_source=self.uid, uid_destination=attribute.uid)
