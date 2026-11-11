import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Olivia AI Assistant", version="1.0.0")

# Initialize OpenAI client (it will look for OPENAI_API_KEY environment variable)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def root():
    return {"status": "online", "agent": "Olivia", "brain": "GPT-4o-mini"}

@app.post("/olivia/process")
async def process_command(payload: CommandRequest):
    user_command = payload.command
    
    if not client.api_key:
        raise HTTPException(status_code=500, status_code_detail="OpenAI API key not configured on backend.")
    
    try:
        # Ask the LLM to interpret the user's command and map it to an action type
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are Olivia, an autonomous AI assistant operating a user's laptop. Analyze the user's request and categorize it into a JSON structure with action_type (e.g., OPEN_APP, FILE_SEARCH, VS_CODE_ACTION, TERMINAL_EXEC) and parameters."
                },
                {"role": "user", "content": user_command}
            ],
            response_format={"type": "json_object"}
        )
        
        llm_output = response.choices[0].message.content
        
        return {
            "status": "success",
            "original_command": user_command,
            "structured_action": llm_output
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))