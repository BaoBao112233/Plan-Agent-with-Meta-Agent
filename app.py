from src.agent.meta import MetaAgent
from src.agent.plan import PlanAgent
from src.inference.vertex_ai import ChatVertexAI
from os import environ
from dotenv import load_dotenv
from experimental import *

load_dotenv()

# Use Vertex AI with Gemini 2.5 Flash
project_id = environ.get("GOOGLE_CLOUD_PROJECT")
service_account_path = environ.get("GOOGLE_APPLICATION_CREDENTIALS", "./service-account.json")
vertex_ai_model = environ.get("VERTEX_AI_MODEL", "gemini-2.5-flash")
vertex_ai_location = environ.get("VERTEX_AI_LOCATION", "us-central1")

if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set. Please add it to your .env file.")

llm = ChatVertexAI(
    model=vertex_ai_model,
    project_id=project_id,
    location=vertex_ai_location,
    temperature=0,
    service_account_path=service_account_path
)

# agent=MetaAgent(llm=llm,tools=[web_search_tool,file_writer_tool],verbose=True)
agent = PlanAgent(llm=llm, verbose=True)
input_text = input("Enter a query: ")
agent_response = agent.invoke(input_text)
print(agent_response)