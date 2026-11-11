import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Olivia AI Assistant", version="1.0.0")

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def root():
    has_key = bool(os.environ.get("OPENAI_API_KEY"))
    return {
        "status": "online",
        "agent": "Olivia",
        "brain": "GPT-4o-mini",
        "api_key_configured": has_key
    }

@app.post("/olivia/process")
async def process_command(payload: CommandRequest):
    user_command = payload.command
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="OPENAI_API_KEY is missing in Render Environment Variables."
        )
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are Olivia, an autonomous AI assistant operating a user's laptop. Analyze the user's request and return ONLY a JSON object with 'action_type' (must be one of: OPEN_APP, FILE_SEARCH, VS_CODE_ACTION, TERMINAL_EXEC) and 'parameters' (an object containing keys like 'file_name', 'app_name', 'command', or 'query')."
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
