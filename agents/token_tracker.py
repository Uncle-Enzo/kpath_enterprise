"""
Token Usage Tracking Module for KPATH Enterprise Agents
"""

import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

@dataclass
class TokenUsageSession:
    """Tracks token usage for a single session"""
    session_id: str
    agent_name: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    api_calls: List[Dict[str, Any]] = field(default_factory=list)
    response_time_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None

@dataclass 
class APICallRecord:
    """Records details of a single API call"""
    timestamp: datetime
    api_type: str  # "openai", "kpath", "service"
    endpoint: str
    input_tokens: int
    output_tokens: int
    response_time_ms: int
    success: bool
    error_message: Optional[str] = None

class TokenTracker:
    """Tracks token usage across agent sessions"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.sessions: Dict[str, TokenUsageSession] = {}
        
        # Initialize token encoder
        if TIKTOKEN_AVAILABLE:
            self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        else:
            self.encoder = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoder:
            return len(self.encoder.encode(str(text)))
        else:
            # Rough approximation: ~4 characters per token
            return len(str(text)) // 4
    
    def start_session(self, session_id: str) -> TokenUsageSession:
        """Start a new tracking session"""
        session = TokenUsageSession(
            session_id=session_id,
            agent_name=self.agent_name,
            start_time=datetime.now()
        )
        self.sessions[session_id] = session
        return session
    
    def record_api_call(self, session_id: str, api_type: str, endpoint: str, 
                       input_text: str, output_text: str, response_time_ms: int,
                       success: bool = True, error_message: str = None):
        """Record an API call and its token usage"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        
        # Create API call record
        api_call = APICallRecord(
            timestamp=datetime.now(),
            api_type=api_type,
            endpoint=endpoint,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message
        )
        
        # Add to session
        session.api_calls.append({
            "timestamp": api_call.timestamp.isoformat(),
            "api_type": api_call.api_type,
            "endpoint": api_call.endpoint,
            "input_tokens": api_call.input_tokens,
            "output_tokens": api_call.output_tokens,
            "response_time_ms": api_call.response_time_ms,
            "success": api_call.success,
            "error_message": api_call.error_message
        })
        
        # Update session totals
        session.total_input_tokens += input_tokens
        session.total_output_tokens += output_tokens
        session.total_tokens += (input_tokens + output_tokens)
        session.response_time_ms += response_time_ms
        
        if not success:
            session.success = False
            if not session.error_message:
                session.error_message = error_message
    
    def record_openai_call(self, session_id: str, messages: List[Dict], response: Any, 
                          response_time_ms: int, success: bool = True, error_message: str = None):
        """Record an OpenAI API call"""
        # Format input messages as text
        input_text = json.dumps(messages)
        
        # Extract response content
        if hasattr(response, 'choices') and response.choices:
            output_text = response.choices[0].message.content
        else:
            output_text = str(response)
        
        self.record_api_call(
            session_id=session_id,
            api_type="openai",
            endpoint="chat/completions",
            input_text=input_text,
            output_text=output_text,
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message
        )
    
    def record_kpath_call(self, session_id: str, query: str, response: Dict, 
                         response_time_ms: int, success: bool = True, error_message: str = None):
        """Record a KPATH API call"""
        self.record_api_call(
            session_id=session_id,
            api_type="kpath",
            endpoint="search",
            input_text=query,
            output_text=json.dumps(response),
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message
        )
    
    def record_service_call(self, session_id: str, service_name: str, tool_name: str,
                           input_params: Dict, response: Dict, response_time_ms: int,
                           success: bool = True, error_message: str = None):
        """Record a service tool call"""
        self.record_api_call(
            session_id=session_id,
            api_type="service",
            endpoint=f"{service_name}.{tool_name}",
            input_text=json.dumps(input_params),
            output_text=json.dumps(response),
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message
        )
    
    def end_session(self, session_id: str) -> Optional[TokenUsageSession]:
        """End a tracking session and return the final data"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        session.end_time = datetime.now()
        
        return session
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of session token usage"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        duration = (session.end_time or datetime.now()) - session.start_time
        
        return {
            "session_id": session_id,
            "agent_name": session.agent_name,
            "duration_seconds": duration.total_seconds(),
            "total_tokens": session.total_tokens,
            "input_tokens": session.total_input_tokens,
            "output_tokens": session.total_output_tokens,
            "api_calls_count": len(session.api_calls),
            "total_response_time_ms": session.response_time_ms,
            "success": session.success,
            "error_message": session.error_message,
            "api_breakdown": self._get_api_breakdown(session),
            "cost_estimate_usd": self._estimate_cost(session)
        }
    
    def _get_api_breakdown(self, session: TokenUsageSession) -> Dict[str, Any]:
        """Get breakdown of API usage by type"""
        breakdown = {}
        
        for call in session.api_calls:
            api_type = call["api_type"]
            if api_type not in breakdown:
                breakdown[api_type] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "response_time_ms": 0
                }
            
            breakdown[api_type]["calls"] += 1
            breakdown[api_type]["input_tokens"] += call["input_tokens"]
            breakdown[api_type]["output_tokens"] += call["output_tokens"]
            breakdown[api_type]["total_tokens"] += (call["input_tokens"] + call["output_tokens"])
            breakdown[api_type]["response_time_ms"] += call["response_time_ms"]
        
        return breakdown
    
    def _estimate_cost(self, session: TokenUsageSession) -> float:
        """Estimate cost based on OpenAI pricing (GPT-4o)"""
        # GPT-4o pricing (as of 2024): $5/1M input tokens, $15/1M output tokens
        openai_input_tokens = 0
        openai_output_tokens = 0
        
        for call in session.api_calls:
            if call["api_type"] == "openai":
                openai_input_tokens += call["input_tokens"]
                openai_output_tokens += call["output_tokens"]
        
        input_cost = (openai_input_tokens / 1_000_000) * 5.0
        output_cost = (openai_output_tokens / 1_000_000) * 15.0
        
        return input_cost + output_cost
    
    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export complete session data for analysis"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            "session_metadata": {
                "session_id": session.session_id,
                "agent_name": session.agent_name,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "duration_seconds": (session.end_time - session.start_time).total_seconds() if session.end_time else None,
                "success": session.success,
                "error_message": session.error_message
            },
            "token_summary": {
                "total_tokens": session.total_tokens,
                "input_tokens": session.total_input_tokens,
                "output_tokens": session.total_output_tokens,
                "cost_estimate_usd": self._estimate_cost(session)
            },
            "performance_summary": {
                "total_response_time_ms": session.response_time_ms,
                "api_calls_count": len(session.api_calls),
                "average_response_time_ms": session.response_time_ms / max(1, len(session.api_calls))
            },
            "api_calls": session.api_calls,
            "api_breakdown": self._get_api_breakdown(session)
        }
