from typing import Dict, Any

def debug_code(user_code: str, language: str) -> Dict[str, Any]:
    """
    Advanced mock debugging engine.
    Detects syntax errors, bracket mismatches, infinite loops, and logic errors.
    Returns corrected code and improvement suggestions.
    """
    if not user_code.strip():
        return {"status": "error", "message": "Please paste some code to debug."}

    bugs = []
    corrected_code = user_code
    suggestion = "Your code looks solid! Consider extracting helper methods if logic grows complex."
    
    # 1. Bracket mismatch detection
    open_brackets = user_code.count('{') + user_code.count('(') + user_code.count('[')
    close_brackets = user_code.count('}') + user_code.count(')') + user_code.count(']')
    if open_brackets != close_brackets:
        bugs.append({
            "type": "Syntax Error",
            "explanation": "Bracket mismatch detected. You have unclosed or extra brackets/parentheses."
        })

    # 2. Infinite Loop risks
    if "while " in user_code and "++" not in user_code and "+=" not in user_code and "-=" not in user_code and "--" not in user_code:
        bugs.append({
            "type": "Infinite Loop Risk",
            "explanation": "You have a while loop but no obvious iterator increment (e.g. i++ or i+=1). Ensure your loop condition eventually turns false."
        })

    # Language specific checks
    if language == "Python":
        if "def " in user_code and ":" not in user_code.split("def ")[1].split("\n")[0]:
            bugs.append({
                "type": "Syntax Error",
                "explanation": "Missing colon ':' at the end of function definition."
            })
            corrected_code = corrected_code.replace("def solve(self, nums)", "def solve(self, nums):")
            
        if "return " not in user_code:
            bugs.append({
                "type": "Logic Error",
                "explanation": "Missing return statement. The function will return None."
            })
            
    elif language in ["Java", "C++"]:
        if "return" in user_code and "return" not in user_code.split(";")[-1]:
             # Just a simple heuristic for missing semicolons
             if not user_code.endswith(";") and not user_code.endswith("}") and not user_code.strip() == "":
                 bugs.append({
                     "type": "Syntax Error",
                     "explanation": "Missing semicolon ';' at the end of a statement."
                 })
                 corrected_code += ";"

    if not bugs:
        return {
            "status": "success",
            "message": "No obvious syntax or heuristic errors found! The logic appears structurally sound.",
            "bugs": [],
            "corrected_code": corrected_code,
            "suggestion": suggestion
        }
    
    return {
        "status": "issues_found",
        "message": f"Found {len(bugs)} potential issue(s) in your code.",
        "bugs": bugs,
        "corrected_code": corrected_code,
        "suggestion": "Review the highlighted errors above. Ensure all syntax is correct before worrying about logical correctness."
    }
