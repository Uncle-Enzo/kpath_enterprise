"""
Enhanced Personal Assistant (PA) Agent - GPT-4o powered orchestration agent
Implements proper agent-to-agent communication pattern
"""

import os
import json
import logging
import asyncio
import argparse
import uuid
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
from dotenv import load_dotenv
from dataclasses import dataclass, asdict

# Import token tracking
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from token_tracker import TokenTracker

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Run: pip install openai")
    openai = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Track token usage for a session"""
    session_id: str
    timestamp: datetime
    operation: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    query: str = ""
    response_preview: str = ""

@dataclass
class SessionMetrics:
    """Overall session metrics"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tokens: int = 0
    total_api_calls: int = 0
    queries_processed: int = 0
    token_usage_history: List[TokenUsage] = None
    
    def __post_init__(self):
        if self.token_usage_history is None:
            self.token_usage_history = []

class EnhancedPersonalAssistantAgent:
    """
    Enhanced Personal Assistant Agent with proper agent-to-agent communication.
    
    Key Changes:
    - Communicates with service agents via chat endpoints
    - Passes full context including tool suggestions
    - Allows target agents to make autonomous decisions
    - Maintains conversation history
    """
    
    def __init__(self, api_key: Optional[str] = None, kpath_base_url: str = "http://localhost:8000"):
        """Initialize the PA Agent"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.kpath_base_url = kpath_base_url
        self.kpath_api_key = "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"
        
        # Token usage tracking
        self.session_id = f"pa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_metrics = SessionMetrics(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        # Conversation history
        self.conversation_history = []
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. AI features will not work.")
            
        if openai and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            
        # HTTP client for API calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Enhanced system prompt
        self.system_prompt = """You are an Enhanced Personal Assistant Agent that orchestrates services through agent-to-agent communication.

Your process:
1. Analyze user requests to understand their needs
2. Search KPATH Enterprise for relevant services and tools
3. Delegate to specialized agents with full context
4. Allow agents to make autonomous decisions
5. Synthesize responses from multiple agents if needed

When communicating with other agents:
- Pass the complete user request and context
- Include your analysis and recommendations
- Provide integration details and available tools
- Let the target agent decide how to handle the request

