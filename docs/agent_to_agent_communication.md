# PA Agent to Service Agent Communication Pattern

## Correct Agent-to-Agent Communication

When the PA Agent needs to delegate work to another agent (like the Shoes Agent), it should send a structured conversation that includes:

### 1. The Message Structure

```python
# Instead of directly calling tool endpoints, PA should call the agent's chat endpoint
agent_message = {
    "message": "User request that needs handling",
    "context": {
        "original_user_query": "I want to buy running shoes under $150",
        "identified_intent": "product_search",
        "suggested_tool": "product_search",
        "suggested_parameters": {
            "query": "running shoes",
            "max_price": 150,
            "category": "athletic"
        }
    },
    "integration_info": {
        "base_endpoint": "http://localhost:8000/agents/shoes",
        "auth_method": "api_key",
        "available_tools": [
            {
                "tool_name": "product_search",
                "endpoint_pattern": "/search",
                "description": "Search for shoes by various criteria"
            }
        ]
    },
    "session_info": {
        "user_id": "user_123",
        "session_id": "session_abc",
        "previous_interactions": []
    }
}
```

### 2. The Communication Flow

```python
# PA Agent's improved call_service_agent method
async def call_service_agent(self, service_name: str, user_query: str, 
                             tool_suggestion: Dict, integration_details: Dict) -> Dict:
    """
    Communicate with another agent, passing full context
    """
    # Use the agent's chat endpoint
    chat_endpoint = f"{integration_details['base_endpoint']}/chat"
    
    # Construct the full conversation message
    agent_message = {
        "message": f"User request: {user_query}",
        "context": {
            "original_query": user_query,
            "pa_analysis": {
                "identified_intent": tool_suggestion.get('tool_name'),
                "confidence": tool_suggestion.get('recommendation_score'),
                "reasoning": tool_suggestion.get('recommendation_reason')
            },
            "suggested_action": {
                "tool": tool_suggestion.get('tool_name'),
                "parameters": self._extract_parameters(user_query, tool_suggestion)
            }
        },
        "integration_context": {
            "source_agent": "PA_Agent",
            "delegation_reason": "Specialized domain expertise required",
            "expected_response_format": "structured"
        }
    }
    
    # Make the request to the agent's chat endpoint
    response = await self.http_client.post(
        chat_endpoint,
        json=agent_message,
        headers={"X-API-Key": self.api_key}
    )
    
    return response.json()
```

### 3. The Receiving Agent's Responsibility

The Shoes Agent (or any specialized agent) should:

1. **Parse the incoming message** to understand:
   - What the user wants
   - What tool the PA Agent suggests
   - Any parameters or context provided

2. **Make its own decision** about:
   - Whether to use the suggested tool or a different one
   - How to best fulfill the request
   - What additional information might be needed

3. **Execute the appropriate action** using its internal tools

4. **Return a structured response** that the PA Agent can relay to the user

### 4. Example Implementation for Shoes Agent

```python
@router.post("/chat")
async def agent_chat(request: AgentMessage):
    """
    Handle conversations from other agents or users
    """
    # Extract context
    user_query = request.message
    context = request.get("context", {})
    suggested_tool = context.get("suggested_action", {}).get("tool")
    
    # Agent makes its own decision
    if suggested_tool == "product_search":
        # Use the suggested tool with provided parameters
        params = context.get("suggested_action", {}).get("parameters", {})
        result = await shoes_agent.product_search(**params)
    else:
        # Or the agent might decide differently
        result = await shoes_agent.process_natural_query(user_query)
    
    # Return structured response
    return {
        "response": result,
        "metadata": {
            "tool_used": suggested_tool,
            "processing_time": 150,
            "confidence": 0.95
        }
    }
```

### 5. Benefits of This Approach

1. **Flexibility**: Agents can adapt based on context
2. **Transparency**: Full conversation history is maintained
3. **Debugging**: Easy to trace what information was passed
4. **Extensibility**: New context fields can be added without breaking existing integrations
5. **Agent Autonomy**: Each agent can make its own decisions while respecting suggestions

### 6. Required Changes

1. **PA Agent**: Update to use agent chat endpoints instead of direct tool calls
2. **Service Agents**: Implement chat endpoints that can handle contextual conversations
3. **KPATH Response**: Should include the chat endpoint in integration details
4. **Documentation**: Clear specification of the agent-to-agent message format
