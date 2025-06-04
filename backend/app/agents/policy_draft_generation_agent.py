"""
Policy Draft Generation Agent

This agent handles the generation of policy drafts based on public health strategies and alerts
using Claude Sonnet 4 with extended thinking capabilities, LangChain, and document integration.
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
from app.models.policy import PolicyCreate

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Langfuse
langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)


class PolicyDraftGenerationAgent:
    """
    Agent responsible for generating policy drafts based on public health strategies and alerts.
    
    Uses Claude Sonnet 4 with extended thinking capabilities via LangChain and integrates with 
    policy documents to ensure compliance with official guidelines. Includes Langfuse tracing.
    """
    
    def __init__(self):
        """Initialize the Policy Draft Generation Agent"""
        # Initialize Anthropic client for file operations only
        self.anthropic_client = Anthropic()
        
        # Initialize LangChain ChatAnthropic with Claude Sonnet 4 and file beta
        self.chat_anthropic = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            temperature=1.0,  # Must be 1.0 when thinking is enabled
            thinking={"type": "enabled", "budget_tokens": 4000},
            betas=["files-api-2025-04-14"]
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
                    session_id=f"policy-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    user_id="policy-generation-system",
                    metadata={
                        "agent_type": "policy_draft_generation",
                        "project": "public-health-policies",
                        "environment": "production"
                    }
                )
                logger.info("✅ Langfuse tracing enabled for policy draft generation")
            else:
                self.langfuse_handler = None
                logger.info("ℹ️  Langfuse tracing disabled (missing keys)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup Langfuse tracing: {str(e)}")
            self.langfuse_handler = None
        
        logger.info("📝 Policy Draft Generation Agent initialized with Claude Sonnet 4 + LangChain + Langfuse")
    
    async def generate_policy_draft(self, strategy: StrategyCreate, alert: AlertCreate, author: str = "AI Policy Generator") -> PolicyCreate:
        """
        Generate a policy draft based on a strategy and its corresponding alert.
        
        Args:
            strategy: StrategyCreate model containing strategy information
            alert: AlertCreate model containing the original alert information
            author: Author name for the policy (defaults to "AI Policy Generator")
            
        Returns:
            PolicyCreate object containing the policy draft
            
        Raises:
            Exception: If policy draft generation fails
        """
        logger.info(f"📝 Generating policy draft for strategy: {strategy.short_description}")
        logger.debug(f"Strategy details - Alert ID: {strategy.alert_id}")
        logger.debug(f"Alert details - Risk: {alert.risk_score}, Location: {alert.location}")
        
        try:
            # Get policy documents for context and compliance guidance
            policy_file_ids = await self._get_policy_file_ids()
            logger.debug(f"Found {len(policy_file_ids)} policy documents")
            
            # Build the policy generation prompt
            policy_prompt = self._build_policy_generation_prompt(strategy, alert, policy_file_ids)
            
            # Generate policy draft using Claude
            response_text = await self._call_claude_for_policy(policy_prompt, policy_file_ids)
            
            # Parse policy from response
            policy_draft = self._parse_policy_from_response(response_text, strategy, alert, author)
            
            logger.info(f"✅ Successfully generated policy draft with LangChain + Langfuse")
            return policy_draft
            
        except Exception as e:
            logger.error(f"Policy draft generation failed: {str(e)}")
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
                    if 'policy' in filename_lower:
                        policy_files.append(file.id)
                        logger.debug(f"Found policy file: {file.filename}")
                    elif any(pattern in filename_lower for pattern in ['strategy', 'paho', 'who', 'epidemic', 'outbreak', 'preparedness', 'response']):
                        # Skip MARSH document as it's very large (3.1 MB) and causes token limits
                        if 'marsh' not in filename_lower:
                            strategy_files.append(file.id)
                            logger.debug(f"Found strategy file: {file.filename}")
                        else:
                            logger.debug(f"Skipping large MARSH document: {file.filename}")
            
            # Combine both types of documents
            all_document_files = policy_files + strategy_files
            
            logger.info(f"Retrieved {len(policy_files)} policy documents and {len(strategy_files)} strategy documents")
            logger.info(f"Total documents available for policy generation: {len(all_document_files)}")
            
            return all_document_files
            
        except Exception as e:
            logger.warning(f"Could not fetch document files: {e}")
            return []
    
    def _build_policy_generation_prompt(self, strategy: StrategyCreate, alert: AlertCreate, policy_file_ids: List[str]) -> str:
        """Build the policy generation prompt with strategy and alert context"""
        prompt = f"""Generate a comprehensive policy draft based on the following strategy and alert information:

ORIGINAL ALERT INFORMATION:
- Name: {alert.name}
- Description: {alert.description}
- Risk Score: {alert.risk_score}/10
- Risk Reason: {alert.risk_reason}
- Location: {alert.location}
- Coordinates: {alert.latitude}, {alert.longitude}

