
#Represents a Node of the CFG
# Contains: An id that represents the node, code_statement that represents the code line that is being re
class Node:
    def __init__(self, node_id, label):
        self.id = node_id
        self.label = label

#This class represents the CFG
class CFG:
    def __init__(self):

        self.nodes = [] #List to store all the nodes
        self.edges = [] #list to store all the edges
        self.node_counter = 0

    def add_node(self, label): #Adds a node to the cfg


        node = Node(self.node_counter, label) #creates a new node
        self.nodes.append(node) #appends the node to the node list
        self.node_counter += 1 #increases the count by 1

        return node.id #returrns the id of the node

    def add_edge(self, from_node, to_node): #adds an edge 
        # Takes a from_node(the node where the edge originates from) and to_node(the node where the edge ends)
        self.edges.append((from_node, to_node)) #appends the edge to the list of edges


    def print_graph(self):#Prints the list of vertices and edges
        print("Vertices:") #Prints the list of vertices
        for node in self.nodes:
            print(f"Node {node.id}: {node.label}")

        print("\nEdges:")#Prins the list of edges

        for edge in sorted(self.edges, key=lambda x: (x[0], x[1])):
            print(f"{edge[0]} -> {edge[1]}")

class Parser:
    def __init__(self, lines):

        self.lines = [self.trim(l) for l in lines if self.trim(l)]
        self.index = 0
        self.cfg = CFG()

    def trim(self, s): #This function removes whitespace fromt he text file
        return s.strip()

    def check_keyword(self, keyword):# This function checks for keywords like if, else, whle,
        return self.index < len(self.lines) and self.lines[self.index].startswith(keyword)

    def parse_statement(self): #this function is used to parse the statements
        line = self.lines[self.index] #gets a line from the list of lines
        self.index += 1 
        return self.cfg.add_node(line) #adds a node with the line
    


    def parse_block(self):# Responsible for parsing a condition block

        has_braces = False #bool to check if the block has braces


        if self.index < len(self.lines) and self.lines[self.index] == "{": #Checks to see if the block contains {
            #This indicates the beginning of the block by setting the bool to true
            has_braces = True
            self.index += 1 

        first_node = last_exit = None



        #main handling of parsing a block

        while self.index < len(self.lines):

            #Breaks from the block when encountering }, which means the end of the block has been met
            if has_braces and self.lines[self.index] == "}":
                self.index += 1
                break

            #Uses the check_keyword function to check if there is an if
            if self.check_keyword("if"):
                #Calls the parse if function
                entry, exit_nodes = self.parse_if()
            #Same as previous function, but checks for while keyword
            elif self.check_keyword("while"):
                #Calls the parse while function
                entry, exit_nodes = self.parse_while()

            #Same as the previous function, but checks for do keyword    
            elif self.check_keyword("do"):
                #Calls the do while parsing function
                entry, exit_nodes = self.parse_do_while()
            #Checks for else keyword
            elif self.check_keyword("else"):
                return first_node, last_exit  # Return to let parse_if handle the else
            
            #Checks for the {, which means the beginning of a block and calls the parse block function
            elif self.lines[self.index] == "{":
                entry, exit_nodes = self.parse_block()

            #if none of the above conditions are met, call the parse_statement function which will parse a simple statement
            else:
                entry = self.parse_statement()
                exit_nodes = [entry]


            if first_node is None:
                first_node = entry


            if last_exit is not None:
                self.cfg.add_edge(last_exit, entry)
            last_exit = exit_nodes[-1] if isinstance(exit_nodes, list) else exit_nodes

            if not has_braces:
                break
        


        if first_node is None:
            passthrough = self.cfg.add_node("empty_block")
            return passthrough, passthrough
        return first_node, last_exit

    def parse_if(self): #This function handles if and if else conditions

        if_node = self.cfg.add_node(self.lines[self.index]) # Adds the if node to the list of nodes
        self.index += 1 
        true_entry, true_exit = self.parse_block() #true entry, true exit represent entering and exiting the true condition of the if branch

        self.cfg.add_edge(if_node, true_entry) #adds the edge from the if node to the true entry





        if self.index < len(self.lines) and self.lines[self.index] == "else": #Checks for an else connected to the if statement
            self.index += 1 
            false_entry, false_exit = self.parse_block() #same as true entry, true exit, but now they are responsible for the false condition of the if else statement
            self.cfg.add_edge(if_node, false_entry) #adds the edge from if node to false entry


            join_node = self.cfg.add_node("join") #for the if else conditions, a node will be created call join that will join the if and else branch into 1 node

            self.cfg.add_edge(true_exit, join_node) #adds edge from true branch exit to join node
            self.cfg.add_edge(false_exit, join_node) #adds edge from false branc exit to join node
            
            return if_node, join_node #returns the if node and join node
        else:
            return if_node, join_node

    def parse_while(self): #This function handles while loops

        #Adds a while node to the list of nodes
        while_node = self.cfg.add_node(self.lines[self.index])
        self.index += 1

        #Same logic, where body_entry represents entering into the while loop, and body exit represents leaving the while loop
        body_entry, body_exit = self.parse_block() #parses the while block

        self.cfg.add_edge(while_node, body_entry)#adds an edge from while node to body_entry
        self.cfg.add_edge(body_exit, while_node)#addsd an edge from the exit back to the beginning of the while loop(while_node)

        return while_node, while_node

    def parse_do_while(self): #This fucntion handles do whiles


        #Adds a do node to the list of nodes
        do_node = self.cfg.add_node(self.lines[self.index])  
        self.index += 1

        #same logic as while loop, see while loop for information about this line
        body_entry, body_exit = self.parse_block()

        while_condition = self.cfg.add_node(self.lines[self.index])  #handles the while condition
        self.index += 1
        self.cfg.add_edge(do_node, body_entry) #adds an edge from the do node to the body entry

        self.cfg.add_edge(body_exit, while_condition)#Creates a node from the body of exit of do node to the while condition node

        self.cfg.add_edge(while_condition, body_entry)#creates a node from the while condition node to the body entry node, creating a loop
        return do_node, while_condition

    def parse(self):

        start_node = None
        last_exits = []

        #Contains the same logic as parse block, but used for code that is not within a block/condition block
        while self.index < len(self.lines):


            if self.check_keyword("if"): #Checks for if keyword and calls the if parsing function
                entry, exit_node = self.parse_if()

            elif self.check_keyword("while"): #Checks for while keyword and calls while parsing function
                entry, exit_node = self.parse_while()

            elif self.check_keyword("do"):#same thing for do while
                entry, exit_node = self.parse_do_while()

            elif self.lines[self.index] == "{": #Checks for the indication of the beginning of a code block and calls the parse block functio
                entry, exit_node = self.parse_block()
            else:
                entry = self.parse_statement() 
                exit_node = entry

            if start_node is None:
                start_node = entry


            for last_exit in last_exits:
                self.cfg.add_edge(last_exit, entry)
            last_exits = [exit_node] if isinstance(exit_node, int) else [exit_node]

        return self.cfg

def read_txt_lines(txt_filename): # receives the txt file name and reads the lines inside the file
    #Opens the file and reads it
    with open(txt_filename, 'r') as f:
        lines = [] #Stores the list of lines

        for line in f: #for every line in the file
            clean_line = line.strip() #Remove whitespace


            if "//" in clean_line:
                clean_line = clean_line.split("//")[0].strip()#handles comments
            if clean_line:
                lines.append(clean_line) #appends the cleaned lines to the list of lines


        return lines

if __name__ == "__main__":
    txt_file = "testing_data.txt" 
    lines = read_txt_lines(txt_file)
    parser = Parser(lines)
    cfg = parser.parse()
    cfg.print_graph()
