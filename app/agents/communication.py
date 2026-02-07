"""
Communication Agent - Writing style, tone, and communication patterns.
"""

from app.orchestration.state import AgentState, Message
from app.config.llm import get_llm
from app.prompts.templates import COMMUNICATION_AGENT_PROMPT
from datetime import datetime


def communication_agent(state: AgentState) -> AgentState:
    """
    Communication agent that handles writing and communication queries.
    
    Specializes in:
    - Drafting messages and emails
    - Writing style and tone
    - Communication effectiveness
    - Content review and improvement
    
    Args:
        state: Current agent state with message history
        
    Returns:
        Updated state with agent response
    """
    # Get the latest user message
    messages = state["messages"]
    if not messages:
        return state
    
    latest_message = messages[-1]
    user_query = latest_message.content
    
    # Get LLM instance (balanced temperature for creativity with structure)
    llm = get_llm(temperature=0.5)
    
    # Prepare messages for LLM
    llm_messages = [
        {"role": "system", "content": COMMUNICATION_AGENT_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    # Get response from LLM
    response = llm.invoke(llm_messages)
    
    # Extract content
    if hasattr(response, 'content'):
        response_content = response.content
    else:
        response_content = str(response)
    
    # Create response message
    assistant_message = Message(
        role="assistant",
        content=response_content,
        agent="communication",
        timestamp=datetime.now().isoformat()
    )
    
    # Update state
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [assistant_message]
    new_state["current_agent"] = "communication"
    
    return new_state
