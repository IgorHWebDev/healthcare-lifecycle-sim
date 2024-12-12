import os
import requests
from dotenv import load_dotenv
import base64
import time

# Load environment variables
load_dotenv()

def test_pod_connection():
    """Test basic pod connectivity"""
    try:
        # New endpoint configuration
        base_url = "https://wvg8vbode7y8kh-19123-5hw3es9xxi3bmciuxlo2.proxy.runpod.net"
        username = "5hw3es9xxi3bmciuxlo2"
        password = "5s7a7vuikkg3flmltti1"
        
        print(f"\nTesting pod URL: {base_url}")
        
        # Create session with authentication
        session = requests.Session()
        session.auth = (username, password)
        
        # Test different endpoints
        endpoints = [
            "/v1/chat/completions",  # OpenAI-compatible chat endpoint
            "/api/v1/generate",      # text-generation-webui endpoint
            "/v1/completions"        # OpenAI-compatible completions endpoint
        ]
        
        for endpoint in endpoints:
            api_url = f"{base_url}{endpoint}"
            print(f"\nTesting endpoint: {endpoint}")
            
            # Adjust payload based on endpoint
            if "chat" in endpoint:
                payload = {
                    "messages": [
                        {"role": "user", "content": "Hello, this is a test message."}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7
                }
            else:
                payload = {
                    "prompt": "Hello, this is a test message.",
                    "max_new_tokens": 50,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9
                }
            
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    print(f"Attempt {attempt + 1} of {max_retries}...")
                    completion_response = session.post(api_url, json=payload, timeout=30)
                    print(f"Status: {completion_response.status_code}")
                    print(f"Response: {completion_response.text[:500]}")  # Limit response text
                    
                    if completion_response.status_code == 200:
                        print("Endpoint is working!")
                        break
                    else:
                        print(f"Endpoint test failed")
                        if attempt < max_retries - 1:
                            print("Waiting 5 seconds before retry...")
                            time.sleep(5)
                except requests.exceptions.RequestException as e:
                    print(f"Connection error: {e}")
                    if attempt < max_retries - 1:
                        print("Waiting 5 seconds before retry...")
                        time.sleep(5)
            
            print("\n" + "="*50 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing pod connection...")
    test_pod_connection() 