STRATEGY BEING IMPLEMENTED:
- Strategy ID: {strategy.alert_id}
- Short Description: {strategy.short_description}
- Full Description: {strategy.full_description}

REFERENCE DOCUMENTS: {len(policy_file_ids)} policy and strategy documents are attached.
Reference these documents for guidance on policy structure, legal compliance, and evidence-based approaches.

POLICY DRAFT REQUIREMENTS:
Generate a comprehensive policy document that includes:

1. POLICY TITLE: Clear, specific title that reflects the strategy and alert context
2. POLICY CONTENT: Detailed policy document with the following sections:
   - Executive Summary
   - Background and Rationale (referencing the alert and strategy)
   - Policy Objectives
   - Scope and Applicability
   - Policy Provisions and Requirements
   - Implementation Guidelines
   - Roles and Responsibilities
   - Monitoring and Evaluation
   - Compliance and Enforcement
   - Review and Amendment Process

The policy should:
- Be legally sound and implementable for {alert.location}
- Reference the specific strategy being implemented
- Address the original alert's risk factors
- Include specific, actionable requirements
- Reference relevant existing policies and guidelines from the attached documents
- Be appropriate for the risk level ({alert.risk_score}/10)
- Include clear timelines and accountability measures
- Consider resource requirements and implementation feasibility
- Provide measurable outcomes and success criteria

Format the response as a formal policy document suitable for governmental or organizational adoption."""

        return prompt
    
    async def _call_claude_for_policy(self, policy_prompt: str, policy_file_ids: List[str]) -> str:
        """Make the Claude API call for policy generation using LangChain with file attachments and Langfuse"""
        
        if policy_file_ids:
            logger.info(f"🤖 Generating policy with Claude Sonnet 4 (documents: {len(policy_file_ids)})")
            
            # Create document attachments
            document_attachments = []
            for file_id in policy_file_ids:
                document_attachments.append({
                    "type": "document",
                    "source": {"type": "file", "file_id": file_id}
                })
            
            # Create message with text and document attachments
            message_content = [{"type": "text", "text": policy_prompt}] + document_attachments
            
            logger.debug(f"📎 Attached {len(document_attachments)} documents to message")
            
            # Build messages
            messages = [HumanMessage(content=message_content)]
            
            # Add system message
            system_message = SystemMessage(content="""You are a Public Health Policy Draft Generator AI with access to official policy and strategy documents. Your task is to generate comprehensive policy drafts based on strategy and alert information.

Take time to think through the policy structure carefully, considering legal requirements, implementation feasibility, and compliance with existing frameworks.

CRITICAL REQUIREMENTS:
1. Generate a comprehensive, implementable policy document
2. Reference both the original alert and the strategy being implemented
3. Use the attached policy and strategy documents to ensure compliance with official guidelines
4. Structure the policy according to standard governmental/organizational policy formats
5. Include specific, actionable provisions and implementation guidelines

POLICY STRUCTURE REQUIREMENTS:
- Use formal policy language and structure
- Include all required sections (Executive Summary, Background, Objectives, etc.)
- Reference specific sections from attached documents when relevant
- Provide clear implementation timelines and responsibilities
- Include measurable outcomes and compliance mechanisms

OUTPUT REQUIREMENTS:
You must respond with a comprehensive policy document in formal policy format. The content should be detailed, professional, and ready for governmental or organizational review and adoption.""")
            
            # Prepare Langfuse config if available
            config = {}
            if self.langfuse_handler:
                config["callbacks"] = [self.langfuse_handler]
                logger.debug("📊 Langfuse tracing enabled for this call")
            
            # Make the LangChain call with document attachments
            try:
                response = await self.chat_anthropic.ainvoke(
                    [system_message] + messages,
                    config=config
                )
                response_text = response.content
                logger.debug(f"Claude response length: {len(response_text)} characters")
                logger.info("✅ Policy generation completed with LangChain + Langfuse")
                return response_text
            except Exception as e:
                logger.error(f"❌ Claude API call failed: {e}")
                raise
        else:
            # No documents available - use LangChain without file attachments
            logger.info("🤖 Generating policy with Claude Sonnet 4 (no documents)")
            
            # Build messages
            messages = [HumanMessage(content=policy_prompt)]
            
            # Add system message
            system_message = SystemMessage(content="""You are a Public Health Policy Draft Generator AI. Generate comprehensive policy drafts based on strategy and alert information.

CRITICAL REQUIREMENTS:
1. Generate a comprehensive, implementable policy document
2. Reference both the original alert and the strategy being implemented
3. Structure the policy according to standard governmental/organizational policy formats
4. Include specific, actionable provisions and implementation guidelines

