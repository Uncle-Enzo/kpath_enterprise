"""
Personal Assistant (PA) Agent - GPT-4o powered orchestration agent
Queries KPATH Enterprise to discover and connect to appropriate services
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

class PersonalAssistantAgent:
    """
    Personal Assistant Agent that orchestrates services through KPATH Enterprise.
    
    Flow:
    1. Takes user query
    2. Searches KPATH for relevant tools/services  
    3. Uses GPT-4o to analyze results and plan execution
    4. Connects to appropriate services
    5. Returns integrated response to user
    """
    
    def __init__(self, api_key: Optional[str] = None, kpath_base_url: str = "http://localhost:8000"):
        """Initialize the PA Agent"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.kpath_base_url = kpath_base_url
        
        # Token usage tracking
        self.session_id = f"pa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_metrics = SessionMetrics(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. AI features will not work.")
            
        if openai and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            
        # HTTP client for KPATH API calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # System prompt for the PA Agent
        self.system_prompt = """You are a Personal Assistant Agent that helps users by finding and coordinating appropriate tools and services.

Your process:
1. Analyze user requests to understand their needs
2. Review available tools and services from KPATH Enterprise
3. Select the most appropriate tools/services for the task
4. Coordinate between multiple services if needed
5. Provide a comprehensive response to the user

When you receive search results from KPATH, you should:
- Evaluate which tools/services are most relevant
- Consider if multiple tools need to be used together
- Plan the execution sequence
- Provide clear explanations of what you're doing

Be helpful, efficient, and thorough in your responses."""

    async def search_kpath(self, query: str, search_mode: str = "tools_only", limit: int = 10) -> Dict[str, Any]:
        """Search KPATH Enterprise for relevant tools and services"""
        try:
            search_url = f"{self.kpath_base_url}/api/v1/search"
            
            params = {
                "query": query,
                "search_mode": search_mode,
                "limit": limit,
                "response_mode": "compact",  # Use optimized response mode
                "api_key": "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"  # KPATH API key
            }
            
            response = await self.http_client.get(search_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error searching KPATH: {str(e)}")
            return {"error": str(e), "results": []}

    async def call_service_tool(self, service_name: str, tool_name: str, endpoint: str, 
                               method: str = "GET", params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """Make a call to a specific service tool"""
        try:
            # Construct the full URL
            if endpoint.startswith('http'):
                url = endpoint
            else:
                url = f"{self.kpath_base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = await self.http_client.get(url, params=params or {})
            elif method.upper() == "POST":
                response = await self.http_client.post(url, json=data or {}, params=params or {})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error calling {service_name}.{tool_name}: {str(e)}")
            return {"error": str(e)}

    async def process_request(self, user_query: str) -> str:
        """
        Main processing method: 
        1. Search KPATH for relevant tools
        2. Use GPT-4o to analyze and plan
        3. Execute the plan
        4. Return response
        """
        try:
            self.session_metrics.queries_processed += 1
            print(f"🔍 Searching KPATH for: '{user_query}'")
            
            # Step 1: Search KPATH for relevant tools
            search_results = await self.search_kpath(user_query)
            
            if "error" in search_results:
                return f"Error searching KPATH Enterprise: {search_results['error']}"
            
            results = search_results.get("results", [])
            if not results:
                return "No relevant tools or services found for your request."
            
            print(f"📋 Found {len(results)} relevant tools")
            
            # Step 2: Use GPT-4o to analyze results and plan execution
            if not self.client:
                return "OpenAI client not available. Cannot process request intelligently."
            
            # Prepare the context for GPT-4o
            tools_context = self._format_tools_for_gpt(results)
            
            analysis_prompt = f"""
            User Request: "{user_query}"
            
            Available Tools and Services:
            {tools_context}
            
            Please analyze this request and the available tools, then:
            1. Identify which tool(s) would best help with this request
            2. Determine the appropriate parameters to use
            3. Plan the execution sequence if multiple tools are needed
            4. Provide a response plan
            
            Format your response as JSON with this structure:
            {{
                "analysis": "Your analysis of the request",
                "selected_tools": [
                    {{
                        "service_name": "ServiceName",
                        "tool_name": "tool_name", 
                        "reason": "Why this tool was selected",
                        "parameters": {{"param1": "value1"}},
                        "endpoint": "/endpoint/path",
                        "method": "GET or POST"
                    }}
                ],
                "execution_plan": "Description of how tools will be used",
                "response_strategy": "How to present results to user"
            }}
            """
            
            gpt_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Track token usage for analysis
            self.track_token_usage("analysis", gpt_response, user_query, gpt_response.choices[0].message.content)
            
            # Parse GPT-4o response
            analysis_text = gpt_response.choices[0].message.content
            
            try:
                # Extract JSON from the response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                analysis_json = json.loads(analysis_text[json_start:json_end])
            except:
                # If JSON parsing fails, return the analysis as text
                return f"Analysis: {analysis_text}"
            
            print(f"🤖 GPT-4o Analysis: {analysis_json.get('analysis', 'No analysis provided')}")
            
            # Step 3: Execute the plan
            return await self._execute_plan(analysis_json, user_query)
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return f"Error processing your request: {str(e)}"

    def _format_tools_for_gpt(self, results: List[Dict]) -> str:
        """Format search results for GPT-4o analysis"""
        formatted = []
        
        for result in results[:10]:  # Limit to top 10 results
            if 'recommended_tool' in result:
                tool = result['recommended_tool']
                formatted.append(f"""
Service: {tool.get('service_name', 'Unknown')}
Tool: {tool.get('tool_name', 'Unknown')}
Description: {tool.get('tool_description', 'No description')}
Score: {tool.get('recommendation_score', 0):.2f}
""")
        
        return "\n".join(formatted) if formatted else "No tools available"

    async def _execute_plan(self, analysis: Dict, user_query: str) -> str:
        """Execute the planned tool calls"""
        try:
            selected_tools = analysis.get("selected_tools", [])
            if not selected_tools:
                return f"Analysis: {analysis.get('analysis', 'No specific tools recommended')}"
            
            results = []
            
            for tool_plan in selected_tools:
                service_name = tool_plan.get("service_name", "Unknown")
                tool_name = tool_plan.get("tool_name", "Unknown")
                endpoint = tool_plan.get("endpoint", "")
                method = tool_plan.get("method", "GET")
                parameters = tool_plan.get("parameters", {})
                
                print(f"🔧 Executing: {service_name}.{tool_name}")
                
                # Execute the tool call
                if method.upper() == "GET":
                    result = await self.call_service_tool(
                        service_name, tool_name, endpoint, method, params=parameters
                    )
                else:
                    result = await self.call_service_tool(
                        service_name, tool_name, endpoint, method, data=parameters
                    )
                
                results.append({
                    "tool": f"{service_name}.{tool_name}",
                    "result": result
                })
            
            # Use GPT-4o to synthesize the final response
            return await self._synthesize_response(analysis, results, user_query)
            
        except Exception as e:
            logger.error(f"Error executing plan: {str(e)}")
            return f"Error executing plan: {str(e)}"

    async def _synthesize_response(self, analysis: Dict, tool_results: List[Dict], user_query: str) -> str:
        """Use GPT-4o to synthesize a final response from tool results"""
        try:
            synthesis_prompt = f"""
            Original User Query: "{user_query}"
            
            Execution Plan: {analysis.get('execution_plan', 'No plan provided')}
            
            Tool Results:
            {json.dumps(tool_results, indent=2)}
            
            Please synthesize these results into a helpful, coherent response for the user.
            Focus on answering their original question and providing actionable information.
            Be conversational and helpful.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant synthesizing tool results into a user-friendly response."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Track token usage for synthesis
            final_response = response.choices[0].message.content
            self.track_token_usage("synthesis", response, user_query, final_response)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error synthesizing response: {str(e)}")
            # Fallback: return raw results
            return f"Tool execution completed. Results: {json.dumps(tool_results, indent=2)}"

    async def close(self):
        """Clean up resources and save metrics"""
        self.session_metrics.end_time = datetime.now()
        self.save_session_metrics()
        await self.http_client.aclose()
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
                
                logger.info(f"Token usage - {operation}: {usage.total_tokens} tokens (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
                
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
