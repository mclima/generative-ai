"""
Predefined workflow definitions for common tasks.
"""
from typing import Dict, Any


def get_price_monitoring_workflow() -> Dict[str, Any]:
    """
    Get the price monitoring workflow definition.
    
    This workflow monitors price alerts in parallel for all active alerts.
    
    Returns:
        Workflow definition dictionary
    """
    return {
        "nodes": [
            {
                "id": "start",
                "type": "agent",
                "agent": "price_alert",
                "is_entry": True,
                "is_finish": True
            }
        ],
        "edges": []
    }


def get_research_workflow() -> Dict[str, Any]:
    """
    Get the research workflow definition.
    
    This workflow gathers news and analysis for portfolio stocks.
    
    Returns:
        Workflow definition dictionary
    """
    return {
        "nodes": [
            {
                "id": "research",
                "type": "agent",
                "agent": "research",
                "is_entry": True,
                "is_finish": True
            }
        ],
        "edges": []
    }


def get_rebalancing_workflow() -> Dict[str, Any]:
    """
    Get the rebalancing workflow definition.
    
    This workflow analyzes portfolio composition and generates rebalancing suggestions.
    
    Returns:
        Workflow definition dictionary
    """
    return {
        "nodes": [
            {
                "id": "rebalancing",
                "type": "agent",
                "agent": "rebalancing",
                "is_entry": True,
                "is_finish": True
            }
        ],
        "edges": []
    }


def get_comprehensive_analysis_workflow() -> Dict[str, Any]:
    """
    Get a comprehensive analysis workflow that runs research and rebalancing sequentially.
    
    This workflow first gathers research, then performs rebalancing analysis.
    
    Returns:
        Workflow definition dictionary
    """
    return {
        "nodes": [
            {
                "id": "research",
                "type": "agent",
                "agent": "research",
                "is_entry": True
            },
            {
                "id": "rebalancing",
                "type": "agent",
                "agent": "rebalancing",
                "is_finish": True
            }
        ],
        "edges": [
            {
                "from": "research",
                "to": "rebalancing"
            }
        ]
    }


def get_parallel_monitoring_workflow() -> Dict[str, Any]:
    """
    Get a parallel monitoring workflow that runs price alerts, research, and rebalancing in parallel.
    
    This workflow executes all three agents concurrently for maximum efficiency.
    
    Returns:
        Workflow definition dictionary
    """
    return {
        "nodes": [
            {
                "id": "start",
                "type": "condition",
                "is_entry": True
            },
            {
                "id": "price_alerts",
                "type": "agent",
                "agent": "price_alert"
            },
            {
                "id": "research",
                "type": "agent",
                "agent": "research"
            },
            {
                "id": "rebalancing",
                "type": "agent",
                "agent": "rebalancing"
            },
            {
                "id": "end",
                "type": "condition",
                "is_finish": True
            }
        ],
        "edges": [
            {
                "from": "start",
                "to": "price_alerts"
            },
            {
                "from": "start",
                "to": "research"
            },
            {
                "from": "start",
                "to": "rebalancing"
            },
            {
                "from": "price_alerts",
                "to": "end"
            },
            {
                "from": "research",
                "to": "end"
            },
            {
                "from": "rebalancing",
                "to": "end"
            }
        ]
    }


# Workflow templates registry
WORKFLOW_TEMPLATES = {
    "price_monitoring": {
        "name": "Price Monitoring",
        "description": "Monitor price alerts and trigger notifications",
        "definition": get_price_monitoring_workflow(),
        "execution_mode": "parallel",
        "default_schedule": "*/5 * * * *"  # Every 5 minutes
    },
    "research": {
        "name": "Portfolio Research",
        "description": "Gather news and analysis for portfolio stocks",
        "definition": get_research_workflow(),
        "execution_mode": "sequential",
        "default_schedule": "0 9 * * *"  # Daily at 9am
    },
    "rebalancing": {
        "name": "Portfolio Rebalancing",
        "description": "Analyze portfolio composition and suggest rebalancing",
        "definition": get_rebalancing_workflow(),
        "execution_mode": "sequential",
        "default_schedule": "0 10 * * 1"  # Weekly on Monday at 10am
    },
    "comprehensive_analysis": {
        "name": "Comprehensive Analysis",
        "description": "Sequential research and rebalancing analysis",
        "definition": get_comprehensive_analysis_workflow(),
        "execution_mode": "sequential",
        "default_schedule": "0 9 * * 1"  # Weekly on Monday at 9am
    },
    "parallel_monitoring": {
        "name": "Parallel Monitoring",
        "description": "Run all monitoring tasks in parallel",
        "definition": get_parallel_monitoring_workflow(),
        "execution_mode": "parallel",
        "default_schedule": "0 */6 * * *"  # Every 6 hours
    }
}


def get_workflow_template(template_name: str) -> Dict[str, Any]:
    """
    Get a workflow template by name.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Workflow template dictionary
        
    Raises:
        ValueError: If template not found
    """
    if template_name not in WORKFLOW_TEMPLATES:
        raise ValueError(f"Workflow template '{template_name}' not found")
    
    return WORKFLOW_TEMPLATES[template_name]


def list_workflow_templates() -> Dict[str, Dict[str, str]]:
    """
    List all available workflow templates.
    
    Returns:
        Dictionary mapping template names to their metadata
    """
    return {
        name: {
            "name": template["name"],
            "description": template["description"],
            "execution_mode": template["execution_mode"],
            "default_schedule": template["default_schedule"]
        }
        for name, template in WORKFLOW_TEMPLATES.items()
    }
