import os 
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

model = "llama-3.3-70b-versatile"
client = Groq(api_key = my_api_key)

role = "user"
prompt = "Suggest a name for my cloth company and a tagline for it."

#SYSTEM PROMPT

message_system = {
    "role": "system",
    "content": "You are a brand manager who suggest for my company."
}
messages = [message_system,{
    "role": role,
    "content": prompt       
}]

#Temaperature by default is 0 and range is [0,2]

response = client.chat.completions.create(model=model, messages=messages, temperature=2)

print(response.choices[0].message.content)