#!/usr/bin/env python3
"""
Generate Policy Drafts from Strategies

This utility script reads the strategies.jsonl file, matches strategies with their
corresponding alerts from dashboard.json, and generates policy drafts for each
strategy-alert pair using the PolicyDraftGenerationAgent.

The script processes:
- 12 strategies from strategies.jsonl (4 strategies per alert for first 3 alerts)
- First 3 alerts from dashboard.json 
- Generates 12 policy drafts saved to policy_drafts.jsonl

Each policy draft is appended to the output file immediately after generation
for incremental progress tracking and resilience to failures.

Usage:
    python utils/generate_policy_drafts_from_strategies.py

Requirements:
    - Run from the project root directory
    - Uses the backend app's virtual environment
    - Requires strategies.jsonl and dashboard.json in documents/data/
    - Outputs policy_drafts.jsonl in documents/data/
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add the backend app to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

try:
    from app.agents.policy_draft_generation_agent import PolicyDraftGenerationAgent
    from app.models.alert import AlertCreate
    from app.models.strategy import StrategyCreate
    from app.models.policy import PolicyCreate
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
STRATEGIES_FILE = project_root / "documents" / "data" / "strategies.ndjson"
DASHBOARD_FILE = project_root / "documents" / "data" / "dashboard.json"
OUTPUT_FILE = project_root / "documents" / "data" / "policy_drafts.jsonl"

async def load_strategies() -> List[Dict[str, Any]]:
    """Load strategies from the JSONL file"""
    try:
        strategies = []
        with open(STRATEGIES_FILE, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        strategy_data = json.loads(line)
                        strategies.append(strategy_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON on line {line_num}: {e}")
                        continue
        
        logger.info(f"📊 Loaded {len(strategies)} strategies from {STRATEGIES_FILE}")
        return strategies
        
    except FileNotFoundError:
        logger.error(f"❌ Strategies file not found: {STRATEGIES_FILE}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading strategies: {e}")
        raise

async def load_alerts() -> List[Dict[str, Any]]:
    """Load alerts from the dashboard.json file"""
    try:
        with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)
        
        alerts = dashboard_data.get('alerts', [])
        
        # Take only the first 3 alerts as specified
        first_three_alerts = alerts[:3]
        
        logger.info(f"📊 Loaded {len(first_three_alerts)} alerts from {DASHBOARD_FILE}")
        return first_three_alerts
        
    except FileNotFoundError:
        logger.error(f"❌ Dashboard file not found: {DASHBOARD_FILE}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading alerts: {e}")
        raise

def match_strategies_to_alerts(strategies: List[Dict[str, Any]], alerts: List[Dict[str, Any]]) -> List[tuple]:
    """
    Match strategies to their corresponding alerts.
    Every 4 strategies belong to one alert (for first 3 alerts):
    - Strategies 0-3 → Alert 0
    - Strategies 4-7 → Alert 1  
    - Strategies 8-11 → Alert 2
    """
    strategy_alert_pairs = []
    
    if len(alerts) < 3:
        logger.error(f"❌ Expected at least 3 alerts, found {len(alerts)}")
        return strategy_alert_pairs
    
    if len(strategies) < 12:
        logger.error(f"❌ Expected at least 12 strategies, found {len(strategies)}")
        return strategy_alert_pairs
    
    logger.info(f"📊 Processing {len(strategies)} strategies with {len(alerts)} alerts")
    
    # Process exactly 3 alerts with 4 strategies each = 12 total policy drafts
    for alert_index in range(3):
        alert = alerts[alert_index]
        
        # Calculate strategy indices for this alert
        start_strategy_index = alert_index * 4  # 0, 4, 8
        end_strategy_index = start_strategy_index + 4  # 4, 8, 12
        
        # Get the 4 strategies for this alert
        alert_strategies = strategies[start_strategy_index:end_strategy_index]
        
        logger.info(f"🔗 Alert {alert_index + 1}: '{alert.get('name', 'Unknown')[:50]}...'")
        logger.info(f"   → Strategies {start_strategy_index}-{end_strategy_index-1} ({len(alert_strategies)} strategies)")
        
        # Create pairs for each strategy with this alert
        for local_strategy_index, strategy in enumerate(alert_strategies):
            global_strategy_index = start_strategy_index + local_strategy_index
            strategy_alert_pairs.append((
                strategy, 
                alert, 
                alert_index + 1,  # Alert number (1, 2, 3)
                local_strategy_index + 1,  # Strategy number within alert (1, 2, 3, 4)
                global_strategy_index + 1  # Global strategy number (1-12)
            ))
            
            # Log the pairing
            strategy_desc = strategy.get('short_description', 'Unknown')[:40]
            logger.info(f"   ✓ Strategy {global_strategy_index + 1}: {strategy_desc}...")
    
    logger.info(f"📊 Created {len(strategy_alert_pairs)} strategy-alert pairs for policy generation")
    return strategy_alert_pairs

def create_alert_model(alert_data: Dict[str, Any]) -> AlertCreate:
    """Convert alert dictionary to AlertCreate model"""
    return AlertCreate(
        name=alert_data.get('name', ''),
        description=alert_data.get('description', ''),
        risk_score=alert_data.get('risk_score', 0),
        risk_reason=alert_data.get('risk_reason', ''),
        location=alert_data.get('location', ''),
        latitude=str(alert_data.get('latitude', '0')),
        longitude=str(alert_data.get('longitude', '0'))
    )

def create_strategy_model(strategy_data: Dict[str, Any]) -> StrategyCreate:
    """Convert strategy dictionary to StrategyCreate model"""
    return StrategyCreate(
        short_description=strategy_data.get('short_description', ''),
        full_description=strategy_data.get('full_description', ''),
        alert_id=strategy_data.get('alert_id', '')
    )

def policy_to_dict(policy: PolicyCreate) -> Dict[str, Any]:
    """Convert PolicyCreate model to dictionary for JSON serialization"""
    return {
        "title": policy.title,
        "content": policy.content,
        "author": policy.author,
        "approved": policy.approved,
        "alert_id": policy.alert_id,
        "strategy_id": policy.strategy_id,
        "generated_timestamp": datetime.now().isoformat()
    }

async def generate_policy_draft(agent: PolicyDraftGenerationAgent, strategy: StrategyCreate, 
                              alert: AlertCreate, alert_num: int, strategy_num: int, global_strategy_num: int) -> Dict[str, Any]:
    """Generate a single policy draft"""
    try:
        logger.info(f"📝 Generating policy draft #{global_strategy_num} (Alert {alert_num}, Strategy {strategy_num}): {strategy.short_description[:50]}...")
        
        start_time = datetime.now()
        
        # Generate the policy draft
        policy_draft = await agent.generate_policy_draft(
            strategy=strategy,
            alert=alert,
            author=f"AI Policy Generator - Policy #{global_strategy_num} (Alert {alert_num}, Strategy {strategy_num})"
        )
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        # Convert to dictionary and add metadata
        policy_dict = policy_to_dict(policy_draft)
        policy_dict.update({
            "generation_time_seconds": generation_time,
            "alert_number": alert_num,
            "strategy_number": strategy_num,
            "global_strategy_number": global_strategy_num,
            "source_alert_name": alert.name,
            "source_strategy_description": strategy.short_description
        })
        
        logger.info(f"✅ Policy draft generated in {generation_time:.2f} seconds")
        return policy_dict
        
    except Exception as e:
        logger.error(f"❌ Failed to generate policy draft #{global_strategy_num} (Alert {alert_num}, Strategy {strategy_num}): {e}")
        # Return error information
        return {
            "error": str(e),
            "alert_number": alert_num,
            "strategy_number": strategy_num,
            "global_strategy_number": global_strategy_num,
            "source_alert_name": alert.name if alert else "Unknown",
            "source_strategy_description": strategy.short_description if strategy else "Unknown",
            "generated_timestamp": datetime.now().isoformat()
        }

async def append_policy_draft(policy_draft: Dict[str, Any]) -> None:
    """Append a single policy draft to the NDJSON file"""
    try:
        # Ensure output directory exists
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to file (create if doesn't exist)
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            json.dump(policy_draft, f, ensure_ascii=False)
            f.write('\n')
        
        # Log success
        if 'error' in policy_draft:
            logger.info(f"📝 Appended error record for policy #{policy_draft.get('global_strategy_number', 'unknown')}")
        else:
            logger.info(f"💾 Appended policy draft #{policy_draft.get('global_strategy_number', 'unknown')} to {OUTPUT_FILE}")
        
    except Exception as e:
        logger.error(f"❌ Error appending policy draft to file: {e}")
        raise

async def initialize_output_file() -> None:
    """Initialize the output file by clearing it if it exists"""
    try:
        # Ensure output directory exists
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Clear the file if it exists
        if OUTPUT_FILE.exists():
            OUTPUT_FILE.unlink()
            logger.info(f"🗑️  Cleared existing output file: {OUTPUT_FILE}")
        
        logger.info(f"📁 Output file initialized: {OUTPUT_FILE}")
        
    except Exception as e:
        logger.error(f"❌ Error initializing output file: {e}")
        raise

async def main():
    """Main execution function"""
    print("🚀 Policy Draft Generation from Strategies")
    print("=" * 80)
    
    start_time = datetime.now()
    successful_drafts = 0
    failed_drafts = 0
    
    try:
        # Initialize output file
        logger.info("📁 Initializing output file...")
        await initialize_output_file()
        
        # Load data
        logger.info("📂 Loading data files...")
        strategies = await load_strategies()
        alerts = await load_alerts()
        
        # Match strategies to alerts
        logger.info("🔗 Matching strategies to alerts...")
        strategy_alert_pairs = match_strategies_to_alerts(strategies, alerts)
        
        if not strategy_alert_pairs:
            logger.error("❌ No strategy-alert pairs found")
            return
        
        # Initialize the policy draft generation agent
        logger.info("🤖 Initializing PolicyDraftGenerationAgent...")
        agent = PolicyDraftGenerationAgent()
        
        # Generate policy drafts with incremental saving
        logger.info(f"📝 Generating {len(strategy_alert_pairs)} policy drafts...")
        
        for i, (strategy_data, alert_data, alert_num, strategy_num, global_strategy_num) in enumerate(strategy_alert_pairs, 1):
            logger.info(f"\n🔄 Processing Policy #{global_strategy_num} ({i}/{len(strategy_alert_pairs)})")
            
            try:
                # Convert to models
                strategy = create_strategy_model(strategy_data)
                alert = create_alert_model(alert_data)
                
                # Generate policy draft
                policy_draft = await generate_policy_draft(agent, strategy, alert, alert_num, strategy_num, global_strategy_num)
                
                # Append to file immediately
                await append_policy_draft(policy_draft)
                
                # Update counters
                if 'error' in policy_draft:
                    failed_drafts += 1
                else:
                    successful_drafts += 1
                
                # Progress update
                progress = (i / len(strategy_alert_pairs)) * 100
                logger.info(f"📊 Progress: {progress:.1f}% ({i}/{len(strategy_alert_pairs)}) - Success: {successful_drafts}, Failed: {failed_drafts}")
                
            except Exception as policy_error:
                logger.error(f"❌ Unexpected error processing policy #{global_strategy_num}: {policy_error}")
                
                # Create error record and append it
                error_record = {
                    "error": f"Processing error: {str(policy_error)}",
                    "alert_number": alert_num,
                    "strategy_number": strategy_num,
                    "global_strategy_number": global_strategy_num,
                    "source_alert_name": alert_data.get('name', 'Unknown') if alert_data else 'Unknown',
                    "source_strategy_description": strategy_data.get('short_description', 'Unknown') if strategy_data else 'Unknown',
                    "generated_timestamp": datetime.now().isoformat()
                }
                
                try:
                    await append_policy_draft(error_record)
                    failed_drafts += 1
                except Exception as append_error:
                    logger.error(f"❌ Failed to append error record: {append_error}")
        
        # Final summary
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Show file size
        if OUTPUT_FILE.exists():
            file_size = OUTPUT_FILE.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"📊 Output file size: {file_size_mb:.2f} MB")
        
        print("\n" + "=" * 80)
        print("📊 FINAL SUMMARY")
        print("=" * 80)
        print(f"✅ Successful policy drafts: {successful_drafts}")
        print(f"❌ Failed policy drafts: {failed_drafts}")
        print(f"📁 Output file: {OUTPUT_FILE}")
        print(f"⏱️  Total processing time: {total_time/60:.1f} minutes")
        
        if len(strategy_alert_pairs) > 0:
            print(f"⚡ Average time per draft: {total_time/len(strategy_alert_pairs):.1f} seconds")
        
        if successful_drafts == len(strategy_alert_pairs):
            print("🎉 All policy drafts generated successfully!")
        elif successful_drafts > 0:
            print("⚠️  Some policy drafts generated successfully, check logs for errors")
            print(f"💡 You can monitor progress by running: tail -f {OUTPUT_FILE}")
        else:
            print("❌ No policy drafts generated successfully")
            
    except Exception as e:
        logger.error(f"❌ Script execution failed: {e}")
        raise

if __name__ == "__main__":
    # Check if required files exist
    if not STRATEGIES_FILE.exists():
        print(f"❌ Strategies file not found: {STRATEGIES_FILE}")
        print("Please ensure strategies.ndjson exists in documents/data/")
        sys.exit(1)
    
    if not DASHBOARD_FILE.exists():
        print(f"❌ Dashboard file not found: {DASHBOARD_FILE}")
        print("Please ensure dashboard.json exists in documents/data/")
        sys.exit(1)
    
    # Run the async main function
    asyncio.run(main()) 