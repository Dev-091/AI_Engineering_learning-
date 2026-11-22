import os
import re
from dotenv import load_dotenv
from groq import Groq
from time import sleep

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-20b"

# tools
def get_product_price(product):
    if product == "iphone 17":
        return 1000
    elif product == "iphone 15":
        return 800
    else:
        return 0


def calculator(expression):
    try:
        return eval(expression)
    except Exception:
        return "calculation error"


tools = {
    "get_product_price": get_product_price,
    "calculator": calculator
}

system_prompt = """
you are shopping assistant.

you have this tools:
get_product_price(product) : returns the price of the product
calculator(expression) : evaluates the mathematical expression and returns the result
Important:
Call tools exactly like these examples:
Action: get_product_price("iphone 17")
Action: calculator("5000 - 1000")

Never write:
get_product_price(product = 'iphone 17')
calculator(expression = '5000 - 1000')

Follow these rules:
1. Decide what you need to do next.
2. Call only one tool at a time.
3. After writing an action, STOP immediately.
4. Never guess or invent a tool result.
5. Wait until you receive an observation.
6. Then decide your next action.
7. When the task is complete, give the final answer.

Format:
Thought: what you need to do
Action: tool_name(argument)

when finished:
Final Answer: your answer
"""


def run_agent(question):
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for step in range(5):
        print("\n--------------------------------\n")
        print("STEP", step + 1)
        print("\n--------------------------------\n")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )

        answer = response.choices[0].message.content
        print(answer)

        if "Final Answer:" in answer:
            break

        match = re.search(r"Action:\s+(\w+)\((.*)\)", answer)

        if match:
            tool_name = match.group(1)
            tool_input = match.group(2).strip().strip('"').strip("'")

            if tool_name in tools:
                observation = tools[tool_name](tool_input)
            else:
                observation = "Tool not found"
        else:
            observation = "Action not found"

        print("Observation:", observation)

        messages.append({
            "role": "assistant",
            "content": answer
        })

        messages.append({
            "role": "user",
            "content": f"Observation: {observation}"
        })
        sleep(5)


prompt = """I have 5000 rupees. What is the price of an iphone 17?
And how much money will I have left after buying it?
"""
run_agent(prompt)


