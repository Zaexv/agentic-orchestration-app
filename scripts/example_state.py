"""Example: How to use State Management

This example demonstrates the state management system for the digital twin.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.orchestration.state import (
    create_initial_state,
    add_message,
    update_routing,
    increment_iteration,
    RetrievedDocument
)


def example_conversation_flow():
    """Example of a complete conversation flow through the state"""
    
    print("=" * 60)
    print("Digital Twin State Management Example")
    print("=" * 60)
    
    # 1. Create initial state
    print("\n1️⃣ Creating initial state...")
    state = create_initial_state(
        user_query="What programming languages do I know?",
        user_id="eduardo",
        max_iterations=10
    )
    print(f"   Session ID: {state['session_id']}")
    print(f"   Current Agent: {state['current_agent']}")
    print(f"   Messages: {len(state['messages'])}")
    
    # 2. Router makes a decision
    print("\n2️⃣ Router deciding which agent to use...")
    state = update_routing(
        state,
        target_agent="professional",
        confidence=0.92,
        reasoning="Query is about technical skills (programming languages)"
    )
    print(f"   Target Agent: {state['next_agent']}")
    print(f"   Confidence: {state['routing_confidence']}")
    print(f"   Reasoning: {state['routing_history'][-1].reasoning}")
    
    # 3. Switch to professional agent
    print("\n3️⃣ Professional agent executing...")
    state["current_agent"] = "professional"
    state = increment_iteration(state)
    
    # 4. Professional agent retrieves documents
    print("\n4️⃣ Retrieving relevant documents...")
    state["retrieved_docs"] = [
        RetrievedDocument(
            content="Python, TypeScript, Go - 5 years experience",
            source="resume.pdf",
            score=0.95,
            agent_domain="professional"
        ),
        RetrievedDocument(
            content="Contributed to open source Python projects",
            source="github_profile.txt",
            score=0.87,
            agent_domain="professional"
        )
    ]
    print(f"   Retrieved: {len(state['retrieved_docs'])} documents")
    for doc in state['retrieved_docs']:
        print(f"     - {doc.source} (score: {doc.score})")
    
    # 5. Professional agent generates response
    print("\n5️⃣ Generating response...")
    response = "I know Python, TypeScript, and Go with 5 years of experience. I've also contributed to open source Python projects."
    state = add_message(state, role="assistant", content=response, agent="professional")
    state["final_response"] = response
    state["should_continue"] = False
    
    print(f"   Response: {response}")
    
    # 6. Show final state summary
    print("\n6️⃣ Final State Summary:")
    print(f"   Total Messages: {len(state['messages'])}")
    print(f"   Total Iterations: {state['iterations']}")
    print(f"   Routing History: {len(state['routing_history'])} decisions")
    print(f"   Session Duration: {(state['updated_at'] - state['started_at']).total_seconds():.3f}s")
    
    # 7. Show message history
    print("\n7️⃣ Message History:")
    for i, msg in enumerate(state['messages'], 1):
        agent_info = f" ({msg.agent})" if msg.agent else ""
        print(f"   {i}. [{msg.role}{agent_info}]: {msg.content[:60]}...")
    
    print("\n" + "=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)
    
    return state


def example_max_iterations():
    """Example showing max iterations safety mechanism"""
    
    print("\n" + "=" * 60)
    print("Max Iterations Safety Example")
    print("=" * 60)
    
    state = create_initial_state("Test query", max_iterations=3)
    
    print(f"\nMax iterations set to: {state['max_iterations']}")
    
    for i in range(5):  # Try to exceed limit
        if not state["should_continue"]:
            print(f"\n❌ Iteration {i+1}: Stopped - {state['error']}")
            break
        
        state = increment_iteration(state)
        print(f"✅ Iteration {i+1}: OK (should_continue={state['should_continue']})")
    
    print("=" * 60)


if __name__ == "__main__":
    # Run examples
    state = example_conversation_flow()
    example_max_iterations()
    
    print("\n💡 Key Features:")
    print("   - Messages accumulate (add operator)")
    print("   - Routing history tracks decisions")
    print("   - Iteration counter prevents infinite loops")
    print("   - Timestamps track state evolution")
    print("   - Type-safe with Pydantic models")
