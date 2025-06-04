#!/usr/bin/env python3
"""
Generate Strategies from Dashboard Alerts

This utility script reads the dashboard.json file from documents/data/,
processes each alert through the StrategyGenerationAgent, and saves
the generated strategies to strategies.jsonl.

Usage:
    python utils/generate_strategies_from_dashboard.py

Requirements:
    - Run from the project root directory
    - Uses the backend app's virtual environment
    - Requires dashboard.json in documents/data/
    - Outputs strategies.jsonl in documents/data/
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app.agents.strategy_generation_agent import StrategyGenerationAgent
    from app.models.alert import AlertCreate
    from app.models.strategy import StrategyCreate
except ImportError as e:
    print(f"❌ Failed to import required modules. Make sure you're running from the project root.")
    print(f"Error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StrategyGenerator:
    """Main class for generating strategies from dashboard alerts"""
    
    def __init__(self):
        """Initialize the strategy generator"""
        self.agent = None
        self.dashboard_file = Path("documents/data/dashboard.json")
        self.output_file = Path("documents/data/strategies.jsonl")
        
    async def initialize_agent(self):
        """Initialize the StrategyGenerationAgent"""
        try:
            logger.info("🤖 Initializing StrategyGenerationAgent...")
            self.agent = StrategyGenerationAgent()
            logger.info("✅ StrategyGenerationAgent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise
    
    def load_dashboard_data(self) -> Dict[str, Any]:
        """Load the dashboard.json file"""
        try:
            logger.info(f"📁 Loading dashboard data from {self.dashboard_file}")
            
            if not self.dashboard_file.exists():
                raise FileNotFoundError(f"Dashboard file not found: {self.dashboard_file}")
                
            with open(self.dashboard_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            alerts = data.get('alerts', [])
            logger.info(f"✅ Loaded {len(alerts)} alerts from dashboard")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to load dashboard data: {e}")
            raise
    
    def convert_alert_to_model(self, alert_data: Dict[str, Any], alert_id: str) -> AlertCreate:
        """Convert dashboard alert data to AlertCreate model"""
        try:
            # Handle latitude/longitude conversion to strings
            latitude = str(alert_data.get('latitude', '0.0'))
            longitude = str(alert_data.get('longitude', '0.0'))
            
            # Handle N/A coordinates
            if latitude == 'N/A':
                latitude = '0.0'
            if longitude == 'N/A':
                longitude = '0.0'
                
            return AlertCreate(
                name=alert_data.get('name', 'Unknown Alert'),
                description=alert_data.get('description', 'No description available'),
                risk_score=int(alert_data.get('risk_score', 1)),
                risk_reason=alert_data.get('risk_reason', 'No risk reason provided'),
                location=alert_data.get('location', 'Unknown Location'),
                latitude=latitude,
                longitude=longitude
            )
        except Exception as e:
            logger.error(f"❌ Failed to convert alert data: {e}")
            raise
    
    async def generate_strategies_for_alert(self, alert: AlertCreate, alert_id: str) -> List[Dict[str, Any]]:
        """Generate strategies for a single alert"""
        try:
            logger.info(f"🎯 Generating strategies for alert: {alert.name}")
            
            # Generate strategies using the agent
            strategies = await self.agent.generate_strategies(alert)
            
            # Convert strategies to dict format with alert_id
            strategy_dicts = []
            for strategy in strategies:
                strategy_dict = {
                    "alert_id": alert_id,
                    "short_description": strategy.short_description,
                    "full_description": strategy.full_description,
                    "generated_at": datetime.now().isoformat(),
                    "agent_version": "strategy_generation_agent_v1"
                }
                strategy_dicts.append(strategy_dict)
            
            logger.info(f"✅ Generated {len(strategy_dicts)} strategies for alert: {alert.name}")
            return strategy_dicts
            
        except Exception as e:
            logger.error(f"❌ Failed to generate strategies for alert {alert.name}: {e}")
            # Return empty list on failure to continue processing other alerts
            return []
    
    def save_strategies_to_jsonl(self, all_strategies: List[Dict[str, Any]]):
        """Save all strategies to JSONL file"""
        try:
            logger.info(f"💾 Saving {len(all_strategies)} strategies to {self.output_file}")
            
            # Create output directory if it doesn't exist
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write strategies as JSONL (one JSON object per line)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for strategy in all_strategies:
                    json.dump(strategy, f, ensure_ascii=False)
                    f.write('\n')
            
            logger.info(f"✅ Successfully saved strategies to {self.output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save strategies: {e}")
            raise
    
    async def process_all_alerts(self):
        """Main processing function - load alerts and generate strategies"""
        try:
            # Initialize agent
            await self.initialize_agent()
            
            # Load dashboard data
            dashboard_data = self.load_dashboard_data()
            alerts_data = dashboard_data.get('alerts', [])
            
            if not alerts_data:
                logger.warning("⚠️  No alerts found in dashboard data")
                return
            
            all_strategies = []
            processed_count = 0
            failed_count = 0
            
            logger.info(f"🚀 Processing {len(alerts_data)} alerts...")
            
            for i, alert_data in enumerate(alerts_data):
                alert_id = f"alert_{i+1:03d}"  # Generate alert ID like "alert_001", "alert_002"
                
                try:
                    # Skip alerts with invalid data
                    if alert_data.get('risk_score', 0) <= 0:
                        logger.warning(f"⚠️  Skipping alert {alert_id} with invalid risk score: {alert_data.get('risk_score')}")
                        continue
                    
                    # Convert to AlertCreate model
                    alert = self.convert_alert_to_model(alert_data, alert_id)
                    
                    # Generate strategies
                    strategies = await self.generate_strategies_for_alert(alert, alert_id)
                    
                    if strategies:
                        all_strategies.extend(strategies)
                        processed_count += 1
                        logger.info(f"✅ Processed alert {alert_id}: {alert.name}")
                    else:
                        failed_count += 1
                        logger.warning(f"⚠️  No strategies generated for alert {alert_id}")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ Failed to process alert {alert_id}: {e}")
                    continue
            
            # Save all strategies
            if all_strategies:
                self.save_strategies_to_jsonl(all_strategies)
                
                # Summary
                logger.info("=" * 60)
                logger.info("📊 PROCESSING SUMMARY")
                logger.info("=" * 60)
                logger.info(f"✅ Total alerts processed: {processed_count}")
                logger.info(f"❌ Failed alerts: {failed_count}")
                logger.info(f"🎯 Total strategies generated: {len(all_strategies)}")
                logger.info(f"📁 Output file: {self.output_file}")
                logger.info("=" * 60)
            else:
                logger.warning("⚠️  No strategies were generated from any alerts")
                
        except Exception as e:
            logger.error(f"❌ Fatal error during processing: {e}")
            raise


async def main():
    """Main entry point"""
    try:
        print("🚀 Dashboard Strategy Generator")
        print("=" * 50)
        
        generator = StrategyGenerator()
        await generator.process_all_alerts()
        
        print("\n🎉 Strategy generation completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if running from correct directory
    if not Path("documents/data").exists():
        print("❌ Error: documents/data directory not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Run the async main function
    asyncio.run(main()) 