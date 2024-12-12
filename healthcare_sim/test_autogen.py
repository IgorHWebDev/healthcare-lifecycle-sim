import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load the root .env file
root_env_path = Path(__file__).parent.parent / '.env'
load_dotenv(root_env_path)

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def test_basic_agent():
    """Test basic agent functionality with RunPod."""
    print("Testing AutoGen with RunPod integration...")
    
    # Get RunPod configuration from environment
    pod_id = os.getenv('RUNPOD_POD_ID')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not pod_id or not api_key:
        raise ValueError("Missing required environment variables. Check your .env file.")
    
    # Configure the client
    model_client = OpenAIChatCompletionClient(
        model="cognitivecomputations_dolphin-2.7-mixtral-8x7b",
        api_type="open_ai",
        api_base=f"https://{pod_id}-50001.proxy.runpod.net/v1",
        api_key=api_key
    )
    
    print(f"Connecting to RunPod instance: {pod_id}")
    
    # Create a test agent
    agent = AssistantAgent(
        name="test_agent",
        model_client=model_client,
        system_message="You are a helpful AI assistant. Be concise and clear in your responses."
    )
    
    # Define termination condition
    termination = TextMentionTermination("TERMINATE")
    
    # Create team
    agent_team = RoundRobinGroupChat([agent], termination_condition=termination)
    
    # Test tasks
    tasks = [
        "Write a simple Python function to calculate the factorial of a number. TERMINATE when done.",
        "Explain what is machine learning in one sentence. TERMINATE when done.",
        "Generate a haiku about artificial intelligence. TERMINATE when done."
    ]
    
    for task in tasks:
        print(f"\nExecuting task: {task}")
        try:
            stream = agent_team.run_stream(task=task)
            await Console(stream)
        except Exception as e:
            print(f"Error during task execution: {str(e)}")
            raise

async def main():
    try:
        await test_basic_agent()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 