Be helpful, efficient, and maintain clear communication between agents."""

    async def search_kpath(self, query: str, search_mode: str = "agents_and_tools", 
                          limit: int = 10, include_orchestration: bool = True) -> Dict[str, Any]:
        """Search KPATH Enterprise with proper flags for agent communication"""
        try:
            search_url = f"{self.kpath_base_url}/api/v1/search"
            
            params = {
                "query": query,
                "search_mode": search_mode,
                "limit": limit,
                "response_mode": "compact",
                "include_orchestration": include_orchestration,  # Get integration details
                "api_key": self.kpath_api_key
            }
            
            response = await self.http_client.get(search_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error searching KPATH: {str(e)}")
            return {"error": str(e), "results": []}

    async def communicate_with_agent(self, service: Dict, user_query: str, 
                                   recommended_tool: Optional[Dict] = None,
                                   analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """Communicate with a service agent using proper agent-to-agent pattern"""
        try:
            # Get integration details
            integration = service.get("integration_details", {})
            if not integration:
                logger.warning(f"No integration details for service {service['name']}")
                return {"error": "No integration details available"}
            
            # Construct chat endpoint
            base_endpoint = integration.get("base_endpoint", "")
            if not base_endpoint:
                return {"error": "No base endpoint configured"}
                
            chat_endpoint = f"{base_endpoint}/chat"
            
            # Build comprehensive agent message
            agent_message = {
                "message": user_query,
                "context": {
                    "source_agent": "PA_Agent",
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "user_intent": user_query,
                    "kpath_analysis": {
                        "matched_service": service["name"],
                        "service_description": service.get("description", ""),
                        "confidence_score": analysis.get("confidence", 0.0) if analysis else 0.0,
                        "recommended_tool": recommended_tool.get("tool_name") if recommended_tool else None,
                        "tool_description": recommended_tool.get("tool_description") if recommended_tool else None,
                        "recommendation_reason": recommended_tool.get("recommendation_reason") if recommended_tool else None
                    },
                    "suggested_action": {
                        "tool": recommended_tool.get("tool_name") if recommended_tool else None,
                        "parameters": await self._extract_parameters(user_query, recommended_tool) if recommended_tool else {}
                    } if recommended_tool else None,
                    "available_tools": service.get("available_tools", [])
                },
                "integration_info": {
                    "auth_method": integration.get("auth_method", "api_key"),
                    "rate_limits": integration.get("rate_limit_requests"),
                    "capabilities": service.get("capabilities", [])
                },
                "conversation_history": self.conversation_history[-5:]  # Last 5 interactions
            }
            
            # Make request to agent's chat endpoint
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.kpath_api_key
            }
            
            logger.info(f"🤝 Communicating with {service['name']} at {chat_endpoint}")
            
            response = await self.http_client.post(
                chat_endpoint,
                json=agent_message,
                headers=headers
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Track the interaction
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "agent": service["name"],
                "request": user_query,
                "response": result
            })
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error communicating with {service['name']}: {e}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Error communicating with {service['name']}: {str(e)}")
            return {"error": str(e)}

    async def _extract_parameters(self, query: str, tool_info: Optional[Dict]) -> Dict:
        """Use GPT-4o to extract parameters from natural language query"""
        if not tool_info or not self.client:
            return {}
        
        try:
            input_schema = tool_info.get("input_schema", {})
            if not input_schema:
                return {}
            
            prompt = f"""
            Extract parameters for the tool '{tool_info['tool_name']}' from this query: "{query}"
            
            Tool expects these parameters:
            {json.dumps(input_schema, indent=2)}
            
            Return ONLY a valid JSON object with the extracted parameters.
            If a parameter cannot be extracted, omit it rather than guessing.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            params_text = response.choices[0].message.content
            # Track token usage
            self.track_token_usage("parameter_extraction", response, query, params_text)
            
            # Extract JSON
            json_start = params_text.find('{')
            json_end = params_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(params_text[json_start:json_end])
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting parameters: {str(e)}")
            return {}

    async def process_request(self, user_query: str) -> str:
        """
        Enhanced processing with agent-to-agent communication
        """
        try:
            self.session_metrics.queries_processed += 1
            print(f"🔍 Processing: '{user_query}'")
            
            # Step 1: Search KPATH for relevant services and tools
            search_results = await self.search_kpath(
                user_query, 
                search_mode="agents_and_tools",
                include_orchestration=True
            )
            
            if "error" in search_results:
                return f"Error searching KPATH Enterprise: {search_results['error']}"
            
            results = search_results.get("results", [])
            if not results:
                return "No relevant services found for your request."
            
            print(f"📋 Found {len(results)} relevant services/tools")
            
            # Step 2: Analyze with GPT-4o
            if self.client:
                analysis = await self._analyze_with_gpt(user_query, results)
            else:
                # Fallback without GPT-4o
                analysis = {"selected_services": [results[0]], "strategy": "direct"}
            
            # Step 3: Communicate with selected agents
            responses = []
            for service_info in analysis.get("selected_services", [results[0]]):
                service = service_info.get("service", results[0].get("service"))
                recommended_tool = service_info.get("recommended_tool", results[0].get("recommended_tool"))
                
                print(f"🤝 Delegating to {service['name']}")
                
                agent_response = await self.communicate_with_agent(
                    service=service,
                    user_query=user_query,
                    recommended_tool=recommended_tool,
                    analysis=analysis
                )
                
                responses.append({
                    "agent": service["name"],
                    "response": agent_response
                })
            
            # Step 4: Synthesize final response
            return await self._synthesize_response(user_query, responses, analysis)
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"

    async def _analyze_with_gpt(self, user_query: str, search_results: List[Dict]) -> Dict:
        """Use GPT-4o to analyze search results and plan agent communication"""
        try:
            # Format results for GPT
            formatted_results = []
            for idx, result in enumerate(search_results[:5]):  # Top 5 results
                service = result.get("service", {})
                tool = result.get("recommended_tool", {})
                
                formatted_results.append(f"""
Result {idx + 1}:
- Service: {service.get('name', 'Unknown')}
- Description: {service.get('description', 'No description')}
- Score: {result.get('score', 0):.3f}
- Recommended Tool: {tool.get('tool_name', 'None')} - {tool.get('tool_description', '')}
- Has Chat Endpoint: {bool(service.get('integration_details', {}).get('base_endpoint', ''))}
""")
            
            analysis_prompt = f"""
User Query: "{user_query}"

Available Services and Tools:
{"".join(formatted_results)}

Please analyze this request and determine:
1. Which service(s) should handle this request
2. Whether to use the recommended tools or let agents decide
3. The order of operations if multiple services are needed

Return your analysis as JSON:
{{
    "analysis": "Your interpretation of the user's need",
    "selected_services": [
        {{
            "service": <service object from results>,
            "recommended_tool": <tool object if applicable>,
            "reason": "Why this service was selected"
        }}
    ],
    "strategy": "single_agent" or "multi_agent",
    "confidence": 0.0-1.0
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            self.track_token_usage("analysis", response, user_query, analysis_text[:200])
            
            # Parse JSON response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                analysis = json.loads(analysis_text[json_start:json_end])
                
                # Map back to actual service objects
                for item in analysis.get("selected_services", []):
                    # Find matching service from results
                    for result in search_results:
                        if result["service"]["name"] == item.get("service", {}).get("name"):
                            item["service"] = result["service"]
                            item["recommended_tool"] = result.get("recommended_tool")
                            break
                
                return analysis
            
            # Fallback
            return {
                "analysis": analysis_text,
                "selected_services": [{"service": search_results[0]["service"]}],
                "strategy": "single_agent",
                "confidence": 0.5
            }
            
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            # Fallback to first result
            return {
                "analysis": "Error in analysis, using top result",
                "selected_services": [{"service": search_results[0]["service"]}],
                "strategy": "single_agent",
                "confidence": 0.3
            }

    async def _synthesize_response(self, user_query: str, agent_responses: List[Dict], 
                                  analysis: Dict) -> str:
        """Synthesize final response from agent communications"""
        try:
            # Handle single agent response
            if len(agent_responses) == 1:
                agent_name = agent_responses[0]["agent"]
                response = agent_responses[0]["response"]
                
                if "error" in response:
                    return await self._provide_fallback_response(user_query, agent_name, response["error"])
                
                # Extract the actual response
                if isinstance(response, dict):
                    if "response" in response:
                        return f"Here's what I found through {agent_name}:\n\n{response['response']}"
                    elif "result" in response:
                        return f"Here's the result from {agent_name}:\n\n{json.dumps(response['result'], indent=2)}"
                    else:
                        return f"Response from {agent_name}:\n\n{json.dumps(response, indent=2)}"
                else:
                    return str(response)
            
            # Handle multiple agent responses with GPT synthesis
            if self.client:
                synthesis_prompt = f"""
