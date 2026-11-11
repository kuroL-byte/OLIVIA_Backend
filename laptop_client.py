import time
import requests

# Replace with your actual Render URL
CLOUD_BACKEND_URL = "https://your-app-name.onrender.com/olivia/process"

def listen_for_commands():
    print("🚀 Olivia Laptop Client is online and listening for commands...")
    
    while True:
        try:
            # For testing, we can simulate sending/checking status
            # In future steps, this will poll or use WebSockets for real-time execution
            time.sleep(10)
        except KeyboardInterrupt:
            print("\nShutting down Olivia client.")
            break
        except Exception as e:
            print(f"Connection retry error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    listen_for_commands()
    