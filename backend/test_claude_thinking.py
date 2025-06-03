#!/usr/bin/env python3
"""
Test script to verify Claude 4.0 Sonnet with thinking mode configuration
"""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))

def test_claude_thinking_mode():
    """Test Claude thinking mode configuration"""
    print("🧪 Testing Claude 4.0 Sonnet with Thinking Mode Configuration")
    print("=" * 70)
    
    try:
        # Test standard agent
        print("\n1. Testing Standard Dashboard Agent...")
        from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
        
        try:
            agent1 = PublicHealthDashboardAgent(llm_provider='anthropic')
            if agent1.llm:
                print(f"✅ Standard Agent Created Successfully")
                print(f"   Model: {agent1.llm.model}")
                print(f"   Temperature: {agent1.llm.temperature}")
                
                # Check for thinking mode configuration
                if hasattr(agent1.llm, 'thinking') and agent1.llm.thinking:
                    print(f"   Thinking Mode: ✅ Enabled (Direct)")
                    print(f"   Thinking Config: {agent1.llm.thinking}")
                elif hasattr(agent1.llm, 'extra_headers') and agent1.llm.extra_headers:
                    thinking_enabled = "anthropic-beta" in agent1.llm.extra_headers
                    print(f"   Thinking Mode: {'✅ Enabled (Beta)' if thinking_enabled else '❌ Disabled'}")
                    if thinking_enabled:
                        print(f"   Beta Header: {agent1.llm.extra_headers['anthropic-beta']}")
                else:
                    print("   Thinking Mode: ❌ Not configured")
            else:
                print("⚠️ No LLM configured (likely missing API key)")
                
        except Exception as e:
            print(f"❌ Standard Agent Error: {str(e)}")
        
        # Test ReAct agent
        print("\n2. Testing ReAct Dashboard Agent...")
        from app.agents.health_dashboard_react_agent import PublicHealthReActAgent
        
        try:
            agent2 = PublicHealthReActAgent(llm_provider='anthropic')
            if agent2.llm:
                print(f"✅ ReAct Agent Created Successfully")
                print(f"   Model: {agent2.llm.model}")
                print(f"   Temperature: {agent2.llm.temperature}")
                
                # Check for thinking mode configuration
                if hasattr(agent2.llm, 'thinking') and agent2.llm.thinking:
                    print(f"   Thinking Mode: ✅ Enabled (Direct)")
                    print(f"   Thinking Config: {agent2.llm.thinking}")
                elif hasattr(agent2.llm, 'extra_headers') and agent2.llm.extra_headers:
                    thinking_enabled = "anthropic-beta" in agent2.llm.extra_headers
                    print(f"   Thinking Mode: {'✅ Enabled (Beta)' if thinking_enabled else '❌ Disabled'}")
                    if thinking_enabled:
                        print(f"   Beta Header: {agent2.llm.extra_headers['anthropic-beta']}")
                else:
                    print("   Thinking Mode: ❌ Not configured")
            else:
                print("⚠️ No LLM configured (likely missing API key)")
                
        except Exception as e:
            print(f"❌ ReAct Agent Error: {str(e)}")
        
        print("\n" + "=" * 70)
        print("🎯 Claude 4.0 Sonnet + Thinking Mode Test Complete")
        
        # Test a simple LLM call if we have an agent
        if 'agent1' in locals() and agent1.llm:
            print("\n3. Testing Simple LLM Call with Thinking Mode...")
            try:
                from langchain_core.messages import HumanMessage
                
                # Simple test message
                messages = [HumanMessage(content="What is 2+2? Think through this step by step.")]
                
                print("   Sending test message to Claude...")
                response = agent1.llm.invoke(messages)
                
                print(f"✅ LLM Response Received")
                
                # Handle the new response format with thinking
                if hasattr(response, 'content') and isinstance(response.content, list):
                    # New format with separate thinking and text blocks
                    print(f"   Response Type: Multi-block format")
                    
                    thinking_block = None
                    text_block = None
                    
                    for block in response.content:
                        if isinstance(block, dict) and block.get('type') == 'thinking':
                            thinking_block = block.get('thinking', '')
                        elif isinstance(block, dict) and block.get('type') == 'text':
                            text_block = block.get('text', '')
                    
                    if thinking_block:
                        print(f"✅ Thinking mode is working!")
                        print(f"   Thinking Length: {len(thinking_block)} characters")
                        print(f"   Thinking Preview: {thinking_block[:100]}...")
                    
                    if text_block:
                        print(f"   Final Response Length: {len(text_block)} characters")
                        print(f"   Final Response Preview: {text_block[:100]}...")
                    
                elif hasattr(response, 'content') and isinstance(response.content, str):
                    # Legacy format
                    print(f"   Response Length: {len(response.content)} characters")
                    print(f"   Response Preview: {response.content[:100]}...")
                    
                    # Check if thinking is visible in response
                    if "<thinking>" in response.content or "thinking" in response.content:
                        print("✅ Thinking mode appears to be working (thinking content detected)")
                    else:
                        print("⚠️ No obvious thinking content detected in response")
                else:
                    print(f"   Unknown response format: {type(response.content)}")
                    
            except Exception as e:
                print(f"❌ LLM Test Error: {str(e)}")
        
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("Make sure you're running from the backend directory with the virtual environment activated")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    test_claude_thinking_mode() 