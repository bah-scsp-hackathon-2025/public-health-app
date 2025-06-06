"""
Strategy Generation Agent

This agent handles the generation of multiple strategy variations based on public health alerts
using Claude Sonnet 4 with extended thinking capabilities, LangChain, and policy document integration.
"""

import json
import re
import logging
import os
from typing import List, Optional
from datetime import datetime

from anthropic import Anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from app.models.alert import AlertCreate
from app.models.strategy import StrategyCreate

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Langfuse
langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)


class StrategyGenerationAgent:
    """
    Agent responsible for generating multiple strategy variations based on public health alerts.

    Uses Claude Sonnet 4 with extended thinking capabilities via LangChain and integrates with
    policy documents to ensure compliance with official guidelines. Includes Langfuse tracing.
    """

    def __init__(self):
        """Initialize the Strategy Generation Agent"""
        # Initialize Anthropic client for file operations only
        self.anthropic_client = Anthropic()

        # Initialize LangChain ChatAnthropic with Claude Sonnet 4 and file beta
        self.chat_anthropic = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            temperature=1.0,  # Must be 1.0 when thinking is enabled
            thinking={"type": "enabled", "budget_tokens": 4000},
            betas=["files-api-2025-04-14"],
        )

        # Initialize Langfuse callback handler
        try:
            langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

            if langfuse_secret_key and langfuse_public_key:
                self.langfuse_handler = CallbackHandler(
                    secret_key=langfuse_secret_key,
                    public_key=langfuse_public_key,
                    host=langfuse_host,
                    session_id=f"strategy-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    user_id="strategy-generation-system",
                    metadata={
                        "agent_type": "strategy_generation",
                        "project": "public-health-strategies",
                        "environment": "production",
                    },
                )
                logger.info("✅ Langfuse tracing enabled for strategy generation")
            else:
                self.langfuse_handler = None
                logger.info("ℹ️  Langfuse tracing disabled (missing keys)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup Langfuse tracing: {str(e)}")
            self.langfuse_handler = None

        logger.info("🎯 Strategy Generation Agent initialized with Claude Sonnet 4 + LangChain + Langfuse")

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

        # Note: Langfuse tracing is handled by the LangChain callback in _call_claude_for_strategies

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
                error_msg = f"Failed to generate required 4 strategies. Only generated {len(strategies)} strategies."
                logger.error(f"Insufficient strategies generated: {len(strategies)}/4")
                raise Exception(error_msg)

            logger.info(f"✅ Successfully generated {len(strategies)} strategies with LangChain + Langfuse")
            return strategies[:4]  # Return exactly 4 strategies

        except Exception as e:
            logger.error(f"Strategy generation failed: {str(e)}")
            raise

    async def _get_policy_file_ids(self) -> List[str]:
        """Get policy and strategy document file IDs from Anthropic API"""
        try:
            files_response = self.anthropic_client.beta.files.list()

            # Filter for policy and strategy documents
            policy_files = []
            strategy_files = []

            for file in files_response.data:
                if file.filename:
                    filename_lower = file.filename.lower()
                    if "policy" in filename_lower:
                        policy_files.append(file.id)
                        logger.debug(f"Found policy file: {file.filename}")
                    elif any(
                        pattern in filename_lower
                        for pattern in ["strategy", "paho", "who", "epidemic", "outbreak", "preparedness", "response"]
                    ):
                        # Skip MARSH document as it's very large (3.1 MB) and causes token limits
                        if "marsh" not in filename_lower:
                            strategy_files.append(file.id)
                            logger.debug(f"Found strategy file: {file.filename}")
                        else:
                            logger.debug(f"Skipping large MARSH document: {file.filename}")

            # Combine both types of documents
            all_document_files = policy_files + strategy_files

            logger.info(f"Retrieved {len(policy_files)} policy documents and {len(strategy_files)} strategy documents")
            logger.info(f"Total documents available for strategy generation: {len(all_document_files)}")

            return all_document_files

        except Exception as e:
            logger.warning(f"Could not fetch document files: {e}")
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

