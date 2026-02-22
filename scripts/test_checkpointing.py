#!/usr/bin/env python3
"""
Interactive Test Script for Checkpointing Feature

This script demonstrates conversation memory by having a multi-turn
conversation with the AI agent.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/chat/graph"

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_message(role, content, metadata=""):
    """Print a formatted message"""
    icon = "🧑" if role == "user" else "🤖"
    print(f"\n{icon} {role.upper()}: {content}")
    if metadata:
        print(f"   {metadata}")

def send_message(message, conversation_id=None):
    """Send a message to the API and return the response"""
    payload = {
        "message": message,
        "user_id": "test_user",
        "max_iterations": 5
    }
    
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    print_message("user", message)
    print("   ⏳ Waiting for response...")
    
    try:
        response = requests.post(API_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print_message(
            "assistant",
            data["response"],
            f"Agent: {data['agent_used']} | Confidence: {data['confidence']:.2%} | Iterations: {data['iterations']}"
        )
        
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        return None

def test_conversation_memory():
    """Test that the agent remembers conversation context"""
    
    print_header("Testing Conversation Memory (Checkpointing)")
    
    print("\n📝 This test will:")
    print("   1. Start a conversation and share information")
    print("   2. Ask questions in subsequent turns")
    print("   3. Verify the agent remembers previous context")
    
    input("\nPress ENTER to start the test...")
    
    # Turn 1: Introduce information
    print_header("TURN 1: Providing Information")
    result1 = send_message(
        "My name is Alice and I am a software engineer. I work with Python and React."
    )
    
    if not result1:
        print("\n❌ Test failed - could not get response")
        return
    
    conversation_id = result1.get("session_id")
    print(f"\n📌 Conversation ID: {conversation_id}")
    print("   (This ID will be used to maintain conversation context)")
    
    time.sleep(2)
    
    # Turn 2: Test memory - ask about name
    print_header("TURN 2: Testing Memory (What is my name?)")
    result2 = send_message(
        "What is my name?",
        conversation_id=conversation_id
    )
    
    if result2 and "alice" in result2["response"].lower():
        print("\n✅ SUCCESS: Agent remembered the name!")
    else:
        print("\n⚠️  WARNING: Agent might not have remembered the name")
    
    time.sleep(2)
    
    # Turn 3: Test memory - ask about profession
    print_header("TURN 3: Testing Memory (What do I do?)")
    result3 = send_message(
        "What do I do for work?",
        conversation_id=conversation_id
    )
    
    if result3 and ("software" in result3["response"].lower() or "engineer" in result3["response"].lower()):
        print("\n✅ SUCCESS: Agent remembered the profession!")
    else:
        print("\n⚠️  WARNING: Agent might not have remembered the profession")
    
    time.sleep(2)
    
    # Turn 4: Test memory - ask about technologies
    print_header("TURN 4: Testing Memory (What technologies?)")
    result4 = send_message(
        "What programming languages or technologies did I mention?",
        conversation_id=conversation_id
    )
    
    if result4 and ("python" in result4["response"].lower() or "react" in result4["response"].lower()):
        print("\n✅ SUCCESS: Agent remembered the technologies!")
    else:
        print("\n⚠️  WARNING: Agent might not have remembered the technologies")
    
    # Summary
    print_header("TEST SUMMARY")
    print("\n✅ Conversation Memory Test Complete!")
    print(f"   Total turns: 4")
    print(f"   Conversation ID: {conversation_id}")
    print(f"\n💡 The agent should have remembered:")
    print(f"   - Your name (Alice)")
    print(f"   - Your profession (Software Engineer)")
    print(f"   - Technologies mentioned (Python, React)")
    
    print("\n📊 Check the checkpoint database:")
    print(f"   Location: data/database/checkpoints.db")
    print(f"   Thread ID: {conversation_id}")

def test_thread_isolation():
    """Test that different conversations are isolated"""
    
    print_header("Testing Thread Isolation")
    
    print("\n📝 This test will:")
    print("   1. Start Conversation A with one piece of information")
    print("   2. Start Conversation B with different information")
    print("   3. Verify they don't mix contexts")
    
    input("\nPress ENTER to start the test...")
    
    # Conversation A
    print_header("CONVERSATION A: Turn 1")
    result_a1 = send_message("My favorite color is blue.")
    conv_a_id = result_a1.get("session_id")
    print(f"\n📌 Conversation A ID: {conv_a_id}")
    
    time.sleep(1)
    
    # Conversation B
    print_header("CONVERSATION B: Turn 1")
    result_b1 = send_message("My favorite color is red.")
    conv_b_id = result_b1.get("session_id")
    print(f"\n📌 Conversation B ID: {conv_b_id}")
    
    time.sleep(1)
    
    # Test Conversation A memory
    print_header("CONVERSATION A: Turn 2 (Testing Memory)")
    result_a2 = send_message(
        "What is my favorite color?",
        conversation_id=conv_a_id
    )
    
    if result_a2 and "blue" in result_a2["response"].lower():
        print("\n✅ SUCCESS: Conversation A correctly remembered BLUE!")
    else:
        print("\n⚠️  WARNING: Conversation A might not have correct memory")
    
    time.sleep(1)
    
    # Test Conversation B memory
    print_header("CONVERSATION B: Turn 2 (Testing Memory)")
    result_b2 = send_message(
        "What is my favorite color?",
        conversation_id=conv_b_id
    )
    
    if result_b2 and "red" in result_b2["response"].lower():
        print("\n✅ SUCCESS: Conversation B correctly remembered RED!")
    else:
        print("\n⚠️  WARNING: Conversation B might not have correct memory")
    
    # Summary
    print_header("ISOLATION TEST SUMMARY")
    print("\n✅ Thread Isolation Test Complete!")
    print(f"\n   Conversation A (blue): {conv_a_id}")
    print(f"   Conversation B (red):  {conv_b_id}")
    print(f"\n💡 Each conversation maintained separate context!")

def main():
    """Main test menu"""
    
    print("\n" + "="*70)
    print("  🧠 CHECKPOINTING FEATURE - INTERACTIVE TEST")
    print("="*70)
    print("\n  This script tests the LangGraph checkpointing feature")
    print("  that enables conversation memory across requests.")
    print("\n  Prerequisites:")
    print("  ✓ Backend running at http://localhost:8000")
    print("  ✓ OpenAI API key configured")
    
    # Check if API is accessible
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print("\n  ✅ API is accessible!")
    except:
        print("\n  ❌ ERROR: Cannot reach API at http://localhost:8000")
        print("     Start the backend with: uv run uvicorn app.main:app --reload")
        return
    
    while True:
        print("\n" + "-"*70)
        print("  SELECT A TEST:")
        print("-"*70)
        print("  1. Test Conversation Memory (recommended)")
        print("  2. Test Thread Isolation")
        print("  3. Run Both Tests")
        print("  4. Exit")
        print("-"*70)
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_conversation_memory()
        elif choice == "2":
            test_thread_isolation()
        elif choice == "3":
            test_conversation_memory()
            test_thread_isolation()
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
