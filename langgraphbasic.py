import pandas as pd
import os, math
from dotenv import load_dotenv
from typing import TypedDict, Optional, Dict, List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0)

#Hello world graph
#-Objs - Understand Agent state structure
#-Create simple nodes
#-compile and invoke langgraph graph
#-Understand data flow 
def First_graph():
    class AgentState(TypedDict): # State schema
        message : str

    def greeting_node(state : AgentState) -> AgentState: #Arrow represents the desired output for func
        """ Simple Node that adds a greeting message to the state"""    #Dock string
        state['message'] = "Hey " + state['message'] + " , how is your day going"

        return state
    
    graph = StateGraph(AgentState)  #graph init and its empty

    graph.add_node("greeter", greeting_node)    #Use add_node to add a node to graph

    #Setting the start node and end node
    graph.set_entry_point("greeter")
    graph.set_finish_point("greeter")

    app = graph.compile()   #Compiles the overall graph

    result = app.invoke({"message": "Bob"}) #Passing in a name to graph

    print(result["message"])

#First_graph()

def multi_in_graph():   #Multiple input langraph practice
    class Agentmultistate(TypedDict):
        values : List[int]
        name: str
        result: str

    def process_vals(state : Agentmultistate) -> Agentmultistate:
        """ This function handles multiple different inputs"""
        print(state)

        state['result'] = f"Hi there {state['name']}! Your sum = {sum(state['values'])}"

        print(state)
        return state

    graph3 = StateGraph(Agentmultistate)
    graph3.add_node('process', process_vals)
    graph3.set_entry_point('process')
    graph3.set_finish_point('process')
    app3 = graph3.compile() #make sure to always store the graph compile in var

    answers = app3.invoke({"values": [1,2,3,4], "name":'steve'})
    print(answers['result'])

#multi_in_graph()

def exercise2():
    class exercise2agent(TypedDict):
        values: List[int]
        name: str
        operation: str
        result : str

    def arithmetic_node(state: exercise2agent) -> exercise2agent:
        """ This node uses the given operation for arithmetic"""
        if state['operation'] == "*":
            state['result'] = f"Hi, {state['name']} result = {math.prod(state['values'])}"
        else:
            state['result'] = f"Hi, {state['name']} result = {sum(state['values'])}"

        return state

    exercise2graph = StateGraph(exercise2agent)

    exercise2graph.add_node("arithmetic", arithmetic_node)
    exercise2graph.set_entry_point("arithmetic")
    exercise2graph.set_finish_point("arithmetic")

    app4 = exercise2graph.compile()

    answers = app4.invoke({"values": [1,2,3,4], "name":'steve', "operation": "*"})
    print(answers['result'])

#exercise2()

def sequential_graph(): #Multi Node
    class seqagent(TypedDict):
        name: str
        age: str
        skills: List[str]
        final: str

    def first_node(state: seqagent) ->seqagent:
        """ This is first node of sequence"""

        state['final'] = f"{state['name']}, welcome to the system!"

        return state

    def second_node(state:seqagent) -> seqagent:
        '''This is second node'''

        state['final'] = state['final'] + f" You are {state['age']} years old!"

        return state

    def third_node(state: seqagent) -> seqagent:
        """ This is third node"""
        state['final'] = state['final'] + f"You have skills in: {state['skills']}"

        return state
    #building is the focus here
    seqgraph = StateGraph(seqagent)

    seqgraph.add_node("first node", first_node)
    seqgraph.add_node("second node", second_node)
    seqgraph.add_node("third node", third_node)

    seqgraph.set_entry_point("first node")
    #SETTING EDGES with add_edge(node one, node two)
    seqgraph.add_edge("first node", "second node")
    seqgraph.add_edge("second node", "third node")

    seqgraph.set_finish_point("third node")

    app5 = seqgraph.compile()

    seqres = app5.invoke({"name" : "Charlie", "age": "25", "skills": ['Python', 'SQL', 'Pandas']})
    print(seqres['final'])

#sequential_graph()


def conditional_graph():    #Adds/sub four nums for 2 conditional edges dem
    class conditionalagent(TypedDict):
        Number1 : int
        Number2 : int
        Number3: int
        Number4 : int
        Operation : str
        Operation2: str
        FinalNumber : int
        FinalNumber2: int

    def adder(state: conditionalagent) ->conditionalagent:
        """ Node adds two number"""
        state['FinalNumber'] = state['Number1'] + state['Number2']
        return state

    def sub(state: conditionalagent) ->conditionalagent:
        """ Node sub two number"""
        state['FinalNumber'] = state['Number1'] - state['Number2']
        return state

    def sub2(state: conditionalagent) ->conditionalagent:
        """ Node sub two number"""
        state['FinalNumber2'] = state['Number3'] - state['Number4']
        return state

    def adder2(state: conditionalagent) ->conditionalagent:
        """ Node sub two number"""
        state['FinalNumber2'] = state['Number3'] + state['Number4']
        return state

    def decide_next_node(state: conditionalagent) -> conditionalagent:
        """ This node will select next node of graph"""
        #This Node will be placed on graph before the two nodes to determine where to go
        if state['Operation'] == '+':
            return "addition_oper"#Return edge based on condition
        elif state['Operation'] == '-':
            return "sub_oper"#Returns edge for sub node

    def decide_next_node2(state: conditionalagent) -> conditionalagent:
        """ This node will select next node of graph"""
        #This Node will be placed on graph before the two nodes to determine where to go
        if state['Operation2'] == '+':
            return "addition_oper2"#Return edge based on condition
        elif state['Operation2'] == '-':
            return "sub_oper2"#Returns edge for sub node

    graph6 = StateGraph(conditionalagent)

    graph6.add_node("add", adder)
    graph6.add_node("sub", sub)
    graph6.add_node("router", lambda state:state)#Passthrough function state stays same

    graph6.add_edge(START, "router")    #This is same as entry point but easier connects to router
    
    graph6.add_conditional_edges(
        "router",   #conditional added node from earlier
        decide_next_node,       #Function for conditional func
        {
           "addition_oper": "add",  #Format in edge node dict of possible locations
            "sub_oper": "sub"
        }
    )

    graph6.add_node("add2", adder2)
    graph6.add_node("sub2", sub2)
    graph6.add_node("router2", lambda state:state)#Passthrough function state stays same


    graph6.add_edge("add", "router2")
    graph6.add_edge("sub", "router2")

    graph6.add_conditional_edges(
        "router2",   #conditional added node from earlier
        decide_next_node2,       #Function for conditional func
        {
           "addition_oper2": "add2",  #Format in edge node dict of possible locations
            "sub_oper2": "sub2"
        }
    )

    graph6.add_edge("add2", END)
    graph6.add_edge("sub2", END)

    #Same workflow for each conditional edge - define the nodes for condition
    #and condition function then draw edges to what you can for condition and repeat
    
    connapp = graph6.compile()

    connfin = connapp.invoke({"Number1": 2, "Number2": 3, "Operation": "+", "Number3": 6, "Number4": 6, "Operation2": "-"})
    print(connfin['FinalNumber'], connfin['FinalNumber2'])

conditional_graph()


