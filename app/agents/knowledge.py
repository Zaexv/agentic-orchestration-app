"""
Knowledge Agent - Personal knowledge base, facts, and memories.
"""

from app.orchestration.state import AgentState, Message
from app.config.llm import get_llm
from app.prompts.templates import KNOWLEDGE_AGENT_PROMPT
from datetime import datetime


def knowledge_agent(state: AgentState) -> AgentState:
    """
    Knowledge agent that handles personal knowledge and memory queries.
    
    Specializes in:
    - Personal facts and information
    - Preferences and interests
    - Experiences and memories
    - Background and history
    
    Note: Will be enhanced with RAG in Phase 8 for personalized knowledge retrieval.
    
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
    
    # Get LLM instance
    llm = get_llm(temperature=0.4)
    
    # Prepare messages for LLM
    # Note: In Phase 8, we'll add RAG retrieval here to fetch relevant personal knowledge
    llm_messages = [
        {"role": "system", "content": KNOWLEDGE_AGENT_PROMPT},
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
        agent="knowledge",
        timestamp=datetime.now().isoformat()
    )
    
    # Update state
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [assistant_message]
    new_state["current_agent"] = "knowledge"
    
    return new_state
