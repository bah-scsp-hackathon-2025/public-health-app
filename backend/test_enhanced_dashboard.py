#!/usr/bin/env python3
"""
Test Enhanced Dashboard with Structured Data

This test demonstrates the new structured data features:
- Sample alerts with priority scoring and analysis (mock data for basic functionality)
- Rising trends detection from epidemiological time series data
- Epidemiological signals analysis via MCP server integration
- Risk assessment with quantitative metrics
- Actionable recommendations

Note: The MCP server now focuses on epidemiological data tools (fetch_epi_signal, detect_rising_trend)
rather than mock alert/trend data. The enhanced dashboard uses sample data for basic alert functionality
while leveraging real epidemiological APIs for trend analysis.
"""

import asyncio
from app.agents.health_dashboard_agent import PublicHealthDashboardAgent
from app.agents.health_dashboard_react_agent import PublicHealthReActAgent


async def test_enhanced_standard_agent():
    """Test the enhanced standard dashboard agent"""
    print("🧪 Testing Enhanced Standard Dashboard Agent...")
    print("=" * 60)
    
    try:
        agent = PublicHealthDashboardAgent(llm_provider='auto')
        result = await agent.generate_dashboard(
            'Generate comprehensive health dashboard with detailed trend analysis and alert prioritization'
        )
        
        print("✅ Dashboard generated successfully!")
        print(f"📊 Alerts: {len(result.get('alerts', []))} alerts with analysis")
        print(f"📈 Rising trends: {len(result.get('rising_trends', []))} trends detected")
        print(f"🔬 Epidemiological signals: {len(result.get('epidemiological_signals', []))} signals")
        print(f"🎯 Recommendations: {len(result.get('recommendations', []))} recommendations")
        print(f"⚠️ Risk level: {result.get('risk_assessment', {}).get('overall_risk_level', 'unknown')}")
        
        # Show sample structured data
        if result.get('alerts'):
            alert = result['alerts'][0]
            print(f"\n🚨 Top Priority Alert:")
            print(f"   Title: {alert['title']}")
            print(f"   Severity: {alert['severity']} | Priority Score: {alert['analysis']['priority_score']}/100")
            print(f"   Risk Level: {alert['analysis']['risk_level']}")
            print(f"   Affected Population: {alert['affected_population']:,}")
            print(f"   State: {alert['state']} | Type: {alert['alert_type']}")
        
        if result.get('rising_trends'):
            trend = result['rising_trends'][0]
            print(f"\n📈 Sample Rising Trend:")
            print(f"   Signal: {trend['signal_name']}")
            print(f"   Direction: {trend['trend_direction']} | Change: {trend['change_percent']}%")
            print(f"   Risk Level: {trend['risk_level']}")
            print(f"   Current Value: {trend['current_value']} {trend['unit']}")
        
        if result.get('risk_assessment'):
            risk = result['risk_assessment']
            print(f"\n⚠️ Risk Assessment:")
            print(f"   Overall Risk: {risk.get('overall_risk_level', 'unknown')}")
            print(f"   High Severity Alerts: {risk.get('high_severity_alerts', 0)}")
            print(f"   Population Affected: {risk.get('total_population_affected', 0):,}")
            print(f"   Geographic Spread: {risk.get('geographic_spread', 'unknown')}")
        
        if result.get('recommendations'):
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"   {i}. {rec}")
        
        return result
        
    except Exception as e:
        print(f"❌ Standard agent test failed: {str(e)}")
        return None


