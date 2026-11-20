import os 
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

model = "openai/gpt-oss-120b"
client = Groq(api_key = my_api_key)

role = "user"
#prompt 
prompt1="You are a helpful assistant."
prompt2="Write a 1000 word essay on Machine Learning."
prompt3="Explain time travel in  detailed manner under 100 words."

prompts= [prompt1, prompt2, prompt3]
for prompt in prompts:
    messages = [{
        "role": role,
        "content": prompt       
    }]

    response = client.chat.completions.create(model=model, messages=messages, max_tokens=500)
    usage = response.usage
    print(f"Prompt: {prompt} --> your tokens: {usage.prompt_tokens} completion_tokens:{usage.completion_tokens},total_tokens: {usage.total_tokens} Finish Reason:{response.choices[0].finish_reason}")
    
# prompt = "Write a short poem about the beauty of nature." 

# messages = [{
#     "role": role,
#     "content": prompt       
# }]

# response = client.chat.completions.create(model=model, messages=messages)

# print(response.choices[0].message.content)