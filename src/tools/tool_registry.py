from .calculator_tool import calculator
from .search_tool import search

def get_tools():
    return [
        {
            "name": "calculator",
            "description": "Calculate the result of a mathematical expression",
            "func": calculator
        },
        {
            "name": "search",
            "description": "Search the web for information",
            "func": search
        }
    ]