import sys
import os
import json
import subprocess
import requests

# Your live Render backend endpoint
CLOUD_BACKEND_URL = "https://olivia-backend-1fvt.onrender.com/olivia/process"

def execute_local_action(structured_action_raw):
    """Parses the LLM JSON output and executes the corresponding OS action locally."""
    try:
        # Handle whether the backend returned a JSON string or an already-parsed dict
        if isinstance(structured_action_raw, str):
            action_data = json.loads(structured_action_raw)
        elif isinstance(structured_action_raw, dict):
            action_data = structured_action_raw
        else:
            print(f"[Executor] Unexpected action format: {structured_action_raw}")
            return

        action_type = action_data.get("action_type", "").upper()
        params = action_data.get("parameters", {})

        print(f"\n⚡ [Executing Local Action] Type: {action_type} | Params: {params}")

        if action_type in ["VS_CODE_ACTION", "OPEN_APP"]:
            file_name = params.get("file_name") or params.get("filename") or params.get("file")
            app_name = (params.get("app_name") or params.get("application") or "").lower()

            if file_name:
                # Create the file if it doesn't exist yet
                if not os.path.exists(file_name):
                    with open(file_name, "w", encoding="utf-8") as f:
                        f.write("# Created by Olivia AI\n")
                    print(f"✅ Created new file: {file_name}")
                # Open the file in VS Code
                subprocess.run(f'code "{file_name}"', shell=True)
                print(f"✅ Opened {file_name} in VS Code.")
            elif "code" in app_name or "vs code" in app_name:
                subprocess.run("code .", shell=True)
                print("✅ Opened VS Code.")
            elif app_name:
                subprocess.run(f"start {app_name}", shell=True)
                print(f"✅ Launched application: {app_name}")

        elif action_type == "TERMINAL_EXEC":
            cmd = params.get("command") or params.get("cmd")
            if cmd:
                confirm = input(f"⚠️ Allow Olivia to run terminal command '{cmd}'? (y/n): ")
                if confirm.lower() == 'y':
                    subprocess.run(cmd, shell=True)

        elif action_type == "FILE_SEARCH":
            query = params.get("query") or params.get("filename") or ""
            print(f"🔍 Searching current directory for '{query}'...")
            for root, dirs, files in os.walk("."):
                if "venv" in root or ".git" in root:
                    continue
                for file in files:
                    if query.lower() in file.lower():
                        print(f"Found: {os.path.join(root, file)}")

        else:
            print(f"ℹ️ Action type '{action_type}' received, no local handler mapped yet.")

    except Exception as e:
        print(f"[Execution Error] Failed to run local action: {e}")

def send_command_to_olivia(command_text: str):
    print(f"\n[Sending to Cloud] '{command_text}'...")
    
    payload = {
        "command": command_text
    }
    
    try:
        response = requests.post(CLOUD_BACKEND_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("\n[Cloud Brain Response Success]")
            print(json.dumps(data, indent=2))
            
            structured_action = data.get("structured_action")
            if structured_action:
                execute_local_action(structured_action)
            else:
                print("\n⚠️ Note: 'structured_action' was empty. Make sure your updated main.py is pushed and deployed on Render.")
        else:
            print(f"\n[Error] Server returned status code {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"\n[Connection Error] Could not reach the cloud backend: {e}")

if __name__ == "__main__":
    print("🚀 Olivia Laptop Client Initialized.")
    
    if len(sys.argv) > 1:
        user_cmd = " ".join(sys.argv[1:])
        send_command_to_olivia(user_cmd)
    else:
        while True:
            try:
                user_cmd = input("\nEnter command for Olivia (or type 'exit' to quit): ")
                if user_cmd.lower() == 'exit':
                    break
                if user_cmd.strip():
                    send_command_to_olivia(user_cmd)
            except KeyboardInterrupt:
                print("\nShutting down client.")
                break