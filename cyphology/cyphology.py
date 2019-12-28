import os
from .cyph_object import CyphObject
from .cyph_attribute import CyphAttribute
from neo4j import GraphDatabase
import json


class Cyphology:
    def __init__(self, path):
        self.cyph_objects = []
        self.known_objects = set()
        
        # defaults belong to a type of Node 
        self.defaults = {}

        # globals belong to every Node/Edge
        self.global_properties = {}

        # set properties to match on
        self.match_on = ["uid"]

        self.parse(path)
        

    def __len__(self):
        return len(self.cyph_objects)

    def parse(self, path):
        path = os.path.normpath(path)

        with open(path, encoding="utf-8") as file:
            for line in file.readlines():
                # ignore empty lines, one character is the line break
                if len(line.strip()) > 1:
                    
                    if line.strip().startswith("#"):
                        # this is a coment, dont do anything here
                        continue

                    
                    elif line.startswith("import "):
                        # enable imports
                        file_to_import = line.split()[1]
                        head, _ = os.path.split(path)

                        self.parse(head + os.path.sep + file_to_import)

                    elif line.startswith("index"):
                        self.add_index(line)

                    elif line.startswith("default "):
                        # set a default value to an edge or a node
                        self.add_default(line)
                    
                    else:
                        if line.startswith(("\t", " ")):
                            # all indented lines are treated as attribute (child) of the object
                            self.add_attribute(line)
                            
                        else:
                            # non indented lines are new objects
                            self.add_object(line)


    def add_attribute(self, line):
        # lines beginning with a tab are attributes to the previous object
        # we can only append an attribute if we have an object
        if not self.cyph_objects:
            raise Exception(f"Error 02: The syntax of your file seems to be faulty, no Object was found for line {line}, do you have a rouge tabulator?")
        
        cyph_attribute = CyphAttribute(line)

        # add defaults and overwrite them if a value is set.
        if cyph_attribute.type in self.defaults:
            cyph_attribute.properties = {**self.defaults[cyph_attribute.type], **cyph_attribute.properties}

        # Raise exception, if the target object was not definedyo c
        if cyph_attribute.uid not in self.known_objects:
            raise Exception(f"Error 04: target object {cyph_attribute.uid} is not known yet")

        self.cyph_objects[-1].add_attribute(cyph_attribute)

    def add_index(self, line):
        pass

    def add_object(self, line):
        cyph_object = CyphObject(line)
        
        # add defaults and overwrite them if a value is set.
        if cyph_object.type in self.defaults:
            cyph_object.properties = {**self.defaults[cyph_object.type], **cyph_object.properties}

        # dont allow multiple instances of an Object
        # unsure if there isnt a usecase for this
        if cyph_object.uid in self.known_objects:
            raise Exception(f"Error 03: Object is already known, please merge occurences of {cyph_object.uid}")


        self.known_objects.add(cyph_object.uid)
        self.cyph_objects.append(cyph_object)


    def add_default(self, line):
        line = line.strip()
        objects = line.split()

        if len(objects) >= 3:
            head = objects[1]
            tail = json.loads(" ".join(objects[2:]))

            self.defaults[head] = tail
        
        else:
            raise Exception(f"Error 04: Mistake in creating default: \n {line}")


    def create_cypher(self, tx, cypher_object):
        # this will produce a node with arbitrary properties
        
        properties = {**self.global_properties, **cypher_object.properties}
        property_string = self.create_property_string(properties)
            
        query_string = f"MERGE (:{cypher_object.type} {property_string})"

        tx.run(query_string, cypher_object.properties)

        # add relationships to other nodes

        # generate parent match criteria
        match_criteria_source = {selector+"_source": properties[selector] for selector in self.match_on}
        match_string_source = ", ".join([f"{selector}:${selector}_source" for selector in self.match_on])
        match_string_destination = ", ".join([f"{selector}:${selector}_destination" for selector in self.match_on])

        for attribute in cypher_object.attributes:
            # merge global properties and the attribute propperties
            attribute_properties = {**self.global_properties, **attribute.properties}
            attribute_property_string = self.create_property_string(attribute_properties)
            
            # generate the criteria for the child            
            match_criteria_destination = {selector+"_destination":attribute_properties[selector] for selector in self.match_on}
            match_criteria = {**match_criteria_source, **match_criteria_destination}

            if attribute.direction == ">":
                query_string = f"MATCH (source {{{match_string_source}}}) OPTIONAL MATCH (destination {{{match_string_destination}}}) MERGE (source)-[:{attribute.type} {attribute_property_string}]->(destination)"

            elif attribute.direction == "<":
                query_string = f"MATCH (source {{{match_string_source}}}) OPTIONAL MATCH (destination {{{match_string_destination}}}) MERGE (source)<-[:{attribute.type} {attribute_property_string}]-(destination)"

            else:
                raise Exception(f"Object Error 02: in line: '{attribute_property_string}' seems to be an error, direction not supported")
            
            tx.run(query_string, match_criteria)


    def write_to_neo4j(self, username="neo4j", password="meow"):
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=(username, password))

        with driver.session() as session:
            for cyph_object in self.cyph_objects:
                self.create_cypher(session, cyph_object)
                

    @staticmethod
    def create_property_string(properties):
        if properties:
            property_string = "{"
            first = True

            for field, value in properties.items():
                if not first:
                    property_string += ", "
                else:
                    first = False

                if isinstance(value, (int, float, bool)):
                    property_string += f"{field}: {value}"
                else: 
                    property_string += f"{field}: '{value}'"

            property_string += "}"
        else:
            property_string = ""
        
        return property_string