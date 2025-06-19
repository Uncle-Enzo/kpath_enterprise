"""
Database registration script for the Shoes Agent
Registers the agent and its tools in the KPATH Enterprise database
"""

import asyncio
import json
from datetime import datetime
from .config import SHOES_SERVICE_CONFIG, TOOLS_CONFIG

async def register_shoes_agent():
    """Register the Shoes Agent and its tools in the database"""
    try:
        # This would connect to the actual database
        # For now, we'll return the SQL statements that need to be executed
        
        service_insert_sql = f"""
        INSERT INTO services (
            service_name, service_description, service_type, category, 
            base_url, authentication_type, status, version, provider,
            rate_limit, timeout_seconds, supported_formats, 
            integration_complexity, documentation_url
        ) VALUES (
            '{SHOES_SERVICE_CONFIG["service_name"]}',
            '{SHOES_SERVICE_CONFIG["description"]}',
            '{SHOES_SERVICE_CONFIG["service_type"]}',
            '{SHOES_SERVICE_CONFIG["category"]}',
            '{SHOES_SERVICE_CONFIG["base_url"]}',
            '{SHOES_SERVICE_CONFIG["authentication_type"]}',
            '{SHOES_SERVICE_CONFIG["status"]}',
            '{SHOES_SERVICE_CONFIG["version"]}',
            '{SHOES_SERVICE_CONFIG["provider"]}',
            '{SHOES_SERVICE_CONFIG["rate_limit"]}',
            {SHOES_SERVICE_CONFIG["timeout_seconds"]},
            '{json.dumps(SHOES_SERVICE_CONFIG["supported_formats"])}',
            '{SHOES_SERVICE_CONFIG["integration_complexity"]}',
            '{SHOES_SERVICE_CONFIG["documentation_url"]}'
        );
        """
        
        print("Service Registration SQL:")
        print(service_insert_sql)
        print("\n" + "="*50 + "\n")
        
        # Generate tool registration SQL
        print("Tool Registration SQL:")
        for i, tool in enumerate(TOOLS_CONFIG):
            tool_sql = f"""
            INSERT INTO tools (
                service_id, tool_name, tool_description, 
                input_schema, output_schema, example_calls,
                tool_type, status, version
            ) VALUES (
                (SELECT service_id FROM services WHERE service_name = 'ShoesAgent'),
                '{tool["tool_name"]}',
                '{tool["description"]}',
                '{json.dumps(tool["parameters"])}',
                '{{"type": "object", "properties": {{"success": {{"type": "boolean"}}, "data": {{"type": "object"}}}}}}',
                '{json.dumps([{"example": "Sample call for " + tool["tool_name"]}])}',
                'function',
                'active',
                '1.0.0'
            );
            """
            print(f"-- Tool {i+1}: {tool['tool_name']}")
            print(tool_sql)
        
        return {
            "success": True,
            "message": "SQL statements generated for Shoes Agent registration",
            "service_config": SHOES_SERVICE_CONFIG,
            "tools_count": len(TOOLS_CONFIG)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = asyncio.run(register_shoes_agent())
    print(json.dumps(result, indent=2))
