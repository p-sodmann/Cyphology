import os
from .cyph_object import CyphObject
from .cyph_attribute import CyphAttribute
from neo4j import GraphDatabase

class Cyphology:
    def __init__(self, path):
        self.cyph_objects = []
        self.known_objects = set()

        self.parse(path)

    def __len__(self):
        return len(self.cyph_objects)

    def parse(self, path):
        with open(path, encoding="utf-8") as file:
            for line in file.readlines():
                # ignore empty lines, one character is the line break
                if len(line) > 1:
                    
                    # ignore comments
                    if line.startswith("#"):
                        pass

                    # enable imports
                    elif line.startswith("import"):
                        file_to_import = line.split()[1]
                        head, tail = os.path.split(path)

                        self.parse(head + os.path.sep + file_to_import)
                        continue
                    
                    else:
                        if line.startswith("\t"):
                            # lines beginning with a tab are attributes to the previous object

                            # we can only append an attribute if we have an object
                            if not len(self.cyph_objects):
                                raise Exception(f"Error 02: The syntax of your file {path} seems to be faulty, no Object was found for line {line}, do you have a rouge tabulator?")
                            
                            cyph_attribute = CyphAttribute(line)

                            # Raise exception, if the target object was not defined
                            if cyph_attribute.uid not in self.known_objects:
                                raise Exception(f"Error 04: target object {cyph_attribute.uid} is not known yet")

                            self.cyph_objects[-1].add_attribute(cyph_attribute)
                            

                        else:
                            cyph_object = CyphObject(line)

                            # dont allow multiple instances of an Object
                            # unsure if there isnt a usecase for this
                            if cyph_object.uid in self.known_objects:
                                raise Exception(f"Error 03: Object is already known, please merge occurences of {cyph_object.uid}")

                            
                            self.known_objects.add(cyph_object.uid)
                            self.cyph_objects.append(cyph_object)


    def write_to_neo4j(self):
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "meow"))

        with driver.session() as session:
            for cyph_object in self.cyph_objects:
                session.write_transaction(cyph_object.create_cypher)