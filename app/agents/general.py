"""
General Agent - Fallback agent for miscellaneous queries.
"""

from app.orchestration.state import AgentState, Message
from app.config.llm import get_llm
from app.prompts.templates import GENERAL_AGENT_PROMPT
from datetime import datetime


def general_agent(state: AgentState) -> AgentState:
    """
    General-purpose agent that handles miscellaneous queries.
    
    Acts as a fallback when other agents are not appropriate.
    
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
    user_query = latest_message.content  # Access as attribute, not dict
    
    # Get LLM instance
    llm = get_llm(temperature=0.7)  # Slightly creative for general queries
    
    # Prepare messages for LLM
    llm_messages = [
        {"role": "system", "content": GENERAL_AGENT_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    # Get response from LLM
    response = llm.invoke(llm_messages)
    
    # Extract content (handle different response types)
    if hasattr(response, 'content'):
        response_content = response.content
    else:
        response_content = str(response)
    
    # Create response message
    assistant_message = Message(
        role="assistant",
        content=response_content,
        agent="general",
        timestamp=datetime.now().isoformat()
    )
    
    # Update state (helper function will handle the add reducer)
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [assistant_message]
    new_state["current_agent"] = "general"
    
    return new_state
