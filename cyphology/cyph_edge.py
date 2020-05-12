import re
import json
from .cyph_property import create_property_string

regex_attribute_matcher = re.compile(r"(\S*) ({.*?} )?([<->]) (.*)")

class CyphEdge:
    def __init__(self, string_representation):
        self.type = None
        self.direction = None
        
        self.source_node = None
        self.target_node = None
        self.target_uid = None

        self.properties = {}
        
        self.parse(string_representation)

    def parse(self, string_representation: str):
        string_representation = string_representation.strip()
        matches = re.match(regex_attribute_matcher, string_representation)

        if matches:
            parts = matches.groups()

            # representations need at least 3 groups: Type direction UID
            if len(parts) < 3:
                raise Exception(f"Attibute Error 00: in line: '{string_representation}' seems to be an error")
            
            self.type = parts[0]
            if parts[1] is not None:
                try:
                    self.properties = json.loads(parts[1])
                except:
                    raise Exception(f"Attribute Error 02: failed parsing json in line: {string_representation} Json: {parts[1]}")
                
            self.direction = parts[2]

            self.target_uid = parts[3]

        else:
            raise Exception(f"Attibute Error 01: could not parse '{string_representation}'")

    def generate_uid(self):
        self.properties["uid"] = self.source_node.properties["uid"] + self.direction + self.type + self.direction + self.target_node.properties["uid"]

    def to_cypher(self, match_on, global_properties, session):
        # uid: $uid, x: $x
        match_string_source = ", ".join([f"{m}: $source_{m}" for m in match_on]) 
        match_string_target = ", ".join([f"{m}: $target_{m}" for m in match_on]) 

        property_string = create_property_string({**global_properties, **self.properties})

        if self.direction == ">":
            query_string = (
                f"MATCH (source:{self.source_node.type} {{{match_string_source}}}) " 
                f"OPTIONAL MATCH (target:{self.target_node.type} {{{match_string_target}}}) "
                f"MERGE (source)-[:{self.type} {property_string}]->(target)"
                )

        properties = {
            **{f"source_{m}":{**global_properties, **self.source_node.properties}[m] for m in match_on}, 
            **{f"target_{m}":{**global_properties, **self.target_node.properties}[m] for m in match_on}
        }

        session.run(query_string, **properties)

    def __str__(self):
        return f"{self.type} {self.direction} {self.properties}"