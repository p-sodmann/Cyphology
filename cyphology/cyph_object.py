import json
from .cyph_attribute import CyphAttribute

class CyphObject:
    def __init__(self, string_representation):
        self.uid = None
        self.type = None
        self.properties = None

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
            self.properties = json.loads(rest_string)

    def __str__(self):
        as_string = f"Type: {self.type}\nUID:{self.uid}\nProperties:{self.properties}"

        for attribute in self.attributes:
            as_string += f"\n{attribute}"

        return as_string

    def add_attribute(self, attribute):
        self.attributes.append(attribute)