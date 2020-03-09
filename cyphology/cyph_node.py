import json
import re
from .cyph_property import create_property_string
regex_object_matcher = re.compile(r"(\S*) (\S*)( {.*})?")

class CyphNode:
    def __init__(self, string_representation, origin):
        self.uid = None
        self.type = None
        self.properties = {}
        self.attributes = []
        self.origin = origin

        self.parse(string_representation, origin)

    def parse(self, string_representation, origin):
        string_representation = string_representation.strip()
        matches = re.match(regex_object_matcher, string_representation)
        
        if matches:
            parts = matches.groups()
            
            # we need at least a type and a uid
            if parts[0] is None or parts[1] is None:
                raise Exception(f"Object Error 01: in line: '{string_representation}' seems to be an error, at least Class and UID are required in file {origin}")
            
            self.type = parts[0]
            self.uid = parts[1]

            # add properties if we have any
            if len(parts) > 2:
                try:
                    self.properties = json.loads(parts[2])
                except:
                    print(f"Error parsing json in file: {origin}")
                    print(string_representation)

            # if we manualy change the uid in the json object, then overwrite the internal uid
            if "uid" not in self.properties:
                self.properties["uid"] = self.uid

        else:
            raise Exception(f"Object Error 01a: in line: '{string_representation}' seems to be an error, at least Class and UID are required in file {origin}")

    def to_cypher(self, global_properties):
        properties = {**global_properties, **self.properties}
        property_string = create_property_string(properties)

        query_string = f"MERGE (:{self.type} {property_string})"
        return query_string

    def __str__(self):
        as_string = f"Type: {self.type}\nUID:{self.uid}\nProperties:{self.properties}"

        for attribute in self.attributes:
            as_string += f"\n{attribute}"

        return as_string

    
