#!/usr/bin/env python3
"""
End-to-End Workflow Token Consumption Test

This script tests the complete workflow from PA Agent to KPATH to Shoes Agent
and measures token consumption for different approaches:

1. Standard Workflow: PA -> KPATH search -> PA analysis -> Shoes Agent chat
2. Tool-First Workflow: PA -> KPATH tools_only -> PA analysis -> Direct tool calls

Tests the full pipeline:
- PA Agent query processing
- KPATH search and tool discovery
- PA Agent analysis and planning
- Shoes Agent integration
- Final response synthesis
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from agents.pa.pa_agent import PersonalAssistantAgent
from agents.shoes.shoes_agent import ShoesAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class WorkflowTestResult:
    """Results from a complete workflow test"""
    test_id: str
    query: str
    approach: str
    start_time: datetime
    end_time: datetime
    duration_ms: int
    
    # PA Agent metrics
    pa_total_tokens: int
    pa_api_calls: int
    pa_search_time_ms: int
    
    # KPATH metrics
    kpath_results_count: int
    kpath_search_mode: str
    
    # Shoes Agent metrics (if used)
    shoes_total_tokens: int
    shoes_api_calls: int
    
    # Overall metrics
    total_tokens: int
    total_api_calls: int
    success: bool
    response_preview: str
    error_message: str = ""

class WorkflowTester:
    """Tests complete PA Agent -> KPATH -> Shoes Agent workflows"""
    
    def __init__(self):
        self.pa_agent = None
        self.shoes_agent = None
        self.test_results = []
        self.test_queries = [
            "I need running shoes under $150",
            "Find Nike Air Max in size 10",
            "Where can I buy shoes near me?",
            "Help me choose the right running shoes",
            "Track my shoe delivery",
            "What's the best shoe for flat feet?",
            "I want comfortable work shoes",
            "Show me the latest sneaker releases"
        ]
    
    async def setup_agents(self):
        """Initialize both agents"""
        logger.info("Setting up PA Agent and Shoes Agent...")
        self.pa_agent = PersonalAssistantAgent()
        self.shoes_agent = ShoesAgent()
        
        # Test connections
        if not self.pa_agent.client:
            raise Exception("PA Agent OpenAI client not initialized")
        if not self.shoes_agent.client:
            raise Exception("Shoes Agent OpenAI client not initialized")
        
        logger.info("✅ Both agents initialized successfully")
    
    async def test_standard_workflow(self, query: str) -> WorkflowTestResult:
        """
        Test Standard Workflow: PA -> KPATH search -> PA analysis -> Shoes Agent chat
        This simulates the natural workflow where PA agent discovers and then delegates to Shoes Agent
        """
        test_id = f"standard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        try:
            logger.info(f"🔄 Testing Standard Workflow: '{query}'")
            
            # Step 1: PA Agent processes query (includes KPATH search and analysis)
            response = await self.pa_agent.process_request(query)
            
            # Step 2: If PA Agent found shoes-related tools, delegate to Shoes Agent
            # (This is simulated since the actual delegation would happen inside PA Agent)
            if "shoe" in query.lower() or "sneaker" in query.lower() or "running" in query.lower():
                shoes_response = await self.shoes_agent.process_request(query)
                # In a real workflow, PA would synthesize this with its own analysis
                final_response = f"Based on my analysis and shoe expertise: {shoes_response}"
            else:
                final_response = response
            
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Collect metrics
            pa_metrics = self.pa_agent.get_session_metrics()
            shoes_metrics = self.shoes_agent.get_session_metrics()
            
            return WorkflowTestResult(
                test_id=test_id,
                query=query,
                approach="standard_workflow",
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                pa_total_tokens=pa_metrics["total_tokens"],
                pa_api_calls=pa_metrics["total_api_calls"],
                pa_search_time_ms=0,  # Would need to track this separately
                kpath_results_count=0,  # Would need to extract from PA metrics
                kpath_search_mode="tools_only",
                shoes_total_tokens=shoes_metrics["total_tokens"],
                shoes_api_calls=shoes_metrics["total_api_calls"],
                total_tokens=pa_metrics["total_tokens"] + shoes_metrics["total_tokens"],
                total_api_calls=pa_metrics["total_api_calls"] + shoes_metrics["total_api_calls"],
                success=True,
                response_preview=final_response[:200],
                error_message=""
            )
            
        except Exception as e:
            logger.error(f"❌ Standard workflow failed: {str(e)}")
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return WorkflowTestResult(
                test_id=test_id,
                query=query,
                approach="standard_workflow",
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                pa_total_tokens=0,
                pa_api_calls=0,
                pa_search_time_ms=0,
                kpath_results_count=0,
                kpath_search_mode="tools_only",
                shoes_total_tokens=0,
                shoes_api_calls=0,
                total_tokens=0,
                total_api_calls=0,
                success=False,
                response_preview="",
                error_message=str(e)
            )