REFERENCE DOCUMENTS: {len(policy_file_ids)} policy and strategy documents are attached.
Reference these documents for guidance on response protocols, evidence-based strategies, and compliance requirements.

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
        """Make the Claude API call for strategy generation using LangChain with file attachments and Langfuse"""
        from langchain_core.messages import SystemMessage, HumanMessage

        system_prompt = """You are a Public Health Strategy Generator AI with access to official policy and strategy documents. Your task is to generate multiple strategic response variations based on alert information.

Take time to think through each strategy carefully, considering the specific context and requirements.

CRITICAL REQUIREMENTS:
1. Generate exactly 4 distinct strategy variations with different severity levels and approaches
2. Each strategy must be actionable and evidence-based
3. Reference policy and strategy documents to ensure compliance with official guidelines and proven methodologies
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
            logger.info(f"🤖 Generating strategies with Claude Sonnet 4 (documents: {len(policy_file_ids)})")

            # Create messages
            system_msg = SystemMessage(content=system_prompt)

            if policy_file_ids:
                # Build content list with text and document attachments (like the ReAct agent)
                content = [{"type": "text", "text": strategy_prompt}]

                # Add each policy/strategy document
                for file_id in policy_file_ids:
                    content.append({"type": "document", "source": {"type": "file", "file_id": file_id}})

                # Create HumanMessage with file content structure
                human_msg = HumanMessage(content=content)
                logger.debug(f"📎 Attached {len(policy_file_ids)} documents to message")
            else:
                # Simple text message without documents
                human_msg = HumanMessage(content=strategy_prompt)

            messages = [system_msg, human_msg]

            # Prepare config with Langfuse callback if available
            config = {}
            if self.langfuse_handler:
                config["callbacks"] = [self.langfuse_handler]
                logger.debug("📊 Langfuse tracing enabled for this call")

            # Invoke LangChain ChatAnthropic with thinking mode and file attachments
            response = await self.chat_anthropic.ainvoke(messages, config=config)

            response_text = response.content
            logger.debug(f"Claude response length: {len(response_text)} characters")
            logger.info("✅ Strategy generation completed with LangChain + Langfuse")

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
                    if pattern.startswith(r"\["):
                        # Full array found
                        try:
                            strategies_data = json.loads(matches[0])
                            for strategy_data in strategies_data:
                                if all(key in strategy_data for key in ["short_description", "full_description"]):
                                    strategies.append(
                                        StrategyCreate(
                                            short_description=strategy_data["short_description"],
                                            full_description=strategy_data["full_description"],
                                            alert_id="placeholder",  # Will be updated when saving to DB
                                        )
                                    )
                            break
                        except json.JSONDecodeError:
                            continue
                    else:
                        # Individual objects found
                        for match in matches:
                            try:
                                strategy_data = json.loads(match)
                                if all(key in strategy_data for key in ["short_description", "full_description"]):
                                    strategies.append(
                                        StrategyCreate(
                                            short_description=strategy_data["short_description"],
                                            full_description=strategy_data["full_description"],
                                            alert_id="placeholder",
                                        )
                                    )
                            except json.JSONDecodeError:
                                continue
                        if strategies:
                            break

            # If JSON parsing fails, try to extract from text structure
            if not strategies:
                strategies = self._extract_strategies_from_text(response_text)

            # Ensure we have at least 4 strategies by generating fallbacks if needed
            while len(strategies) < 4:
                strategy_type = [
                    "Immediate Response",
                    "Moderate Response",
                    "Preventive Response",
                    "Long-term Response",
                ][len(strategies)]
                strategies.append(
                    StrategyCreate(
                        short_description=f"{strategy_type} for {alert.name}",
                        full_description=f"Implement {strategy_type.lower()} measures to address {alert.description}. Risk score: {alert.risk_score}. Location: {alert.location}. This strategy requires detailed planning and resource allocation based on current risk assessment.",
                        alert_id="placeholder",
                    )
                )

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
            r"Strategy \d+:?\s*([^\n]+)\n([^Strategy]*?)(?=Strategy \d+|$)",
            r"\d+\.\s*([^\n]+)\n([^0-9]*?)(?=\d+\.|$)",
            r"(?:Immediate|Moderate|Preventive|Long-term).*?Response:?\s*([^\n]+)\n([^I|M|P|L]*?)(?=(?:Immediate|Moderate|Preventive|Long-term)|$)",
        ]

        for pattern in strategy_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            if matches and len(matches) >= 2:
                for i, (title, description) in enumerate(matches[:4]):
                    strategies.append(
                        StrategyCreate(
                            short_description=title.strip()[:100],  # Limit to 100 chars
                            full_description=description.strip(),
                            alert_id="placeholder",
                        )
                    )
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
                alert_id="placeholder",
            ),
            StrategyCreate(
                short_description=f"Monitoring Strategy for {alert.name}",
                full_description=f"Enhanced monitoring and surveillance for {alert.description} in {alert.location}. Risk score: {alert.risk_score}. Implement systematic tracking and early warning systems.",
                alert_id="placeholder",
            ),
            StrategyCreate(
                short_description=f"Prevention Protocol for {alert.name}",
                full_description=f"Preventive measures to mitigate {alert.description} in {alert.location}. Risk score: {alert.risk_score}. Focus on community education and preparedness.",
                alert_id="placeholder",
            ),
            StrategyCreate(
                short_description=f"Long-term Planning for {alert.name}",
                full_description=f"Strategic long-term response planning for {alert.description} in {alert.location}. Risk score: {alert.risk_score}. Build resilient systems and capacity for future response.",
                alert_id="placeholder",
            ),
        ]
