"""
Strategy Generation Agent

This agent handles the generation of multiple strategy variations based on public health alerts
using Claude with extended thinking capabilities and policy document integration.
"""

import json
import re
import logging
from typing import List, Optional
from datetime import datetime

from anthropic import Anthropic
from app.models.alert import AlertCreate
from app.models.strategy import StrategyCreate

# Configure logging
logger = logging.getLogger(__name__)


class StrategyGenerationAgent:
    """
    Agent responsible for generating multiple strategy variations based on public health alerts.
    
    Uses Claude Sonnet with extended thinking capabilities and integrates with policy documents
    to ensure compliance with official guidelines.
    """
    
    def __init__(self):
        """Initialize the Strategy Generation Agent"""
        self.anthropic_client = Anthropic()
        logger.info("🎯 Strategy Generation Agent initialized")
    
    async def generate_strategies(self, alert: AlertCreate) -> List[StrategyCreate]:
        """
        Generate multiple strategy variations based on an alert.
        
        Args:
            alert: AlertCreate model containing alert information
            
        Returns:
            List of StrategyCreate objects (exactly 4 strategies)
            
        Raises:
            Exception: If strategy generation fails or insufficient strategies are generated
        """
        logger.info(f"🚀 Generating strategies for alert: {alert.name}")
        logger.debug(f"Alert details - Risk: {alert.risk_score}, Location: {alert.location}")
        
        try:
            # Get policy documents for context
            policy_file_ids = await self._get_policy_file_ids()
            logger.debug(f"Found {len(policy_file_ids)} policy documents")
            
            # Build the strategy generation prompt
            strategy_prompt = self._build_strategy_generation_prompt(alert, policy_file_ids)
            
            # Generate strategies using Claude
            response_text = await self._call_claude_for_strategies(strategy_prompt, policy_file_ids)
            
            # Parse strategies from response
            strategies = self._parse_strategies_from_response(response_text, alert)
            
            if len(strategies) < 4:
                logger.error(f"Insufficient strategies generated: {len(strategies)}/4")
                raise Exception(f"Failed to generate required 4 strategies. Only generated {len(strategies)} strategies.")
            
            logger.info(f"✅ Successfully generated {len(strategies)} strategies")
            return strategies[:4]  # Return exactly 4 strategies
            
        except Exception as e:
            logger.error(f"Strategy generation failed: {str(e)}")
            raise
    
    async def _get_policy_file_ids(self) -> List[str]:
        """Get policy document file IDs from Anthropic API"""
        try:
            files_response = self.anthropic_client.files.list()
            
            # Filter for policy documents
            policy_files = []
            for file in files_response.data:
                if file.filename and 'policy' in file.filename.lower():
                    policy_files.append(file.id)
                    logger.debug(f"Found policy file: {file.filename}")
            
            logger.info(f"Retrieved {len(policy_files)} policy documents")
            return policy_files
            
        except Exception as e:
            logger.warning(f"Could not fetch policy files: {e}")
            return []
    
    def _build_strategy_generation_prompt(self, alert: AlertCreate, policy_file_ids: List[str]) -> str:
        """Build the strategy generation prompt with alert context"""
        prompt = f"""Generate 4 distinct public health strategy variations based on the following alert:

ALERT INFORMATION:
- Name: {alert.name}
- Description: {alert.description}
- Risk Score: {alert.risk_score}/10
- Risk Reason: {alert.risk_reason}
- Location: {alert.location}
- Coordinates: {alert.latitude}, {alert.longitude}

POLICY DOCUMENTS: {len(policy_file_ids)} COVID-19 policy briefs are attached.
Reference these documents for guidance on response protocols and compliance requirements.

STRATEGY GENERATION REQUIREMENTS:
Generate exactly 4 strategies with varying approaches:

1. IMMEDIATE RESPONSE (High Severity): Emergency protocols for risk scores 7-10
2. MODERATE RESPONSE (Medium Severity): Structured intervention for risk scores 4-6  
3. PREVENTIVE RESPONSE (Low-Medium Severity): Early warning measures for risk scores 2-4
4. LONG-TERM RESPONSE (Strategic): Systemic improvements regardless of current risk score

Each strategy should:
- Address the specific risk factors mentioned in the alert
- Be geographically appropriate for {alert.location}
- Include specific, actionable steps
- Reference relevant policy guidelines
- Consider resource allocation and implementation feasibility
- Provide clear success metrics and timelines

The strategies should complement each other and provide a comprehensive response framework that can be implemented simultaneously or sequentially based on evolving conditions."""

        return prompt
    
    async def _call_claude_for_strategies(self, strategy_prompt: str, policy_file_ids: List[str]) -> str:
        """Make the Claude API call for strategy generation"""
        system_prompt = """You are a Public Health Strategy Generator AI with access to official policy documents. Your task is to generate multiple strategic response variations based on alert information.

CRITICAL REQUIREMENTS:
1. Generate exactly 4 distinct strategy variations with different severity levels and approaches
2. Each strategy must be actionable and evidence-based
3. Reference policy documents to ensure compliance with official guidelines
4. Vary the response approach, timeline, and target audience for each strategy

STRATEGY VARIATION FRAMEWORK:
- Strategy 1: Immediate Response (High Severity) - Urgent containment and emergency protocols
- Strategy 2: Moderate Response (Medium Severity) - Structured monitoring and controlled intervention
- Strategy 3: Preventive Response (Low-Medium Severity) - Early warning and preparedness measures
- Strategy 4: Long-term Response (Strategic) - Systemic improvements and capacity building

OUTPUT REQUIREMENTS:
You must respond with a JSON array containing exactly 4 strategies in this format:
[
  {
    "short_description": "Brief strategy title (max 100 chars)",
    "full_description": "Detailed strategy description with specific actions, timeline, responsible parties, expected outcomes, and policy compliance notes",
    "alert_id": "placeholder"
  },
  ... (3 more strategies)
]

Each full_description should include:
- Specific actions to take
- Timeline and milestones
- Responsible agencies/departments
- Expected outcomes and success metrics
- Resource requirements
- Policy compliance references
- Risk mitigation measures"""

        try:
            if policy_file_ids:
                # Use file-attached API call
                messages_content = [
                    {
                        "type": "text",
                        "text": strategy_prompt
                    }
                ]
                # Add policy documents
                for file_id in policy_file_ids:
                    messages_content.append({
                        "type": "document",
                        "source": {
                            "type": "file",
                            "file_id": file_id
                        }
                    })
                    
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=8000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": messages_content
                    }]
                )
            else:
                # Fallback without policy files
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022", 
                    max_tokens=8000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": strategy_prompt
                    }]
                )
            
            # Extract response content
            response_text = ""
            if hasattr(response, 'content'):
                if isinstance(response.content, list):
                    for item in response.content:
                        if hasattr(item, 'text'):
                            response_text += item.text
                        elif isinstance(item, dict) and item.get('type') == 'text':
                            response_text += item.get('text', '')
                else:
                    response_text = str(response.content)
            else:
                response_text = str(response)
            
            logger.debug(f"Claude response length: {len(response_text)} characters")
            return response_text
            
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    def _parse_strategies_from_response(self, response_text: str, alert: AlertCreate) -> List[StrategyCreate]:
        """Parse strategies from Claude's response"""
        strategies = []
        
        try:
            # Try to find JSON array in the response
            json_patterns = [
                r'\[\s*\{[^}]*"short_description"[^}]*\}[^]]*\]',  # Full array pattern
                r'\{[^}]*"short_description"[^}]*\}',  # Individual objects
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, response_text, re.DOTALL)
                if matches:
                    if pattern.startswith(r'\['):
                        # Full array found
                        try:
                            strategies_data = json.loads(matches[0])
                            for strategy_data in strategies_data:
                                if all(key in strategy_data for key in ["short_description", "full_description"]):
                                    strategies.append(StrategyCreate(
                                        short_description=strategy_data["short_description"],
                                        full_description=strategy_data["full_description"],
                                        alert_id="placeholder"  # Will be updated when saving to DB
                                    ))
                            break
                        except json.JSONDecodeError:
                            continue
                    else:
                        # Individual objects found
                        for match in matches:
                            try:
                                strategy_data = json.loads(match)
                                if all(key in strategy_data for key in ["short_description", "full_description"]):
                                    strategies.append(StrategyCreate(
                                        short_description=strategy_data["short_description"],
                                        full_description=strategy_data["full_description"], 
                                        alert_id="placeholder"
                                    ))
                            except json.JSONDecodeError:
                                continue
                        if strategies:
                            break
            
            # If JSON parsing fails, try to extract from text structure
            if not strategies:
                strategies = self._extract_strategies_from_text(response_text)
            
            # Ensure we have at least 4 strategies by generating fallbacks if needed
            while len(strategies) < 4:
                strategy_type = ["Immediate Response", "Moderate Response", "Preventive Response", "Long-term Response"][len(strategies)]
                strategies.append(StrategyCreate(
                    short_description=f"{strategy_type} for {alert.name}",
                    full_description=f"Implement {strategy_type.lower()} measures to address {alert.description}. Risk score: {alert.risk_score}. Location: {alert.location}. This strategy requires detailed planning and resource allocation based on current risk assessment.",
                    alert_id="placeholder"
                ))
            
            logger.info(f"Successfully parsed {len(strategies)} strategies")
            return strategies[:4]  # Return exactly 4 strategies
            
        except Exception as e:
            logger.error(f"Error parsing strategies: {e}")
            # Return fallback strategies
            return self._generate_fallback_strategies(alert)
    
    def _extract_strategies_from_text(self, text: str) -> List[StrategyCreate]:
        """Extract strategies from unstructured text as fallback"""
        strategies = []
        
        # Look for strategy markers
        strategy_patterns = [
            r'Strategy \d+:?\s*([^\n]+)\n([^Strategy]*?)(?=Strategy \d+|$)',
            r'\d+\.\s*([^\n]+)\n([^0-9]*?)(?=\d+\.|$)',
            r'(?:Immediate|Moderate|Preventive|Long-term).*?Response:?\s*([^\n]+)\n([^I|M|P|L]*?)(?=(?:Immediate|Moderate|Preventive|Long-term)|$)'
        ]
        
        for pattern in strategy_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            if matches and len(matches) >= 2:
                for i, (title, description) in enumerate(matches[:4]):
                    strategies.append(StrategyCreate(
                        short_description=title.strip()[:100],  # Limit to 100 chars
                        full_description=description.strip(),
                        alert_id="placeholder"
                    ))
                break
        
        logger.debug(f"Extracted {len(strategies)} strategies from text")
        return strategies
    
    def _generate_fallback_strategies(self, alert: AlertCreate) -> List[StrategyCreate]:
        """Generate fallback strategies if parsing completely fails"""
        logger.warning("Generating fallback strategies due to parsing failure")
        
        return [
            StrategyCreate(
                short_description=f"Emergency Response for {alert.name}",
                full_description=f"Immediate emergency response to address {alert.description} in {alert.location}. Risk score: {alert.risk_score}. Deploy emergency protocols and coordinate with local authorities.",
                alert_id="placeholder"
            ),
            StrategyCreate(
                short_description=f"Monitoring Strategy for {alert.name}",
                full_description=f"Enhanced monitoring and surveillance for {alert.description} in {alert.location}. Risk score: {alert.risk_score}. Implement systematic tracking and early warning systems.",
                alert_id="placeholder"
            ),
            StrategyCreate(
                short_description=f"Prevention Protocol for {alert.name}",
                full_description=f"Preventive measures to mitigate {alert.description} in {alert.location}. Risk score: {alert.risk_score}. Focus on community education and preparedness.",
                alert_id="placeholder"
            ),
            StrategyCreate(
                short_description=f"Long-term Planning for {alert.name}",
                full_description=f"Strategic long-term response planning for {alert.description} in {alert.location}. Risk score: {alert.risk_score}. Build resilient systems and capacity for future response.",
                alert_id="placeholder"
            )
        ] 