User Query: "{user_query}"

I coordinated with multiple specialized agents. Here are their responses:

{json.dumps(agent_responses, indent=2)}

Please synthesize these responses into a single, coherent answer for the user.
Make it conversational and helpful, highlighting the key information from each agent.
"""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are synthesizing responses from multiple specialized agents into a unified answer."},
                        {"role": "user", "content": synthesis_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                final_response = response.choices[0].message.content
                self.track_token_usage("synthesis", response, user_query, final_response[:200])
                
                return final_response
            else:
                # Fallback without GPT
                parts = ["I coordinated with multiple services for your request:\n"]
                for resp in agent_responses:
                    parts.append(f"\n**{resp['agent']}**:")
                    if "error" in resp["response"]:
                        parts.append(f"Error: {resp['response']['error']}")
                    else:
                        parts.append(json.dumps(resp["response"], indent=2))
                
                return "\n".join(parts)
                
        except Exception as e:
            logger.error(f"Error synthesizing response: {str(e)}")
            return f"I received responses but encountered an error formatting them: {str(e)}"

    async def _provide_fallback_response(self, user_query: str, agent_name: str, error: str) -> str:
        """Provide helpful fallback when agent communication fails"""
        if "404" in str(error) or "Not Found" in str(error):
            return f"""I found that {agent_name} would be the best service for your request about "{user_query}", but I couldn't connect to it directly.

The service appears to be temporarily unavailable or not fully integrated. Here's what I recommend:

1. The {agent_name} service specializes in handling requests like yours
2. It may have tools for the specific functionality you need
3. You might try accessing it directly if you have the appropriate credentials

Would you like me to search for alternative services that might help with your request?"""
        else:
            return f"""I attempted to connect with {agent_name} for your request but encountered an issue: {error}

