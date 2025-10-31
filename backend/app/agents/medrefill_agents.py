"""
AI agents for MedRefills using LangChain.
Primary Agent reviews refill requests using protocol checking tools.
"""
import json
from typing import Dict
from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agents.tools import ProtocolCheckTool
from app.core.db import engine
from sqlmodel import Session


def create_primary_agent(session: Session) -> AgentExecutor:
    """
    Create the Primary Agent that reviews refill requests.
    
    Args:
        session: Database session for the ProtocolCheckTool
        
    Returns:
        Configured AgentExecutor
    """
    # Initialize the protocol check tool with database session
    protocol_tool = ProtocolCheckTool(session=session)
    
    # Initialize LLM (using Google Gemini Pro)
    import os
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        temperature=0,
        google_api_key=google_api_key,
    )
    
    # Create a prompt template for the agent using the ReAct format
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that reviews medication refill requests.
        
You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: Format your final response as JSON with:
{{
    "decision": "<Approve or Deny>",
    "reason": "<detailed reason from tool>",
    "confidence": <0-100>
}}"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the agent
    agent = create_react_agent(llm, [protocol_tool], prompt)
    
    # Create executor
    executor = AgentExecutor(
        agent=agent,
        tools=[protocol_tool],
        verbose=True,
        handle_parsing_errors=True
    )
    
    return executor


def run_ai_review(patient_mrn: str, medication_class: str) -> Dict:
    """
    Run the AI review process for a refill request.
    
    This function:
    1. Creates the Primary Agent
    2. Invokes it with a review prompt
    3. Parses the JSON response
    4. Returns the decision data
    
    Args:
        patient_mrn: Patient's Medical Record Number
        medication_class: Class of medication being refilled
        
    Returns:
        Dictionary with keys: decision, reason, confidence
    """
    with Session(engine) as session:
        # Create agent
        agent = create_primary_agent(session)
        
        # Create review prompt
        prompt = f"""Review patient {patient_mrn} for {medication_class} refill using your tools.
        
        Check all applicable protocols and provide your recommendation as JSON with decision, reason, and confidence."""
        
        # Run the agent
        try:
            result = agent.invoke({"input": prompt, "chat_history": []})
            
            # Extract the AI message from the result
            output = result.get("output", "")
            
            # Try to parse JSON from the output
            # The agent might return JSON wrapped in markdown or plain text
            import re
            json_match = re.search(r'\{[^{}]*"decision"[^{}]*\}', output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                decision_data = json.loads(json_str)
            else:
                # Fallback: try to parse the entire output as JSON
                try:
                    decision_data = json.loads(output)
                except:
                    # Last resort: create a basic response
                    decision_data = {
                        "decision": "Deny",
                        "reason": "Unable to parse agent response",
                        "confidence": 0
                    }
            
            return {
                "decision": decision_data.get("decision", "Deny"),
                "reason": decision_data.get("reason", "No reason provided"),
                "confidence": float(decision_data.get("confidence", 75))
            }
            
        except Exception as e:
            # Return error response
            return {
                "decision": "Deny",
                "reason": f"Error during AI review: {str(e)}",
                "confidence": 0
            }

