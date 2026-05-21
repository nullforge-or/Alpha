import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import AVAILABLE_TOOLS
import memory

# Load environment variables
load_dotenv()

# Google Gemini via OpenAI SDK compatibility layer
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)

TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "browse_website",
            "description": "Navigate to a URL and extract its text content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full HTTP/HTTPS URL"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for a query to find information or URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query (e.g., 'latest technology news')"}
                },
                "required": ["query"]
            }
        }
    }
]

def run_agent(user_prompt: str):
    print(f"\n[User]: {user_prompt}")
    
    # 1. Initialize temporary memory for THIS specific processing loop
    messages = [
        {"role": "system", "content": "You are Alpha, a powerful, autonomous agent. Use your tools to fulfill the user's request efficiently."}
    ]
    
    # 2. Load permanent history (Text only. We filter out any past tool crashes)
    past_memory = memory.get_recent_memory(limit=10)
    for msg in past_memory:
        if msg["role"] in ["user", "assistant"] and msg["content"]:
            messages.append(msg)
            
    # 3. Add current prompt to active memory and save to permanent DB
    messages.append({"role": "user", "content": user_prompt})
    memory.save_message("user", user_prompt)
    
    while True:
        print("[System] Alpha is computing...")
        
        response = client.chat.completions.create(
            model="gemini-1.5-flash-latest", # Auto-routes to the most stable flash endpoint
            messages=messages,
            tools=TOOL_SCHEMA
        )
        
        message = response.choices[0].message
        
        # Append the raw object to the active loop so Gemini keeps its hidden signatures
        messages.append(message)
        
        # If the AI decides to use a tool
        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if func_name in AVAILABLE_TOOLS:
                    result = AVAILABLE_TOOLS[func_name](**args)
                    
                    # Google STRICTLY requires 'role', 'tool_call_id', and 'name'
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name, 
                        "content": str(result)
                    }
                    messages.append(tool_msg)
        else:
            # The AI is finished. Save ONLY the final text answer to permanent memory.
            print(f"\n[Agent]: {message.content}")
            if message.content:
                memory.save_message("assistant", message.content)
            return message.content

if __name__ == "__main__":
    run_agent("System check.")