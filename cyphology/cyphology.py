import os

from .cyph_node import CyphNode
from .cyph_edge import CyphEdge

from neo4j import GraphDatabase
import json
from tqdm import tqdm
import warnings

class Cyphology:
    def __init__(self, path):
        self.nodes = []
        self.known_nodes = {}
        self.edges = []

        self.current_file = path
        
        # defaults belong to a type of Node 
        self.defaults = {}

        # globals belong to every Node/Edge
        self.global_properties = {}

        # set properties to match on
        self.match_on = ["uid"]

        self.parse(path)
        

    def __len__(self):
        return len(self.nodes)

    def parse(self, path):
        path = os.path.normpath(path)
        self.current_file = path

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
                        
                        # reset current file
                        self.current_file = path

                    elif line.startswith("index"):
                        self.add_index(line)

                    elif line.startswith("default "):
                        # set a default value to an edge or a node
                        self.add_default(line)
                    
                    else:
                        if line.startswith(("\t", " ")):
                            # all indented lines are treated as attribute (child) of the object
                            self.add_edge(line)
                            
                        else:
                            # non indented lines are new objects
                            self.add_node(line)
        
    def add_node(self, line):
        node = CyphNode(line, origin=self.current_file)
        
        # add defaults and overwrite them if a value is set.
        if node.type in self.defaults:
            node.properties = {**self.defaults[node.type], **node.properties}

        # dont allow multiple instances of an Object
        # unsure if there isnt a usecase for this
        if node.uid in self.known_nodes:
            original = self.nodes[self.known_nodes[node.uid]]

            warnings.warn(f"Warning 01: Object is already known, please merge occurences of {node.uid} first occurence: {original.origin} second occurence: {self.current_file}")

        else:
            self.nodes.append(node)
            self.known_nodes[node.uid] = len(self.nodes) - 1

    def add_edge(self, line):
        # lines beginning with a tab are attributes to the previous node
        # we need to have the origin and the target node to be defined
        if not self.nodes:
            raise Exception(f"Error 02: The syntax of your file seems to be faulty, no Object was found for line {line}, do you have a rouge tabulator?")
        
        edge = CyphEdge(line)

        # add defaults and overwrite them if a value is set.
        if edge.type in self.defaults:
            edge.properties = {**self.defaults[edge.type], **edge.properties}

        # Raise exception, if the target object was not defined
        if edge.target_uid in self.known_nodes:
            edge.source_node = self.nodes[-1]
            edge.target_node = self.nodes[self.known_nodes[edge.target_uid]]
            edge.generate_uid()

        else:
            raise Exception(f"Error 05: target object {edge.target_uid} in file: {self.current_file} is not known yet")
        
        self.edges.append(edge)

    def add_index(self, line):
        pass

    def add_default(self, line):
        line = line.strip()
        objects = line.split()

        if len(objects) >= 3:
            head = objects[1]
            tail = json.loads(" ".join(objects[2:]))

            self.defaults[head] = tail
        
        else:
            raise Exception(f"Error 04: Mistake in creating default: \n {line}")

    def write_to_neo4j(self, username="neo4j", password="meow", session=None):
        if session is None:
            driver = GraphDatabase.driver("bolt://localhost:7687", auth=(username, password))

            with driver.session() as session:
                self.transmit(session)
            
        else:
            self.transmit(session)
                

    def transmit(self, session):
        for e, node in enumerate(tqdm(self.nodes)):
            session.run(node.to_cypher(self.global_properties))
            if e % 1000:
                session.sync()

        for e, edge in enumerate(tqdm(self.edges)):
            edge.to_cypher(self.match_on, self.global_properties, session)
            if e % 1000:
                session.sync()