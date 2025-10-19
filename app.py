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

# Khởi tạo Plan Agent với API enabled (mặc định là True)
# Để tắt API, sử dụng: agent=PlanAgent(llm=llm,verbose=True,api_enabled=False)
agent=PlanAgent(llm=llm,verbose=True,api_enabled=True)

print("Plan Agent đã sẵn sàng! API integration đã được kích hoạt.")
print("Thông tin sẽ được gửi lên http://localhost:8000")
print("-" * 50)

user_input=input("Enter a query: ")
agent_response=agent.invoke(user_input)
print("\n" + "="*50)
print("Final Response:")
print(agent_response)