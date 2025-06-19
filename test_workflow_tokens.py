#!/usr/bin/env python3
"""
Full Workflow Token Analysis: PA Agent -> KPATH -> Shoes Agent -> Function Calls -> Response

This script tests the complete workflow:
1. PA Agent receives user query
2. PA Agent searches KPATH Enterprise 
3. PA Agent selects Shoes Agent
4. PA Agent forwards request to Shoes Agent
5. Shoes Agent processes request and calls its functions
6. Shoes Agent returns results to PA Agent
7. PA Agent synthesizes final response

Measures token consumption at each step for complete workflow analysis.
"""

import asyncio
import json
import time
import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../agents'))

# Import agents
from agents.pa.pa_agent import PersonalAssistantAgent
from agents.shoes.shoes_agent import ShoesAgent
from agents.token_tracker import TokenTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    """Represents a single step in the workflow"""
    step_number: int
    step_name: str
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    response_time_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class WorkflowResult:
    """Complete workflow test result"""
    test_id: str
    scenario: str
    user_query: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tokens: int = 0
    total_response_time_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None
    steps: List[WorkflowStep] = field(default_factory=list)
    final_response: Optional[str] = None

class WorkflowTokenTester:
    """Tests the complete PA Agent -> Shoes Agent workflow"""
    
    def __init__(self):
        self.pa_agent = None
        self.shoes_agent = None
        self.results: List[WorkflowResult] = []
        
    async def initialize_agents(self):
        """Initialize both agents"""
        try:
            self.pa_agent = PersonalAssistantAgent()
            self.shoes_agent = ShoesAgent()
            logger.info("✅ Agents initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {e}")
            raise
    
    def get_test_scenarios(self) -> List[Tuple[str, str]]:
        """Get test scenarios for shoe-related queries"""
        return [
            ("Simple Product Search", "I'm looking for running shoes under $150"),
            ("Availability Check", "Do you have Nike Air Max in size 10?"),
            ("Store Location", "Where can I buy shoes near me in New York?"),
            ("Buying Advice", "What are the best running shoes for flat feet?"),
            ("Delivery Tracking", "Can you track my shoe order with tracking number TRK123456?"),
            ("Complex Query", "I need comfortable running shoes for marathon training, size 9, under $200, and want to know where to buy them in NYC"),
            ("Multi-Service Query", "Find me Nike running shoes, check if they're available in size 11, and help me find a store that sells them"),
            ("Guidance Request", "I'm new to running, what shoes should I get and how do I pick the right size?")
        ]
    
    async def run_workflow_test(self, scenario: str, user_query: str) -> WorkflowResult:
        """Run a complete workflow test"""
        test_id = f"workflow_{uuid.uuid4().hex[:8]}"
        result = WorkflowResult(
            test_id=test_id,
            scenario=scenario,
            user_query=user_query,
            start_time=datetime.now()
        )
        
        logger.info(f"🚀 Starting workflow test: {scenario}")
        logger.info(f"Query: {user_query}")
        
        try:
            # Step 1: PA Agent receives and processes initial query
            step1 = await self._step1_pa_initial_processing(test_id, user_query)
            result.steps.append(step1)
            
            if not step1.success:
                result.success = False
                result.error_message = step1.error_message
                return result
            
            # Step 2: PA Agent searches KPATH
            step2 = await self._step2_pa_kpath_search(test_id, user_query)
            result.steps.append(step2)
            
            if not step2.success:
                result.success = False
                result.error_message = step2.error_message
                return result
            
            # Step 3: PA Agent analyzes results and plans execution
            step3 = await self._step3_pa_analysis_planning(test_id, user_query, step2.details.get('search_results', {}))
            result.steps.append(step3)
            
            if not step3.success:
                result.success = False
                result.error_message = step3.error_message
                return result
            
            # Step 4: PA Agent calls Shoes Agent
            step4 = await self._step4_pa_shoes_coordination(test_id, user_query, step3.details.get('execution_plan', {}))
            result.steps.append(step4)
            
            # Step 5: Shoes Agent processes request
            step5 = await self._step5_shoes_processing(test_id, user_query)
            result.steps.append(step5)
            
            # Step 6: Shoes Agent function calls
            step6 = await self._step6_shoes_function_calls(test_id, user_query, step5.details.get('tools_to_call', []))
            result.steps.append(step6)
            
            # Step 7: PA Agent synthesizes final response
            step7 = await self._step7_pa_final_synthesis(test_id, user_query, step6.details.get('tool_results', []))
            result.steps.append(step7)
            
            # Calculate totals
            result.total_tokens = sum(step.total_tokens for step in result.steps)
            result.total_response_time_ms = sum(step.response_time_ms for step in result.steps)
            result.final_response = step7.details.get('final_response', 'No response generated')
            result.success = all(step.success for step in result.steps)
            
        except Exception as e:
            logger.error(f"❌ Workflow test failed: {e}")
            result.success = False
            result.error_message = str(e)
        finally:
            result.end_time = datetime.now()
        
        return result
    
    async def _step1_pa_initial_processing(self, test_id: str, query: str) -> WorkflowStep:
        """Step 1: PA Agent initial processing"""
        step = WorkflowStep(
            step_number=1,
            step_name="PA Agent Initial Processing",
            agent_name="PA_Agent",
            start_time=datetime.now()
        )
        
        try:
            # Simulate PA Agent initial query processing
            start_time = time.time()
            
            # Count tokens for initial processing
            input_text = f"User query: {query}"
            processing_text = f"Analyzing query: {query}. Need to search KPATH for relevant tools and services."
            
            if hasattr(self.pa_agent, 'token_tracker'):
                step.input_tokens = self.pa_agent.token_tracker.count_tokens(input_text)
                step.output_tokens = self.pa_agent.token_tracker.count_tokens(processing_text)
            else:
                step.input_tokens = len(input_text) // 4
                step.output_tokens = len(processing_text) // 4
            
            step.total_tokens = step.input_tokens + step.output_tokens
            step.response_time_ms = int((time.time() - start_time) * 1000)
            step.success = True
            
            logger.info(f"✅ Step 1 completed: {step.total_tokens} tokens, {step.response_time_ms}ms")
            
        except Exception as e:
            step.success = False
            step.error_message = str(e)
            logger.error(f"❌ Step 1 failed: {e}")
        finally:
            step.end_time = datetime.now()
        
        return step    
    async def _step2_pa_kpath_search(self, test_id: str, query: str) -> WorkflowStep:
        """Step 2: PA Agent searches KPATH"""
        step = WorkflowStep(
            step_number=2,
            step_name="PA Agent KPATH Search",
            agent_name="PA_Agent",
            start_time=datetime.now()
        )
        
        try:
            start_time = time.time()
            
            # Perform KPATH search
            search_results = await self.pa_agent.search_kpath(query)
            
            # Count tokens
            input_text = query
            output_text = json.dumps(search_results)
            
            if hasattr(self.pa_agent, 'token_tracker'):
                step.input_tokens = self.pa_agent.token_tracker.count_tokens(input_text)
                step.output_tokens = self.pa_agent.token_tracker.count_tokens(output_text)
            else:
                step.input_tokens = len(input_text) // 4
                step.output_tokens = len(output_text) // 4
            
            step.total_tokens = step.input_tokens + step.output_tokens
            step.response_time_ms = int((time.time() - start_time) * 1000)
            step.success = "error" not in search_results
            step.details = {"search_results": search_results}
            
            logger.info(f"✅ Step 2 completed: {step.total_tokens} tokens, {step.response_time_ms}ms")
            
        except Exception as e:
            step.success = False
            step.error_message = str(e)
            logger.error(f"❌ Step 2 failed: {e}")
        finally:
            step.end_time = datetime.now()
        
        return step
    
    async def _step3_pa_analysis_planning(self, test_id: str, query: str, search_results: Dict) -> WorkflowStep:
        """Step 3: PA Agent analyzes results and creates execution plan"""
        step = WorkflowStep(
            step_number=3,
            step_name="PA Agent Analysis & Planning",
            agent_name="PA_Agent",
            start_time=datetime.now()
        )
        
        try:
            start_time = time.time()
            
            # Simulate the GPT-4o analysis call that would happen in the real PA Agent
            if self.pa_agent.client:
                analysis_prompt = f"""
                User Query: "{query}"
                
                Available Tools: {json.dumps(search_results.get('results', [])[:5], indent=2)}
                
                Analyze this and create an execution plan. Focus on shoe-related services if available.
                """
                
                messages = [
                    {"role": "system", "content": self.pa_agent.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ]
                
                response = self.pa_agent.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                execution_plan = response.choices[0].message.content
                
                # Count tokens
                input_text = json.dumps(messages)
                output_text = execution_plan
                
                if hasattr(self.pa_agent, 'token_tracker'):
                    step.input_tokens = self.pa_agent.token_tracker.count_tokens(input_text)
                    step.output_tokens = self.pa_agent.token_tracker.count_tokens(output_text)
                else:
                    step.input_tokens = len(input_text) // 4
                    step.output_tokens = len(output_text) // 4
                
                step.details = {"execution_plan": execution_plan}
                step.success = True
            else:
                # Fallback without OpenAI
                execution_plan = f"Plan: Use shoes-related tools for query: {query}"
                step.input_tokens = len(query) // 4
                step.output_tokens = len(execution_plan) // 4
                step.details = {"execution_plan": execution_plan}
                step.success = True
            
            step.total_tokens = step.input_tokens + step.output_tokens
            step.response_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"✅ Step 3 completed: {step.total_tokens} tokens, {step.response_time_ms}ms")
            
        except Exception as e:
            step.success = False
            step.error_message = str(e)
            logger.error(f"❌ Step 3 failed: {e}")
        finally:
            step.end_time = datetime.now()
        
        return step
    
    async def _step4_pa_shoes_coordination(self, test_id: str, query: str, execution_plan: str) -> WorkflowStep:
        """Step 4: PA Agent coordinates with Shoes Agent"""
        step = WorkflowStep(
            step_number=4,
            step_name="PA-Shoes Coordination",
            agent_name="PA_Agent",
            start_time=datetime.now()
        )
        
        try:
            start_time = time.time()
            
            # Simulate coordination between PA and Shoes Agent
            coordination_text = f"""
            PA Agent forwarding request to Shoes Agent:
            Original Query: {query}
            Execution Plan: {execution_plan}
            Instructions: Process this shoe-related request using appropriate tools.
            """
            
            # Count tokens for coordination
            step.input_tokens = len(query + str(execution_plan)) // 4
            step.output_tokens = len(coordination_text) // 4
            step.total_tokens = step.input_tokens + step.output_tokens
            step.response_time_ms = int((time.time() - start_time) * 1000)
            step.success = True
            step.details = {"coordination_message": coordination_text}
            
            logger.info(f"✅ Step 4 completed: {step.total_tokens} tokens, {step.response_time_ms}ms")
            
        except Exception as e:
            step.success = False
            step.error_message = str(e)
            logger.error(f"❌ Step 4 failed: {e}")
        finally:
            step.end_time = datetime.now()
        
        return step    
    async def _step5_shoes_processing(self, test_id: str, query: str) -> WorkflowStep:
        """Step 5: Shoes Agent processes the request"""
        step = WorkflowStep(
            step_number=5,
            step_name="Shoes Agent Processing",
            agent_name="Shoes_Agent",
            start_time=datetime.now()
        )
        
        try:
            start_time = time.time()
            
            # Simulate Shoes Agent processing the request and determining which tools to call
            tools_to_call = []
            
            query_lower = query.lower()
            if any(word in query_lower for word in ['find', 'search', 'looking', 'show']):
                tools_to_call.append('product_search')
            if any(word in query_lower for word in ['available', 'stock', 'have']):
                tools_to_call.append('product_availability')
            if any(word in query_lower for word in ['store', 'where', 'location', 'buy']):
                tools_to_call.append('store_location_search')
            if any(word in query_lower for word in ['advice', 'recommend', 'best', 'should', 'guide']):
                tools_to_call.append('shoe_buying_guide')
            if any(word in query_lower for word in ['track', 'delivery', 'order', 'shipping']):
                tools_to_call.append('delivery_tracker')
            
            # Default to product search if no specific tool identified
            if not tools_to_call:
                tools_to_call.append('product_search')
            
            processing_text = f"Shoes Agent analyzing query: {query}. Will call tools: {', '.join(tools_to_call)}"
            
            step.input_tokens = len(query) // 4
            step.output_tokens = len(processing_text) // 4
            step.total_tokens = step.input_tokens + step.output_tokens
            step.response_time_ms = int((time.time() - start_time) * 1000)
            step.success = True
            step.details = {"tools_to_call": tools_to_call}
            
            logger.info(f"✅ Step 5 completed: {step.total_tokens} tokens, {step.response_time_ms}ms")
            logger.info(f"Tools to call: {tools_to_call}")
            
        except Exception as e:
            step.success = False
            step.error_message = str(e)
            logger.error(f"❌ Step 5 failed: {e}")
        finally:
            step.end_time = datetime.now()
        
        return step
    
    async def _step6_shoes_function_calls(self, test_id: str, query: str, tools_to_call: List[str]) -> WorkflowStep:
        """Step 6: Shoes Agent executes function calls"""
        step = WorkflowStep(
            step_number=6,
            step_name="Shoes Agent Function Calls",
            agent_name="Shoes_Agent",
            start_time=datetime.now()
        )
        
        try:
            start_time = time.time()
            tool_results = []
            total_input_tokens = 0
            total_output_tokens = 0
            
            for tool_name in tools_to_call:
                logger.info(f"🔧 Calling {tool_name}")
                
                if tool_name == "product_search":
                    result = await self.shoes_agent.product_search(query, max_price=200)
                elif tool_name == "product_availability":
                    result = await self.shoes_agent.product_availability("NK001", size="10")
                elif tool_name == "store_location_search":
                    result = await self.shoes_agent.store_location_search("New York")
                elif tool_name == "shoe_buying_guide":
                    result = await self.shoes_agent.shoe_buying_guide(question_type="selection", use_case="running")
                elif tool_name == "delivery_tracker":
                    result = await self.shoes_agent.delivery_tracker("TRK123456")
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })
                
                # Count tokens for this tool call
                input_text = f"{tool_name}: {query}"
                output_text = json.dumps(result)
                
                if hasattr(self.shoes_agent, 'token_tracker'):
                    tool_input_tokens = self.shoes_agent.token_tracker.count_tokens(input_text)
                    tool_output_tokens = self.shoes_agent.token_tracker.count_tokens(output_text)
                else:
                    tool_input_tokens = len(input_text) // 4
                    tool_output_tokens = len(output_text) // 4
                
                total_input_tokens += tool_input_tokens
                total_output_tokens += tool_output_tokens
            
            step.input_tokens = total_input_tokens
            step.output_tokens = total_output_tokens
            step.total_tokens = step.input_tokens + step.output_tokens
            step.response_time_ms = int((time.time() - start_time) * 1000)
            step.success = True
            step.details = {"tool_results": tool_results}
            
            logger.info(f"✅ Step 6 completed: {step.total_tokens} tokens, {step.response_time_ms}ms")
            
        except Exception as e:
            step.success = False
            step.error_message = str(e)
            logger.error(f"❌ Step 6 failed: {e}")
        finally:
            step.end_time = datetime.now()
        
        return step
    
    async def _step7_pa_final_synthesis(self, test_id: str, query: str, tool_results: List[Dict]) -> WorkflowStep:
        """Step 7: PA Agent synthesizes final response"""
        step = WorkflowStep(
            step_number=7,
            step_name="PA Agent Final Synthesis",
            agent_name="PA_Agent",
            start_time=datetime.now()
        )
        
        try:
            start_time = time.time()
            
            if self.pa_agent.client:
                # Use GPT-4o to synthesize final response
                synthesis_prompt = f"""
                Original User Query: "{query}"
                
                Tool Results from Shoes Agent:
                {json.dumps(tool_results, indent=2)}
                
                Please synthesize these results into a helpful, conversational response for the user.
                """
                
                messages = [
                    {"role": "system", "content": "You are a helpful assistant synthesizing tool results into a user-friendly response."},
                    {"role": "user", "content": synthesis_prompt}
                ]
                
                response = self.pa_agent.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800
                )
                
                final_response = response.choices[0].message.content
                
                # Count tokens
                input_text = json.dumps(messages)
                output_text = final_response
                
                if hasattr(self.pa_agent, 'token_tracker'):
                    step.input_tokens = self.pa_agent.token_tracker.count_tokens(input_text)
                    step.output_tokens = self.pa_agent.token_tracker.count_tokens(output_text)
                else:
                    step.input_tokens = len(input_text) // 4
                    step.output_tokens = len(output_text) // 4
            else:
                # Fallback synthesis
                final_response = f"Based on your query '{query}', I found relevant information using our shoe tools."
                step.input_tokens = len(str(tool_results)) // 4
                step.output_tokens = len(final_response) // 4
            
            step.total_tokens = step.input_tokens + step.output_tokens
            step.response_time_ms = int((time.time() - start_time) * 1000)
            step.success = True
            step.details = {"final_response": final_response}
            
            logger.info(f"✅ Step 7 completed: {step.total_tokens} tokens, {step.response_time_ms}ms")
            
        except Exception as e:
            step.success = False
            step.error_message = str(e)
            logger.error(f"❌ Step 7 failed: {e}")
        finally:
            step.end_time = datetime.now()
        
        return step    
    async def run_all_tests(self):
        """Run all workflow tests"""
        logger.info("🚀 Starting Full Workflow Token Analysis Tests")
        logger.info("=" * 80)
        
        await self.initialize_agents()
        
        scenarios = self.get_test_scenarios()
        
        for scenario, query in scenarios:
            try:
                result = await self.run_workflow_test(scenario, query)
                self.results.append(result)
                
                logger.info(f"📊 Test completed: {scenario}")
                logger.info(f"   Total tokens: {result.total_tokens}")
                logger.info(f"   Total time: {result.total_response_time_ms}ms")
                logger.info(f"   Success: {result.success}")
                logger.info("-" * 50)
                
                # Small delay between tests
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Test failed for {scenario}: {e}")
                continue
        
        await self.generate_comprehensive_report()
    
    async def generate_comprehensive_report(self):
        """Generate detailed analysis report"""
        if not self.results:
            logger.error("No results to report")
            return
        
        logger.info("📊 GENERATING COMPREHENSIVE WORKFLOW ANALYSIS REPORT")
        logger.info("=" * 80)
        
        # Calculate statistics
        successful_tests = [r for r in self.results if r.success]
        total_tokens = [r.total_tokens for r in successful_tests]
        total_times = [r.total_response_time_ms for r in successful_tests]
        
        print("\n" + "=" * 80)
        print("FULL WORKFLOW TOKEN ANALYSIS REPORT")
        print("PA Agent -> KPATH -> Shoes Agent -> Function Calls -> Response")
        print("=" * 80)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Scenarios Tested: {len(self.results)}")
        print(f"Successful Tests: {len(successful_tests)}")
        print(f"Success Rate: {len(successful_tests)/len(self.results)*100:.1f}%")
        print()
        
        # Summary statistics
        if total_tokens:
            print("OVERALL STATISTICS")
            print("-" * 40)
            print(f"Average Total Tokens: {sum(total_tokens)/len(total_tokens):.1f}")
            print(f"Min Total Tokens: {min(total_tokens)}")
            print(f"Max Total Tokens: {max(total_tokens)}")
            print(f"Average Response Time: {sum(total_times)/len(total_times):.1f}ms")
            print(f"Min Response Time: {min(total_times)}ms")
            print(f"Max Response Time: {max(total_times)}ms")
            print()
        
        # Detailed breakdown by scenario
        print("DETAILED RESULTS BY SCENARIO")
        print("-" * 80)
        print(f"{'Scenario':<25} {'Total Tokens':<15} {'Time (ms)':<12} {'Steps':<8} {'Success':<10}")
        print("-" * 80)
        
        for result in self.results:
            steps_completed = len([s for s in result.steps if s.success])
            success_status = "✅ YES" if result.success else "❌ NO"
            
            print(f"{result.scenario[:24]:<25} {result.total_tokens:<15} {result.total_response_time_ms:<12} "
                  f"{steps_completed}/7{'':<8} {success_status:<10}")
        
        print()
        
        # Step-by-step analysis
        print("STEP-BY-STEP ANALYSIS (Successful Tests)")
        print("-" * 80)
        
        step_names = [
            "PA Initial Processing",
            "PA KPATH Search", 
            "PA Analysis & Planning",
            "PA-Shoes Coordination",
            "Shoes Processing",
            "Shoes Function Calls",
            "PA Final Synthesis"
        ]
        
        step_stats = {}
        for i in range(7):
            step_tokens = []
            step_times = []
            
            for result in successful_tests:
                if i < len(result.steps) and result.steps[i].success:
                    step_tokens.append(result.steps[i].total_tokens)
                    step_times.append(result.steps[i].response_time_ms)
            
            if step_tokens:
                step_stats[i] = {
                    "avg_tokens": sum(step_tokens) / len(step_tokens),
                    "avg_time": sum(step_times) / len(step_times),
                    "count": len(step_tokens)
                }
        
        print(f"{'Step':<30} {'Avg Tokens':<12} {'Avg Time (ms)':<15} {'Count':<8}")
        print("-" * 65)
        
        for i, stats in step_stats.items():
            step_name = step_names[i] if i < len(step_names) else f"Step {i+1}"
            print(f"{step_name:<30} {stats['avg_tokens']:<12.1f} {stats['avg_time']:<15.1f} {stats['count']:<8}")
        
        print()
        
        # Token distribution analysis
        if step_stats:
            print("TOKEN DISTRIBUTION ANALYSIS")
            print("-" * 40)
            
            total_avg_tokens = sum(stats['avg_tokens'] for stats in step_stats.values())
            
            for i, stats in step_stats.items():
                step_name = step_names[i] if i < len(step_names) else f"Step {i+1}"
                percentage = (stats['avg_tokens'] / total_avg_tokens) * 100
                print(f"{step_name:<30} {percentage:>6.1f}%")
            
            print()
        
        # Cost analysis
        print("COST ANALYSIS (Estimated)")
        print("-" * 40)
        if successful_tests:
            avg_total_tokens = sum(total_tokens) / len(total_tokens)
            # Rough cost estimation (GPT-4o pricing)
            estimated_cost_per_request = (avg_total_tokens / 1_000_000) * 10  # Rough average
            print(f"Average tokens per request: {avg_total_tokens:.1f}")
            print(f"Estimated cost per request: ${estimated_cost_per_request:.6f}")
            print(f"Estimated cost per 1000 requests: ${estimated_cost_per_request * 1000:.2f}")
        
        print()
        print("=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.pa_agent and hasattr(self.pa_agent, 'http_client'):
            await self.pa_agent.http_client.aclose()

async def main():
    """Main test runner"""
    tester = WorkflowTokenTester()
    
    try:
        await tester.run_all_tests()
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
