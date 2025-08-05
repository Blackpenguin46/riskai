#!/usr/bin/env python3
"""
RiskAI Chatbot API
General AI consultation and planning assistance
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import openai
import os

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    context: Optional[str] = None  # Optional context about user's business/situation

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

@router.post("/chatbot/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    General AI chat endpoint for planning, consultation, and cybersecurity advice
    """
    try:
        # Build conversation context
        system_prompt = """You are a cybersecurity expert AI assistant for RiskAI. You help users with:
        
        1. Cybersecurity planning and strategy
        2. Risk assessment guidance
        3. Security implementation advice
        4. Compliance and regulatory questions
        5. Incident response planning
        6. General cybersecurity consultation
        
        You provide practical, actionable advice tailored to the user's business context.
        Keep responses professional but conversational, and always consider the user's industry and company size when giving advice.
        
        If the user asks about their risk assessment results, guide them to use the assessment tool for detailed analysis."""
        
        # Add business context if provided
        if request.context:
            system_prompt += f"\n\nUser's business context: {request.context}"
        
        # Build message history for OpenAI
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in request.conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user", 
            "content": request.message
        })
        
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Return a helpful response without AI if no API key
            response_text = """I'm here to help with cybersecurity planning and consultation! However, the AI service is currently unavailable. 
            
Here are some general cybersecurity planning areas I can help with once the service is restored:

• **Risk Assessment Planning** - Identifying and prioritizing security risks
• **Security Framework Implementation** - NIST, ISO 27001, CIS Controls
• **Incident Response Planning** - Preparing for and responding to security incidents  
• **Compliance Guidance** - GDPR, HIPAA, SOC 2, PCI DSS requirements
• **Security Architecture** - Designing secure systems and networks
• **Employee Training Programs** - Building security awareness

Please ensure your OpenAI API key is configured to enable full AI consultation features."""
        else:
            try:
                # Make OpenAI API call using updated client
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                
                completion = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                response_text = completion.choices[0].message.content
            except Exception as ai_error:
                logger.error(f"OpenAI API error: {str(ai_error)}")
                response_text = f"""I'm experiencing technical difficulties connecting to the AI service. 

**Current Issue:** {str(ai_error)}

**Common Solutions:**
• Verify your OpenAI API key is valid and has sufficient credits
• Check your internet connection
• Ensure the OpenAI service is not experiencing outages

**In the meantime, here are some cybersecurity best practices:**
• Implement multi-factor authentication (MFA) across all systems
• Regular security assessments and vulnerability scanning
• Employee training on phishing and social engineering
• Incident response plan development and testing
• Data backup and recovery procedures

I'll be fully functional once the AI service connection is restored."""
        
        # Generate conversation ID
        conversation_id = f"chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@router.get("/chatbot/suggestions")
async def get_chat_suggestions():
    """
    Get suggested conversation starters for the chatbot
    """
    return {
        "suggestions": [
            "Help me create a cybersecurity plan for my small business",
            "What are the most important security controls to implement first?", 
            "How do I prepare for a security audit?",
            "What should be in my incident response plan?",
            "How can I improve employee security awareness?",
            "What compliance requirements do I need to consider?",
            "How do I assess third-party vendor security?",
            "What backup and disaster recovery strategy should I use?"
        ]
    }

@router.post("/chatbot/context")
async def save_user_context(context: Dict[str, Any]):
    """
    Save user business context for better chatbot responses
    """
    try:
        # In a production system, this would save to a database
        # For now, just return success
        return {
            "status": "success",
            "message": "Business context saved for improved consultation",
            "context_id": f"ctx_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        }
    except Exception as e:
        logger.error(f"Error saving context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Context save error: {str(e)}")