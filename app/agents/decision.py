"""
Decision Agent - Decision-making patterns, values, and reasoning.
"""

from app.orchestration.state import AgentState, Message
from app.config.llm import get_llm
from app.prompts.templates import DECISION_AGENT_PROMPT
from app.rag import get_retriever
from datetime import datetime


def decision_agent(state: AgentState) -> AgentState:
    """
    Decision agent that handles decision-making and value-based queries.
    
    Specializes in:
    - Decision analysis and trade-offs
    - Values and priorities
    - Strategic thinking
    - Option evaluation
    
    Uses RAG to retrieve past decisions and decision frameworks.
    
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
    
    # Retrieve relevant context from decision knowledge base
    retriever = get_retriever()
    context = retriever.retrieve_and_format(
        query=user_query,
        domain="decision",
        top_k=3
    )
    
    # Get LLM instance (lower temperature for structured analysis)
    llm = get_llm(temperature=0.4)
    
    # Prepare system prompt with retrieved context
    system_prompt = DECISION_AGENT_PROMPT
    if context:
        system_prompt += f"\n\n{context}\n\nUse the decision patterns above to provide consistent, value-aligned guidance."
    
    # Prepare messages for LLM
    llm_messages = [
        {"role": "system", "content": system_prompt},
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
        agent="decision",
        timestamp=datetime.now().isoformat()
    )
    
    # Update state
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [assistant_message]
    new_state["current_agent"] = "decision"
    
    return new_state
