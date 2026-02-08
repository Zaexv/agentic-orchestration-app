"""
Professional Agent - Technical expertise and work-related queries.
"""

from app.orchestration.state import AgentState, Message
from app.config.llm import get_llm
from app.prompts.templates import PROFESSIONAL_AGENT_PROMPT
from app.rag import get_retriever
from datetime import datetime


def professional_agent(state: AgentState) -> AgentState:
    """
    Professional agent that handles technical and work-related queries.
    
    Specializes in:
    - Programming and software development
    - Technical problem-solving
    - Professional knowledge and expertise
    - System design and architecture
    
    Uses RAG to retrieve relevant technical documents and context.
    
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
    
    # Retrieve relevant context from professional knowledge base
    retriever = get_retriever()
    context = retriever.retrieve_and_format(
        query=user_query,
        domain="professional",
        top_k=3
    )
    
    # Get LLM instance (lower temperature for technical accuracy)
    llm = get_llm(temperature=0.3)
    
    # Prepare system prompt with retrieved context
    system_prompt = PROFESSIONAL_AGENT_PROMPT
    if context:
        system_prompt += f"\n\n{context}\n\nUse the retrieved context above to provide accurate, personalized responses."
    
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
        agent="professional",
        timestamp=datetime.now().isoformat()
    )
    
    # Update state
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [assistant_message]
    new_state["current_agent"] = "professional"
    
    return new_state
