"""
Knowledge Agent - Personal knowledge base, facts, and memories.
"""

from app.orchestration.state import AgentState, Message
from app.config.llm import get_llm
from app.prompts.templates import KNOWLEDGE_AGENT_PROMPT
from app.rag import get_retriever
from datetime import datetime


def knowledge_agent(state: AgentState) -> AgentState:
    """
    Knowledge agent that handles personal knowledge and memory queries.
    
    Specializes in:
    - Personal facts and information
    - Preferences and interests
    - Experiences and memories
    - Background and history
    
    Uses RAG to retrieve relevant personal knowledge.
    
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
    
    # Retrieve relevant context from knowledge base
    retriever = get_retriever()
    context = retriever.retrieve_and_format(
        query=user_query,
        domain="knowledge",
        top_k=3
    )
    
    # Get LLM instance
    llm = get_llm(temperature=0.4)
    
    # Prepare system prompt with retrieved context
    system_prompt = KNOWLEDGE_AGENT_PROMPT
    if context:
        system_prompt += f"\n\n{context}\n\nUse the personal knowledge above to provide accurate, personalized responses."
    
    # Build conversation history for LLM (include previous turns)
    llm_messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (last 10 messages for context)
    for msg in messages[-10:]:
        llm_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
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
