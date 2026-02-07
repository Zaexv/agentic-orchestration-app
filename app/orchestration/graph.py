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
    # Get latest user message
    latest_message = state["messages"][-1].content
    
    # Route using LLM with fallback
    agent_name, confidence, reasoning = router_agent_with_fallback(latest_message)
    
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
    
    Checks:
    - Max iterations reached
    - should_continue flag
    
    Args:
        state: Current agent state
        
    Returns:
        "continue" to loop back to router, "end" to finish
    """
    # Check if max iterations reached
    if state["iterations"] >= state["max_iterations"]:
        return "end"
    
    # Check should_continue flag
    if not state["should_continue"]:
        return "end"
    
    # For now, always end after one agent execution (single-turn)
    # In Phase 6+, we'll enable multi-turn by checking for follow-up questions
    return "end"


def agent_wrapper(agent_func):
    """
    Wrapper for agent functions to increment iteration counter.
    
    Args:
        agent_func: The agent function to wrap
        
    Returns:
        Wrapped agent function
    """
    def wrapped(state: AgentState) -> AgentState:
        # Execute the agent
        state = agent_func(state)
        
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