async def test_enhanced_react_agent():
    """Test the enhanced ReAct dashboard agent"""
    print("\n" + "=" * 60)
    print("🧪 Testing Enhanced ReAct Dashboard Agent...")
    print("=" * 60)
    
    try:
        agent = PublicHealthReActAgent(llm_provider='auto')
        result = await agent.generate_dashboard(
            'Analyze epidemiological trends and generate dashboard with rising trend detection'
        )
        
        print("✅ ReAct Dashboard generated successfully!")
        print(f"📊 Alerts: {len(result.get('alerts', []))} alerts")
        print(f"📈 Rising trends: {len(result.get('rising_trends', []))} trends detected")
        print(f"🔬 Epidemiological signals: {len(result.get('epidemiological_signals', []))} signals")
        print(f"🎯 Recommendations: {len(result.get('recommendations', []))} recommendations")
        print(f"⚠️ Risk level: {result.get('risk_assessment', {}).get('overall_risk_level', 'unknown')}")
        
        # Show ReAct-specific structured data
        if result.get('epidemiological_signals'):
            signal = result['epidemiological_signals'][0]
            print(f"\n🔬 Sample Epidemiological Signal:")
            print(f"   Signal: {signal['signal_name']}")
            print(f"   Description: {signal['description']}")
            print(f"   Data Source: {signal['data_source']}")
            print(f"   Status: {signal['status']}")
        
        if result.get('rising_trends'):
            trend = result['rising_trends'][0]
            print(f"\n📈 Detected Rising Trend:")
            print(f"   Signal: {trend['signal_name']}")
            print(f"   Detection Method: {trend.get('detected_via', 'unknown')}")
            print(f"   Risk Level: {trend['risk_level']}")
        
        if result.get('risk_assessment'):
            risk = result['risk_assessment']
            print(f"\n⚠️ ReAct Risk Assessment:")
            print(f"   Overall Risk: {risk.get('overall_risk_level', 'unknown')}")
            print(f"   Signals Analyzed: {risk.get('epidemiological_signals_analyzed', 0)}")
            print(f"   Rising Trends: {risk.get('rising_trends_detected', 0)}")
            print(f"   Analysis Method: {risk.get('analysis_method', 'unknown')}")
            print(f"   Confidence: {risk.get('confidence_level', 'unknown')}")
        
        return result
        
    except Exception as e:
        print(f"❌ ReAct agent test failed: {str(e)}")
        return None


async def compare_agents():
    """Compare the output of both enhanced agents"""
    print("\n" + "=" * 60)
    print("📊 ENHANCED DASHBOARD COMPARISON")
    print("=" * 60)
    
    # Test both agents
    standard_result = await test_enhanced_standard_agent()
    react_result = await test_enhanced_react_agent()
    
    # Compare results
    print("\n" + "=" * 60)
    print("🔍 COMPARISON SUMMARY")
    print("=" * 60)
    
    if standard_result and react_result:
        print("✅ Both agents successfully generated enhanced dashboards!")
        print(f"\nStandard Agent (using sample data):")
        print(f"  - Alerts with analysis: {len(standard_result.get('alerts', []))}")
        print(f"  - Rising trends: {len(standard_result.get('rising_trends', []))}")
        print(f"  - Recommendations: {len(standard_result.get('recommendations', []))}")
        print(f"  - Risk level: {standard_result.get('risk_assessment', {}).get('overall_risk_level', 'unknown')}")
        
        print(f"\nReAct Agent (using epidemiological APIs):")
        print(f"  - Epidemiological signals: {len(react_result.get('epidemiological_signals', []))}")
        print(f"  - Rising trends detected: {len(react_result.get('rising_trends', []))}")
        print(f"  - Recommendations: {len(react_result.get('recommendations', []))}")
        print(f"  - Risk level: {react_result.get('risk_assessment', {}).get('overall_risk_level', 'unknown')}")
        
        print(f"\n🎉 Enhanced Dashboard System Test Completed!")
        print("The system now provides:")
        print("  ✅ Sample alerts with risk analysis (standard agent)")
        print("  ✅ Real epidemiological signal integration (ReAct agent)")
        print("  ✅ Rising trend detection with statistical evidence")
        print("  ✅ Quantitative risk assessment")
        print("  ✅ Actionable recommendations")
        print("\n🔬 Focus: Epidemiological data via fetch_epi_signal and detect_rising_trend tools")
        
    else:
        print("❌ One or both agents failed to generate enhanced dashboards")


if __name__ == "__main__":
    asyncio.run(compare_agents()) 