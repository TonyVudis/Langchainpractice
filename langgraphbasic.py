import pandas as pd
import os, math, random
from dotenv import load_dotenv
from typing import TypedDict, Optional, Dict, List, Union, Annotated, Sequence
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import ToolMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode 
from langchain.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

from langchain_google_genai import ChatGoogleGenerativeAI

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

#conditional_graph()

def Looping_graph():    #Route flow back to nodes when needed
    class loopingagent(TypedDict):
        PlayerName: str
        guesses: List[int]
        current_guess:int
        attempts: int
        lower_bound:int
        upper_bound:int
        selected_num:int

    def setup(state: loopingagent)->loopingagent:
        """setup for guessing game"""
        state['selected_num'] = random.randint(state['lower_bound'], state['upper_bound'])
        state['attempts'] = 0
        return state

    def guess_node(state:loopingagent)->loopingagent:   #Guesses number and appends
        """guess looping node for game"""
        guess = random.randint(state['lower_bound'], state['upper_bound'])
        state['current_guess'] = guess
        state["guesses"].append(guess)
        state['attempts'] +=1

        return state

    def hint_node(state:loopingagent)->loopingagent:    #Adjusts bound from current hint
        """gives hint for each iteration and guess"""
        if state['selected_num'] > state['current_guess']:
            print("Higher")
            state['lower_bound'] = state['current_guess']
        else:
            print("Lower")
            state['upper_bound'] = state['current_guess']

        return state

    def should_continue(state: loopingagent)->loopingagent: #Checks the answer
        if state['attempts'] < 7:
            print("looping", state['attempts'])
            if state['selected_num'] == state['current_guess']:
                return "exit"
            else:
                return "loop"   #Loops back through/loop edge
        else:
                return "exit"   #exit loop/exit edge   


    graphloop = StateGraph(loopingagent)

    graphloop.add_node("setup", setup)
    graphloop.add_node("guess", guess_node)
    graphloop.add_node("hint", hint_node)

    graphloop.add_edge(START, "setup")
    graphloop.add_edge("setup", "guess")
    graphloop.add_edge("guess", "hint")

    graphloop.add_conditional_edges(     #Uses conditional edge to loop
        "hint",       #Source node
        should_continue,    #Action
        {
            "loop": "guess",   #Loop
            "exit": END     #End
        }
    )

    graphloop.set_entry_point("setup")

    apploop = graphloop.compile()

    loopres = apploop.invoke({"Name": "Tony", "guesses" : [], "lower_bound": 1, "upper_bound": 20})
    print(loopres)

#Looping_graph()

#SIMPLE BOT - AI PORTION
load_dotenv()
def First_AI_agent():   #SIMPLE CHATBOT
    class firstagent(TypedDict):
        messages : List[HumanMessage]   #Tells model human message
    
    MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0)

    def process_node(state:firstagent)->firstagent:
        response = llm.invoke(state['messages'])
        print(f"\nAI : {response.content}")
        return state

    faigraph = StateGraph(firstagent)
    faigraph.add_node("process", process_node)
    faigraph.add_edge(START, "process")
    faigraph.add_edge("process", END)
    agent = faigraph.compile()

    user_in = input("Enter: ")
    while user_in != "exit":
        agent.invoke({"messages": [HumanMessage(content=user_in)]})
        user_input = input("Enter: ")

#First_AI_agent()

def Memory_AI_agent():  #Chatbot but with some memory
    class Magentstate(TypedDict):
        messages: List[Union[HumanMessage, AIMessage]]  #Lets you input/store either message using union

    MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0)

    def process(state: Magentstate)->Magentstate:
        """This node will solve the request you input"""
        response = llm.invoke(state['messages'])

        state['messages'].append(AIMessage(content=response.content))#Stores the data taken in in state

        return state
    
    aigraph = StateGraph(Magentstate)
    aigraph.add_node("process", process)
    aigraph.add_edge(START, "process")
    aigraph.add_edge("process", END)
    agent = aigraph.compile()  

    #User input
    convohistory = []
    user_in = input("Enter: ")
    while user_in != "exit":
        convohistory.append(HumanMessage(content=user_in))

        result = agent.invoke({"messages": convohistory})
        convohistory = result['messages']
        print("\nAI:", convohistory[-1].text)

        user_in = input("Enter: ")
    #Stores the convo (not the best way)
    with open("logging.txt", "w") as file:
        file.write("Your convo log: \n")

        for message in convohistory:
            if isinstance(message, HumanMessage):
                file.write(f"you: {message.content}\n")
            elif isinstance(message, AIMessage):
                file.write(f"AI: {message.content}\n\n")
        file.write("End of conversation")
    print("Conversation saved to logging.txt")

#Memory_AI_agent()

#TOOL AGENT

#Sequence - To automatically handle the state updates for sequences such as adding new messages to a chat history
#ToolMessage- Data is passed back to llm 
#BaseMessage - foundational class for all messages in LanGraph
#add_message - Tells us how to merge new data into current state/prevents overwriting(reducer function)

def ReAct_agent():  #Loop integration with LLM IMPORTANT
    class Ragent(TypedDict):
        pass

