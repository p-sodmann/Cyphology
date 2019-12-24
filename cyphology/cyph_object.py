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
                    print("error!")
                    print(string_representation)

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
    
