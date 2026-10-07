import os, re, sqlite3
import pandas as pd
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0)
from langchain_google_genai import ChatGoogleGenerativeAI


class AnswerOutputParser(BaseOutputParser[list[str]]): #Parses output by answer = of llm call
    def parse(self, text:str):
        return text.strip().split("answer =")

class CommaSepOutputParser(BaseOutputParser[list[str]]): #Parses output by comma of llm call
    def parse(self, text: str):
        return text.strip().split(", ")

def testing():
    template = "You are a helpful assistant that takes a math problem and shows your work. Output each step then return the answer in the format answer = <answer here>." \
    " Make sure to output answer in all lowercase and have exactly one space and equal sign that follows"
    human_temp = "{problem}"

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_temp)
    ])

    messages = chat_prompt.format_messages(problem = "2x^2 - 5x + 3 = 0")

    result = llm.invoke(messages)
    parsed = AnswerOutputParser().parse(result.content)
    steps, answer = parsed

    print(steps, answer)


def chainingtest():
    template = "You are a helpful assistant who generates comma seperated lists. A user passes in a category and you return 5 words" \
    "seperated by a comma and nothing more."
    human_temp = "{text}"
    
    chat_prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", human_temp),
    ])
    
    chain = chat_prompt | llm | CommaSepOutputParser()
    result = chain.invoke({"text": "video games"})
    print(result)






#testing()
chainingtest()