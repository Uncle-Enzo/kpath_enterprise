# PA Agent Enhancement - Agent-to-Agent Communication

## Current Implementation Issue

The PA Agent is currently trying to:
1. Search KPATH for tools
2. Directly call tool endpoints (e.g., `/agents/shoes/search`)
3. These endpoints don't exist in the main API, causing 404 errors

## Correct Implementation

The PA Agent should instead:
1. Search KPATH for services/agents
2. Call the agent's chat endpoint with full context
3. Let the target agent decide how to handle the request

## Code Example - Enhanced PA Agent

```python
async def process_with_agent_delegation(self, user_query: str) -> str:
    """
    Process user query with proper agent-to-agent communication
    """
    # Step 1: Search KPATH for relevant services
    search_results = await self.search_kpath(
        user_query, 
        search_mode="agents_and_tools",
        include_orchestration=True  # Get integration details
    )
    
    if not search_results.get("results"):
        return "No relevant services found for your request."
    
    # Step 2: Prepare delegation to specialized agent
    best_match = search_results["results"][0]
    service = best_match["service"]
    recommended_tool = best_match.get("recommended_tool")
    
    # Step 3: Call the agent's chat endpoint with full context
    if service.get("integration_details"):
        base_endpoint = service["integration_details"]["base_endpoint"]
        chat_endpoint = f"{base_endpoint}/chat"
        
        # Construct comprehensive message for the target agent
        agent_request = {
            "message": user_query,
            "context": {
                "source": "PA_Agent",
                "user_intent": user_query,
                "kpath_analysis": {
                    "matched_service": service["name"],
                    "confidence_score": best_match["score"],
                    "recommended_tool": recommended_tool["tool_name"] if recommended_tool else None,
                    "tool_parameters": self._extract_parameters_from_query(user_query, recommended_tool)
                }
            },
            "request_metadata": {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "pa_version": "1.0.0"
            }
        }
        
        try:
            # Make request to specialized agent
            response = await self.http_client.post(
                chat_endpoint,
                json=agent_request,
                headers={"X-API-Key": self.api_key}
            )
            response.raise_for_status()
            
            result = response.json()
            return self._format_agent_response(result, service["name"])
            
        except Exception as e:
            logger.error(f"Error communicating with {service['name']}: {e}")
            return self._provide_fallback_guidance(user_query, service, recommended_tool)
    
    else:
        # No integration details available
        return self._provide_manual_guidance(user_query, service)

def _extract_parameters_from_query(self, query: str, tool_info: Dict) -> Dict:
    """
    Use GPT-4o to extract parameters from natural language query
    """
    if not tool_info:
        return {}
    
    prompt = f"""
    Extract parameters for the tool '{tool_info['tool_name']}' from this query: "{query}"
    
    Tool expects these parameters:
    {json.dumps(tool_info.get('input_schema', {}), indent=2)}
    
    Return extracted parameters as JSON.
    """
    
    # Use GPT-4o to extract parameters
    response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {}
```

## Benefits of This Approach

1. **Flexibility**: Target agents can interpret requests in their own way
2. **Context Preservation**: Full conversation context is passed between agents
3. **Error Handling**: Graceful fallback when agents are unavailable
4. **Extensibility**: Easy to add new context fields without breaking existing integrations
5. **Debugging**: Clear trace of what information was passed between agents

## Required Updates

1. **PA Agent (`pa_agent.py`)**: Implement the enhanced delegation method
2. **Service Agents**: Enhance chat endpoints to handle structured context
3. **KPATH Search**: Ensure integration details are always included for agents
4. **Documentation**: Update integration guides with this pattern
