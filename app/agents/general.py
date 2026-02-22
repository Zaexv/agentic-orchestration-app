"""
General Agent - Fallback agent for miscellaneous queries.
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def general_agent(state):
    """
    General-purpose agent that handles miscellaneous queries.
    
    Acts as a fallback when other agents are not appropriate.
    Uses RAG to retrieve general information and has access to tools like weather.
    
    Args:
        state: Current agent state with message history
        
    Returns:
        Updated state with agent response
    """
    # Import here to avoid circular dependency
    from app.orchestration.state import Message
    from app.config.llm import get_llm
    from app.prompts.templates import GENERAL_AGENT_PROMPT
    from app.rag import get_retriever
    from app.tools.weather import weather_tools
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    
    # Get the latest user message
    messages = state["messages"]
    if not messages:
        return state
    
    latest_message = messages[-1]
    user_query = latest_message.content
    
    # Retrieve relevant context from general knowledge base
    retriever = get_retriever()
    context = retriever.retrieve_and_format(
        query=user_query,
        domain="general",
        top_k=3
    )
    
    # Get LLM instance with tools bound
    llm = get_llm(temperature=0.7)
    llm_with_tools = llm.bind_tools(weather_tools)
    
    # Prepare system prompt
    system_prompt = GENERAL_AGENT_PROMPT
    if context:
        system_prompt += f"\n\n{context}\n\nUse the information above when relevant."
    
    system_prompt += """

You have access to weather tools (get_weather, get_weather_forecast).
When users ask about weather, use these tools to get accurate current data.
For other queries, respond normally with your knowledge."""
    
    # Build conversation messages
    llm_messages = [SystemMessage(content=system_prompt)]
    
    # Add conversation history (last 10 messages)
    for msg in messages[-10:-1]:
        if msg.role == "user":
            llm_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            llm_messages.append(AIMessage(content=msg.content))
    
    # Add current user message
    llm_messages.append(HumanMessage(content=user_query))
    
    try:
        # Invoke LLM with tools
        response = llm_with_tools.invoke(llm_messages)
        
        # Check if tool calls are needed
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # Execute tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Find and execute the tool
                for tool in weather_tools:
                    if tool.name == tool_name:
                        try:
                            result = tool.invoke(tool_args)
                            tool_results.append(f"\n[Tool: {tool_name}]\n{result}")
                            logger.info(f"Executed tool: {tool_name} with args: {tool_args}")
                        except Exception as e:
                            tool_results.append(f"\n[Tool Error: {tool_name}] {str(e)}")
                            logger.error(f"Tool execution error: {e}")
                        break
            
            # If we got tool results, include them in the response
            if tool_results:
                response_content = response.content + "\n\n" + "\n".join(tool_results) if response.content else "\n".join(tool_results)
            else:
                response_content = response.content if response.content else "I apologize, but I couldn't fetch the weather information."
        else:
            # No tool calls, just return the response
            response_content = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        logger.error(f"Error in general agent: {e}", exc_info=True)
        response_content = "I apologize, but I encountered an error processing your request. Please try again."
    
    # Create response message
    assistant_message = Message(
        role="assistant",
        content=response_content,
        agent="general",
        timestamp=datetime.now().isoformat()
    )
    
    # Update state
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [assistant_message]
    new_state["current_agent"] = "general"
    
    return new_state
