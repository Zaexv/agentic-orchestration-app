"""
Router Agent - LLM-based intelligent routing for the Digital Twin system.
"""

import json
from typing import Optional
from app.config.llm import get_llm
from app.prompts.templates import ROUTER_AGENT_PROMPT


def router_agent(message: str) -> tuple[str, float, str]:
    """
    LLM-based router that intelligently routes queries to appropriate agents.
    
    Uses an LLM to analyze the query semantically and determine the best agent,
    providing better accuracy than keyword-based routing.
    
    Args:
        message: User message to route
        
    Returns:
        Tuple of (agent_name, confidence, reasoning)
    """
    # Get LLM instance with low temperature for consistent routing
    llm = get_llm(temperature=0.2)
    
    # Prepare the routing prompt
    full_prompt = f"{ROUTER_AGENT_PROMPT}\n\nUser Query: \"{message}\"\n\nYour routing decision (JSON):"
    
    try:
        # Get routing decision from LLM
        response = llm.invoke([
            {"role": "system", "content": "You are a routing agent that responds only with valid JSON."},
            {"role": "user", "content": full_prompt}
        ])
        
        # Extract response content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Parse JSON response
        # Try to extract JSON from response (in case LLM adds extra text)
        response_text = response_text.strip()
        
        # Find JSON object in response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            routing_decision = json.loads(json_str)
            
            agent = routing_decision.get("agent", "general")
            confidence = routing_decision.get("confidence", 0.6)
            reasoning = routing_decision.get("reasoning", "LLM routing decision")
            
            # Validate agent name
            valid_agents = ["professional", "communication", "knowledge", "decision", "general"]
            if agent not in valid_agents:
                agent = "general"
                confidence = 0.6
                reasoning = f"Invalid agent '{agent}' returned, using general"
            
            # Ensure confidence is in valid range
            confidence = max(0.0, min(1.0, float(confidence)))
            
            return agent, confidence, reasoning
        else:
            # JSON not found, fallback
            return "general", 0.6, "Could not parse LLM response, using general agent"
    
    except json.JSONDecodeError as e:
        # JSON parsing failed, fallback to general
        return "general", 0.6, f"JSON decode error: {str(e)}, using general agent"
    
    except Exception as e:
        # Any other error, fallback to general
        return "general", 0.5, f"Router error: {str(e)}, using general agent"


def router_agent_with_fallback(message: str) -> tuple[str, float, str]:
    """
    Router with keyword fallback for reliability.
    
    Tries LLM-based routing first, falls back to keyword matching if LLM fails.
    
    Args:
        message: User message to route
        
    Returns:
        Tuple of (agent_name, confidence, reasoning)
    """
    try:
        agent, confidence, reasoning = router_agent(message)
        
        # If confidence is too low or agent is general with low confidence,
        # use keyword fallback
        if confidence < 0.5:
            return _keyword_fallback(message)
        
        return agent, confidence, f"LLM: {reasoning}"
    
    except Exception as e:
        # LLM routing failed completely, use keyword fallback
        return _keyword_fallback(message)


def _keyword_fallback(message: str) -> tuple[str, float, str]:
    """
    Simple keyword-based routing fallback.
    
    Used when LLM routing fails or returns low confidence.
    
    Args:
        message: User message to route
        
    Returns:
        Tuple of (agent_name, confidence, reasoning)
    """
    message_lower = message.lower()
    
    # Quick keyword checks
    professional_keywords = ["code", "programming", "python", "api", "debug", "technical"]
    communication_keywords = ["write", "email", "draft", "tone", "message"]
    knowledge_keywords = ["what do i", "my preference", "my favorite", "tell me about my"]
    decision_keywords = ["should i", "decide", "choose", "recommend", "pros and cons"]
    
    # Count matches
    scores = {
        "professional": sum(1 for kw in professional_keywords if kw in message_lower),
        "communication": sum(1 for kw in communication_keywords if kw in message_lower),
        "knowledge": sum(1 for kw in knowledge_keywords if kw in message_lower),
        "decision": sum(1 for kw in decision_keywords if kw in message_lower),
    }
    
    max_score = max(scores.values())
    
    if max_score == 0:
        return "general", 0.6, "Fallback: No keywords matched"
    
    best_agent = max(scores, key=scores.get)
    confidence = min(0.75, 0.6 + (max_score * 0.1))
    
    return best_agent, confidence, f"Fallback: Matched {max_score} keyword(s)"
