import re
from typing import Dict, Any

def extract_constraints(problem_statement: str) -> Dict[str, Any]:
    """
    Advanced parser to extract constraints, input types, edge cases, and expected outputs.
    Uses regex and heuristic parsing.
    """
    result = {
        "input_type": "Unknown",
        "constraints": [],
        "edge_cases": [],
        "expected_output": "Unknown",
        "important_keywords": []
    }

    if not problem_statement or not problem_statement.strip():
        return result

    text = problem_statement

    # 1. Extract Constraints using regex
    # Looks for common constraint formats like: "1 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9"
    constraint_pattern = r'(-?\d+(?:\^|e)\d+|\d+)\s*<=\s*([a-zA-Z0-9_\[\]\.]+)\s*<=\s*(-?\d+(?:\^|e)\d+|\d+)'
    matches = re.finditer(constraint_pattern, text)
    for match in matches:
        result["constraints"].append(match.group(0))

    # Fallback/Additional constraints section parsing
    if "Constraints:" in text:
        try:
            constraints_section = text.split("Constraints:")[1].strip().split('\n')
            for line in constraints_section:
                clean_line = line.strip().lstrip('-').lstrip('•').strip()
                if clean_line and clean_line not in result["constraints"] and len(clean_line) < 100:
                    result["constraints"].append(clean_line)
        except Exception:
            pass
            
    # 2. Extract Input Type & Expected Output (Heuristics)
    # Looking for "Given an array of integers nums" or "Return the indices"
    lower_text = text.lower()
    
    if "array" in lower_text or "list" in lower_text or "vector" in lower_text:
        result["input_type"] = "Array / List"
    elif "string" in lower_text:
        result["input_type"] = "String"
    elif "tree" in lower_text or "node" in lower_text:
        result["input_type"] = "Tree Nodes"
    elif "matrix" in lower_text or "grid" in lower_text:
        result["input_type"] = "2D Matrix"

    if "return true" in lower_text or "return false" in lower_text:
        result["expected_output"] = "Boolean (True/False)"
    elif "return the minimum" in lower_text or "return the maximum" in lower_text or "return an integer" in lower_text:
        result["expected_output"] = "Integer (Min/Max/Count)"
    elif "return an array" in lower_text or "return a list" in lower_text:
        result["expected_output"] = "Array / List"
    elif "return the string" in lower_text:
        result["expected_output"] = "String"

    # 3. Detect Edge Cases based on constraints
    for constraint in result["constraints"]:
        if "0 <=" in constraint or "1 <=" in constraint and "length" in constraint:
            result["edge_cases"].append("Empty or single-element input.")
        if "-10" in constraint:
            result["edge_cases"].append("Negative numbers in input.")
            
    if "duplicate" in lower_text:
        result["edge_cases"].append("Input contains duplicate values.")
    if "sorted" in lower_text:
        result["important_keywords"].append("Sorted Array")

    # Ensure no empty lists if we failed to parse
    if not result["constraints"]:
        result["constraints"] = ["No explicit constraints detected. Assume standard 32-bit integer limits."]
    if not result["edge_cases"]:
        result["edge_cases"] = ["Consider extreme values (0, Max Int) and empty inputs."]

    return result
