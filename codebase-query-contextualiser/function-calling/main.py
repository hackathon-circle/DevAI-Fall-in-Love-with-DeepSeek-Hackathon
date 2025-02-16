import json
import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from groq_service import GroqService
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

class FunctionRegistry:
    def __init__(self):
        self.functions = {}
        self.function_descriptions = {}

    def register(self, func_description: Dict[str, Any]):
        """Decorator to register a function with its description"""
        def decorator(func):
            name = func_description["name"]
            self.functions[name] = func
            self.function_descriptions[name] = func_description
            return func
        return decorator

    def get_functions_description(self) -> List[Dict[str, Any]]:
        """Get all registered function descriptions"""
        return list(self.function_descriptions.values())

    async def execute_function(self, name: str, tool_call: Dict[str, Any]) -> Any:
        """Execute a registered function with given tool call"""
        if name not in self.functions:
            raise ValueError(f"Function {name} not found")
        
        try:
            # Execute the function with unpacked arguments
            result = await self.functions[name](**tool_call["args"])
            return result
        except Exception as e:
            raise Exception(f"Error executing function {name}: {str(e)}")

class LLMFunctionCaller:
    def __init__(self):
        self.groq = GroqService.get_instance()
        self.registry = FunctionRegistry()

    def register_tool(self, tool_func):
        """Register a tool function and its description"""
        name = tool_func.name
        description = {
            "name": name,
            "description": tool_func.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to directory or file"
                    }
                },
                "required": ["path"]
            }
        }
        self.registry.functions[name] = tool_func
        self.registry.function_descriptions[name] = description

    async def process_with_functions(self, 
                                   user_input: str, 
                                   conversation_history: Optional[List[Dict]] = None) -> str:
        if conversation_history is None:
            conversation_history = []

        messages = conversation_history + [{"role": "user", "content": user_input}]

        self.groq.set_config({
            "model": "mixtral-8x7b-32768",
            "temperature": 0.7,
            "functions": list(self.registry.function_descriptions.values()),
            "function_call": "auto"
        })

        try:
            response = await self.groq.generate_response(messages)
            
            if isinstance(response, dict) and "function_call" in response:
                func_name = response["function_call"]["name"]
                func_args = json.loads(response["function_call"]["arguments"])
                
                # Execute function
                func = self.registry.functions[func_name]
                result = await func.arun(tool_input=func_args["path"])
                
                # Add result to conversation
                messages.extend([
                    {"role": "assistant", "function_call": response["function_call"]},
                    {"role": "function", "name": func_name, "content": str(result)}
                ])
                
                # Get final response with function result
                final_response = await self.groq.generate_response(messages)
                return str(result) + "\n\n" + final_response.get("content", "")
            
            return response.get("content", str(response))
            
        except Exception as e:
            return f"Error: {str(e)}"

# Example usage with LangChain's @tool decorator
@tool
async def get_weather(path: str) -> str:
    """Get the weather for a location.
    
    Args:
        path: The city name to get weather for
    Returns:
        Current weather information
    """
    # Mock weather data for demo
    weather_data = {
        "san francisco": "Foggy, 65°F",
        "new york": "Partly cloudy, 72°F",
        "london": "Rainy, 60°F",
    }
    city = path.lower()
    return weather_data.get(city, f"Weather data not available for {path}")

@tool
async def list_directory(path: str = ".") -> str:
    """List contents of a directory.
    
    Args:
        path: The directory path to list (default: current directory)
    Returns:
        A string containing the directory listing
    """
    try:
        items = os.listdir(path)
        return "\n".join([
            f"{'[DIR]' if os.path.isdir(os.path.join(path, item)) else '[FILE]'} {item}"
            for item in items
        ])
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@tool
async def read_file(path: str) -> str:
    """Read and return the contents of a file.
    
    Args:
        path: The path to the file to read
    Returns:
        The contents of the file as a string
    """
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
async def get_current_path() -> str:
    """Get the current working directory path."""
    return str(Path.cwd())

async def main():
    function_caller = LLMFunctionCaller()
    
    # Register the weather tool
    function_caller.register_tool(get_weather)
    
    # Ask about weather
    response = await function_caller.process_with_functions(
        "What's the weather like in San Francisco?"
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
