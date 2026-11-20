import os 
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

model = "openai/gpt-oss-120b"
client = Groq(api_key = my_api_key)


#structured data extraction
from pydantic import BaseModel
class Ticket(BaseModel):
    name: str
    email: str
    phone: str
    issue: str

schema = Ticket.model_json_schema()

response_format ={
    "type": "json_object",
}

system_prompt = f"""
You are a helpful assistant. You will be given a customer ticket. Please extract the personal information from the ticket and return it in this schema format: {schema} and give me a json output
"""

message_system = {
    "role": "system",
    "content": system_prompt
}

text = "Hello my name iss dev . I have purchased a new car and it has some faults. MY email is abc@example.com. Please contact me at 123-456-7890 for further details."

prompt = f"""
This is a customer ticket. please extract the personal information from this{text}
"""

message = {
    "role": "user",
    "content": prompt       
}

messages = [message_system, message]

response = client.chat.completions.create(model=model, messages=messages, response_format=response_format)

answer = response.choices[0].message.content
print(answer)

#isko padhna kaise h 
import json
raw_json = answer
data_file = json.loads(raw_json)
ticket = Ticket(**data_file)

print(ticket.name)
print(ticket.email)
print(ticket.phone)
print(ticket.issue)