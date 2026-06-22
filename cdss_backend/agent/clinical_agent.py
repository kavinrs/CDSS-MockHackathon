"""
Clinical AI Agent using LangChain with simple tool calling.
Simple and reliable implementation for academic presentation.
"""

import json
import os
from typing import Dict, List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnablePassthrough

from .tools import ALL_TOOLS


# Load environment variables from .env file
load_dotenv()


# System prompt for clinical decision support
SYSTEM_MESSAGE = """You are a Clinical Decision Support AI Assistant for doctors.

CRITICAL RULES:
1. You MUST use tools to gather information - NEVER guess or make up data
2. You MUST call tools in this order:
   - First: PatientDataTool to get patient information
   - Second: PredictionTool to get risk assessments
   - Third: KnowledgeTool to get evidence-based guidelines
   - Finally: FinalAnswerTool to provide recommendations

3. Your final answer MUST include ALL of the following sections:
   - PATIENT SUMMARY: Demographics and medical history
   - RISK ASSESSMENT: Explain risk scores and SHAP feature importance
   - CLINICAL RECOMMENDATIONS: Evidence-based suggestions citing guidelines
   - NEXT ACTIONS: Specific steps for the doctor
   - DISCLAIMER: "These are AI-generated recommendations for decision support. The doctor retains final clinical decision-making authority."

4. When you receive guideline information, cite the sources
5. Be thorough but concise - doctors need actionable information
6. Use medical terminology appropriately

Remember: You are providing DECISION SUPPORT, not making decisions. The doctor has final authority."""


class ClinicalAgent:
    """
    Clinical decision support agent using LangChain tool calling.
    Simple implementation for easy understanding during viva.
    """
    
    def __init__(self, max_iterations: int = 10):
        """
        Initialize the clinical AI agent.
        
        Args:
            max_iterations: Maximum number of tool calls allowed (default: 10)
        """
        self.max_iterations = max_iterations
        
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please ensure .env file exists and contains OPENAI_API_KEY=sk-..."
            )
        
        # Initialize OpenAI LLM with tool binding
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Cost-effective for academic project
            temperature=0,  # Deterministic responses
            api_key=api_key
        ).bind_tools(ALL_TOOLS)
        
        # Create tool name to function mapping
        self.tool_map = {tool.name: tool.func for tool in ALL_TOOLS}
    
    def invoke(self, query: str) -> Dict:
        """
        Execute the agent with a clinical query.
        
        Args:
            query: Clinical question or request (e.g., "Provide recommendations for patient 3")
            
        Returns:
            Dictionary with 'output' (final answer) and 'steps' (tool calls made)
        """
        print(f"\n{'='*70}")
        print(f"Clinical Agent Processing Query")
        print(f"{'='*70}")
        print(f"Query: {query}\n")
        
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": query}
        ]
        
        steps = []
        iterations = 0
        
        while iterations < self.max_iterations:
            iterations += 1
            
            # Call LLM
            response = self.llm.invoke(messages)
            
            # Check if there are tool calls
            if not response.tool_calls:
                # No tool calls - agent provided final answer
                final_output = response.content
                print(f"\n{'='*70}")
                print("Agent Execution Complete - No more tool calls")
                print(f"{'='*70}\n")
                break
            
            # Add the AIMessage with tool_calls ONCE (before processing tools)
            messages.append({
                "role": "assistant", 
                "content": response.content or "", 
                "tool_calls": response.tool_calls
            })
            
            # Process each tool call and add ToolMessages
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                tool_call_id = tool_call['id']
                
                print(f"Step {iterations}: Calling {tool_name}")
                print(f"  Arguments: {tool_args}")
                
                # Execute the tool
                try:
                    tool_result = self.tool_map[tool_name](**tool_args)
                    print(f"  Result: {str(tool_result)[:100]}...")
                except Exception as e:
                    tool_result = f"Error: {str(e)}"
                    print(f"  Error: {str(e)}")
                
                # Store step
                steps.append({
                    "tool": tool_name,
                    "tool_input": tool_args,
                    "observation": str(tool_result)
                })
                
                # Add ToolMessage for this specific tool_call_id
                messages.append({
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_call_id
                })
                
                # Check if this was the final answer tool
                if tool_name == "FinalAnswerTool":
                    final_output = tool_result
                    print(f"\n{'='*70}")
                    print("Final Answer Received")
                    print(f"{'='*70}\n")
                    return {
                        "output": final_output,
                        "steps": steps
                    }
        
        # If we get here, we hit max iterations
        final_output = "Unable to generate complete recommendation within iteration limit."
        print(f"\n{'='*70}")
        print("Max Iterations Reached")
        print(f"{'='*70}\n")
        
        return {
            "output": final_output,
            "steps": steps
        }
    
    def clear_history(self):
        """Clear the chat history (not implemented in this simple version)."""
        print("Note: This simple agent implementation does not maintain chat history.")