Let me search for alternative services that might help with "{user_query}"."""

    # Token tracking methods (same as original)
    def track_token_usage(self, operation: str, response, query: str = "", response_preview: str = ""):
        """Track token usage from OpenAI API response"""
        try:
            if hasattr(response, 'usage') and response.usage:
                usage = TokenUsage(
                    session_id=self.session_id,
                    timestamp=datetime.now(),
                    operation=operation,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    model=getattr(response, 'model', 'gpt-4o'),
                    query=query,
                    response_preview=response_preview[:200] if response_preview else ""
                )
                
                self.session_metrics.token_usage_history.append(usage)
                self.session_metrics.total_tokens += usage.total_tokens
                self.session_metrics.total_api_calls += 1
                
                logger.info(f"Token usage - {operation}: {usage.total_tokens} tokens")
                
        except Exception as e:
            logger.error(f"Error tracking token usage: {str(e)}")
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """Get current session metrics"""
        if self.session_metrics.end_time is None:
            self.session_metrics.end_time = datetime.now()
            
        return {
            "session_id": self.session_metrics.session_id,
            "start_time": self.session_metrics.start_time.isoformat(),
            "end_time": self.session_metrics.end_time.isoformat() if self.session_metrics.end_time else None,
            "duration_seconds": (self.session_metrics.end_time - self.session_metrics.start_time).total_seconds() if self.session_metrics.end_time else None,
            "total_tokens": self.session_metrics.total_tokens,
            "total_api_calls": self.session_metrics.total_api_calls,
            "queries_processed": self.session_metrics.queries_processed,
            "average_tokens_per_query": self.session_metrics.total_tokens / max(1, self.session_metrics.queries_processed),
            "token_usage_breakdown": [asdict(usage) for usage in self.session_metrics.token_usage_history]
        }
    
    def save_session_metrics(self, filepath: Optional[str] = None):
        """Save session metrics to file"""
        if filepath is None:
            filepath = f"pa_agent_metrics_{self.session_id}.json"
            
        metrics = self.get_session_metrics()
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
            
        logger.info(f"Session metrics saved to {filepath}")

    async def close(self):
        """Clean up resources and save metrics"""
        self.session_metrics.end_time = datetime.now()
        self.save_session_metrics()
        await self.http_client.aclose()


# Command-line interface
async def interactive_mode(agent: EnhancedPersonalAssistantAgent):
    """Run the agent in interactive mode"""
    print("\n🤖 Enhanced PA Agent - Interactive Mode")
    print("=" * 50)
    print("Type 'help' for available commands")
    print("Type 'quit' or 'exit' to stop")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if user_input.lower() == 'help':
                print("""
Available commands:
- Any natural language query to search for services
- 'status' - Check agent and connection status
- 'metrics' - Show current session metrics
- 'quit/exit/q' - Exit the agent
                """)
                continue
                
            if user_input.lower() == 'status':
                # Check KPATH connectivity
                test_result = await agent.search_kpath("test", limit=1)
                kpath_status = "✅ Connected" if "results" in test_result else "❌ Not connected"
                print(f"""
Agent Status:
- Session ID: {agent.session_id}
- KPATH API: {kpath_status}
- OpenAI: {"✅ Connected" if agent.client else "❌ Not configured"}
- Queries processed: {agent.session_metrics.queries_processed}
                """)
                continue
                
            if user_input.lower() == 'metrics':
                metrics = agent.get_session_metrics()
                print(f"""
Session Metrics:
- Total tokens used: {metrics['total_tokens']:,}
- API calls made: {metrics['total_api_calls']}
- Queries processed: {metrics['queries_processed']}
- Avg tokens/query: {metrics['average_tokens_per_query']:.1f}
                """)
                continue
            
            # Process the query
            print("\n🔄 Processing...")
            response = await agent.process_request(user_input)
            print(f"\n🤖 PA Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            logger.error(f"Interactive mode error: {str(e)}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Personal Assistant Agent")
    parser.add_argument("query", nargs="?", help="Query to process (if not provided, enters interactive mode)")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--kpath-url", default="http://localhost:8000", help="KPATH Enterprise base URL")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = EnhancedPersonalAssistantAgent(
        api_key=args.api_key,
        kpath_base_url=args.kpath_url
    )
    
    try:
        if args.query:
            # Single query mode
            print(f"🔍 Processing query: {args.query}")
            response = await agent.process_request(args.query)
            print(f"\n📝 Response:\n{response}")
        else:
            # Interactive mode
            await interactive_mode(agent)
            
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
