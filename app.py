from src.agent.meta import MetaAgent
from src.agent.plan import PlanAgent
from src.inference.groq import ChatGroq
from os import environ
from dotenv import load_dotenv
from experimental import *

load_dotenv()

api_key = environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")

llm=ChatGroq('llama-3.3-70b-versatile',api_key,temperature=0)
# agent=MetaAgent(llm=llm,tools=[web_search_tool,file_writer_tool],verbose=True)
agent=PlanAgent(llm=llm,verbose=True)
input=input("Enter a query: ")
agent_response=agent.invoke(input)
print(agent_response)