OUTPUT REQUIREMENTS:
Respond with a comprehensive policy document in formal policy format.""")
            
            # Prepare Langfuse config if available
            config = {}
            if self.langfuse_handler:
                config["callbacks"] = [self.langfuse_handler]
                logger.debug("📊 Langfuse tracing enabled for this call")
            
            try:
                response = await self.chat_anthropic.ainvoke(
                    [system_message] + messages,
                    config=config
                )
                response_text = response.content
                logger.debug(f"Claude response length: {len(response_text)} characters")
                logger.info("✅ Policy generation completed with LangChain + Langfuse")
                return response_text
            except Exception as e:
                logger.error(f"❌ Claude API call failed: {e}")
                raise
    
    def _parse_policy_from_response(self, response_text: str, strategy: StrategyCreate, alert: AlertCreate, author: str) -> PolicyCreate:
        """Parse policy information from Claude's response"""
        try:
            # Extract policy title from the response
            title = self._extract_policy_title(response_text, strategy, alert)
            
            # The content is the full response (Claude generates a complete policy document)
            content = response_text.strip()
            
            # Create PolicyCreate object
            policy_draft = PolicyCreate(
                title=title,
                content=content,
                author=author,
                approved=False,  # Draft policies start as unapproved
                alert_id=strategy.alert_id,
                strategy_id=strategy.alert_id  # Using alert_id as strategy identifier since Strategy model doesn't have id in StrategyCreate
            )
            
            logger.debug(f"Generated policy: {title}")
            return policy_draft
            
        except Exception as e:
            logger.error(f"Error parsing policy from response: {e}")
            # Generate fallback policy
            return self._generate_fallback_policy(strategy, alert, author)
    
    def _extract_policy_title(self, response_text: str, strategy: StrategyCreate, alert: AlertCreate) -> str:
        """Extract policy title from the response text"""
        try:
            # Look for common policy title patterns
            title_patterns = [
                r"^#\s*(.+?)$",  # Markdown header
                r"^\*\*(.+?)\*\*$",  # Bold text
                r"^POLICY TITLE:\s*(.+?)$",  # Explicit title label
                r"^Title:\s*(.+?)$",  # Title label
                r"^(.+?)\s*POLICY$",  # Text ending with POLICY
                r"^(.+?)\s*Policy$",  # Text ending with Policy
            ]
            
            lines = response_text.split('\n')
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if not line:
                    continue
                    
                for pattern in title_patterns:
                    match = re.match(pattern, line, re.IGNORECASE | re.MULTILINE)
                    if match:
                        title = match.group(1).strip()
                        # Clean up the title
                        title = re.sub(r'[#*]+', '', title).strip()
                        if len(title) > 10 and len(title) < 200:  # Reasonable title length
                            return title
            
            # If no title found, generate one based on strategy and alert
            return f"Policy for {strategy.short_description} - {alert.location}"
            
        except Exception as e:
            logger.warning(f"Could not extract title: {e}")
            return f"Policy Draft for {alert.name}"
    
    def _generate_fallback_policy(self, strategy: StrategyCreate, alert: AlertCreate, author: str) -> PolicyCreate:
        """Generate a fallback policy if parsing fails"""
        logger.warning("Generating fallback policy due to parsing failure")
        
        title = f"Policy Draft for {strategy.short_description}"
        
        content = f"""POLICY DRAFT

TITLE: {title}

BACKGROUND:
This policy draft was generated in response to the alert "{alert.name}" (Risk Score: {alert.risk_score}/10) in {alert.location}.

STRATEGY IMPLEMENTATION:
This policy implements the strategy: {strategy.short_description}

STRATEGY DETAILS:
{strategy.full_description}

ALERT CONTEXT:
- Alert: {alert.name}
- Risk Score: {alert.risk_score}/10
- Location: {alert.location}
- Risk Reason: {alert.risk_reason}
- Alert Description: {alert.description}

POLICY PROVISIONS:
1. Immediate implementation of the strategy outlined above
2. Coordination with relevant agencies and departments
3. Regular monitoring and evaluation of implementation progress
4. Compliance with existing public health guidelines and regulations

IMPLEMENTATION TIMELINE:
- Immediate: Policy review and approval process
- Short-term (1-4 weeks): Initial strategy implementation
- Medium-term (1-3 months): Full strategy deployment and monitoring
- Long-term (3+ months): Evaluation and policy refinement

RESPONSIBLE PARTIES:
- Public Health Authorities
- Emergency Management Agencies
- Healthcare Providers
- Local Government Officials

REVIEW AND AMENDMENT:
This policy shall be reviewed quarterly and amended as necessary based on evolving conditions and implementation outcomes.

Generated: {datetime.now().isoformat()}
Author: {author}
"""
        
        return PolicyCreate(
            title=title,
            content=content,
            author=author,
            approved=False,
            alert_id=strategy.alert_id,
            strategy_id=strategy.alert_id
        ) 