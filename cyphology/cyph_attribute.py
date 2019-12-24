import re
import json

regex_attribute_matcher = re.compile(r"(\S*) ({.*?} )?([<->]) (\S*)")

class CyphAttribute:
    def __init__(self, string_representation):
        string_representation = string_representation.strip()
        matches = re.match(regex_attribute_matcher, string_representation)

        self.type = None
        self.direction = None
        self.uid = None
        self.properties = {}
        
        if matches:
            parts = matches.groups()

            # representations need at least 3 groups: Type direction UID
            if len(parts) < 3:
                raise Exception(f"Attibute Error 00: in line: '{string_representation}' seems to be an error")
            
            self.type = parts[0]
            if parts[1] is not None:
                self.properties = json.loads(parts[1])
                
            self.direction = parts[2]
            self.uid = parts[3]

            self.properties["uid"] = self.uid

        else:
            raise Exception(f"Attibute Error 01: could not parse '{string_representation}'")

    def __str__(self):
        return f"{self.type} {self.direction} {self.uid} {self.properties}"