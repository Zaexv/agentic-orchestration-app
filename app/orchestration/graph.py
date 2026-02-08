"""LangGraph Workflow for Digital Twin Agent Orchestration

This module defines the StateGraph that orchestrates routing and execution
of specialized agents using LangGraph's graph-based workflow system.
"""

from typing import Literal
from langgraph.graph import StateGraph, END

from app.orchestration.state import AgentState, increment_iteration, update_routing
from app.agents.router import router_agent_with_fallback
from app.agents.general import general_agent
from app.agents.professional import professional_agent
from app.agents.communication import communication_agent
from app.agents.knowledge import knowledge_agent
from app.agents.decision import decision_agent


def router_node(state: AgentState) -> AgentState:
    """
    Router node - Entry point that determines which specialized agent to call.
    
    Uses LLM-based routing with keyword fallback for reliability.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with routing decision
    """
    from app.orchestration.state import IterationLog
    from datetime import datetime
    
    # Get latest user message
    latest_message = state["messages"][-1].content
    
    # Route using LLM with fallback
    agent_name, confidence, reasoning = router_agent_with_fallback(latest_message)
    
    # Log this routing decision (only once per iteration)
    current_iter = state["iterations"] + 1
    # Check if we already logged routing for this iteration
    already_logged = any(
        log.iteration == current_iter and log.agent == "router"
        for log in state["iteration_log"]
    )
    if not already_logged:
        log_entry = IterationLog(
            iteration=current_iter,
            agent="router",
            action=f"Routed to {agent_name}",
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
        state["iteration_log"].append(log_entry)
    
    # Update routing information in state
    state = update_routing(state, agent_name, confidence, reasoning)
    
    # Update current agent
    state["current_agent"] = "router"
    
    return state


def route_to_agent(state: AgentState) -> str:
    """
    Conditional edge function that determines which agent node to call next.
    
    Returns the name of the next node based on the routing decision.
    
    Args:
        state: Current agent state
        
    Returns:
        Name of the next agent node
    """
    # Get the latest routing decision
    if state["routing_history"]:
        target_agent = state["routing_history"][-1].target_agent
        return target_agent
    
    # Fallback to general if no routing decision exists
    return "general"


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """
    Conditional edge function that determines if workflow should continue or end.
    
    Multi-turn is enabled: Agents can iterate multiple times to refine responses,
    gather more information, or perform complex multi-step reasoning.
    
    Checks:
    - Max iterations reached
    - should_continue flag
    - Agent confidence threshold
    
    Args:
        state: Current agent state
        
    Returns:
        "continue" to loop back to router, "end" to finish
    """
    from app.orchestration.state import IterationLog
    from datetime import datetime
    
    # Check if max iterations reached
    if state["iterations"] >= state["max_iterations"]:
        log_entry = IterationLog(
            iteration=state["iterations"],
            agent="workflow",
            action="Stopped: Max iterations reached",
            confidence=0.0,
            reasoning=f"Reached max iterations ({state['max_iterations']})",
            timestamp=datetime.now()
        )
        state["iteration_log"].append(log_entry)
        return "end"
    
    # Check should_continue flag
    if not state["should_continue"]:
        log_entry = IterationLog(
            iteration=state["iterations"],
            agent="workflow",
            action="Stopped: should_continue=False",
            confidence=0.0,
            reasoning="Agent signaled to stop",
            timestamp=datetime.now()
        )
        state["iteration_log"].append(log_entry)
        return "end"
    
    # Check if we have a final response
    if state.get("final_response"):
        return "end"
    
    # For low confidence (<70%), allow one retry with different agent
    if state["routing_history"]:
        latest_routing = state["routing_history"][-1]
        if latest_routing.confidence < 0.7 and state["iterations"] < 2:
            log_entry = IterationLog(
                iteration=state["iterations"],
                agent="workflow",
                action="Continuing: Low confidence retry",
                confidence=latest_routing.confidence,
                reasoning=f"Confidence {(latest_routing.confidence*100):.0f}% < 70%, retrying",
                timestamp=datetime.now()
            )
            state["iteration_log"].append(log_entry)
            return "continue"
    
    # Allow up to 3 iterations for complex queries
    if state["iterations"] < 3:
        # Check if the last message suggests more work needed
        if state["messages"]:
            last_message = state["messages"][-1].content.lower()
            # Continue if agent is asking questions or needs clarification
            if any(indicator in last_message for indicator in [
                "let me", "i'll also", "additionally", "furthermore",
                "i can also", "would you like", "shall i"
            ]):
                log_entry = IterationLog(
                    iteration=state["iterations"],
                    agent="workflow",
                    action="Continuing: Agent signaled more work",
                    confidence=0.0,
                    reasoning="Detected continuation keywords in response",
                    timestamp=datetime.now()
                )
                state["iteration_log"].append(log_entry)
                return "continue"
    
    # Default: end after processing
    log_entry = IterationLog(
        iteration=state["iterations"],
        agent="workflow",
        action="Stopped: Workflow complete",
        confidence=0.0,
        reasoning="No continuation conditions met",
        timestamp=datetime.now()
    )
    state["iteration_log"].append(log_entry)
    return "end"


def agent_wrapper(agent_func):
    """
    Wrapper for agent functions to increment iteration counter and log execution.
    
    Args:
        agent_func: The agent function to wrap
        
    Returns:
        Wrapped agent function
    """
    def wrapped(state: AgentState) -> AgentState:
        from app.orchestration.state import IterationLog, increment_iteration
        from datetime import datetime
        
        agent_name = agent_func.__name__.replace('_agent', '')
        
        # Execute the agent
        state = agent_func(state)
        
        # Log agent execution
        response_preview = state["messages"][-1].content[:100] if state["messages"] else "No response"
        log_entry = IterationLog(
            iteration=state["iterations"] + 1,
            agent=agent_name,
            action="Generated response",
            confidence=state["routing_confidence"],
            reasoning=f"Response: {response_preview}...",
            timestamp=datetime.now()
        )
        state["iteration_log"].append(log_entry)
        
        # Increment iteration counter
        state = increment_iteration(state)
        
        return state
    
    return wrapped


def create_workflow() -> StateGraph:
    """
    Create and configure the LangGraph workflow.
    
    Graph structure:
        START → router → [5 agents] → should_continue → END
                  ↑                           ↓
                  └───────────────────────────┘
                         (loop for multi-turn)
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("general", agent_wrapper(general_agent))
    workflow.add_node("professional", agent_wrapper(professional_agent))
    workflow.add_node("communication", agent_wrapper(communication_agent))
    workflow.add_node("knowledge", agent_wrapper(knowledge_agent))
    workflow.add_node("decision", agent_wrapper(decision_agent))
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional edges from router to agents
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "general": "general",
            "professional": "professional",
            "communication": "communication",
            "knowledge": "knowledge",
            "decision": "decision",
        }
    )
    
    # Add conditional edges from agents back to router or end
    for agent_name in ["general", "professional", "communication", "knowledge", "decision"]:
        workflow.add_conditional_edges(
            agent_name,
            should_continue,
            {
                "continue": "router",  # Loop back for multi-turn
                "end": END             # Finish workflow
            }
        )
    
    # Compile the graph
    return workflow.compile()


# Create the compiled workflow (singleton)
workflow_app = create_workflow()


def run_workflow(state: AgentState) -> AgentState:
    """
    Execute the workflow with the given initial state.
    
    Args:
        state: Initial agent state
        
    Returns:
        Final state after workflow execution
    """
    return workflow_app.invoke(state)
