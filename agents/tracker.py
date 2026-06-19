import json
import os
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'progress.json')

def load_progress() -> list:
    """Loads progress data with automatic schema migration and error recovery."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            
            # Schema Migration & Error Recovery
            cleaned_data = []
            for item in data:
                if not isinstance(item, dict): continue
                
                # Add missing keys for old data
                item.setdefault("attempts", 1)
                item.setdefault("mistakes", 0)
                item.setdefault("revision_count", 0)
                
                # Ensure essential keys exist
                if "name" in item and "difficulty" in item:
                    cleaned_data.append(item)
                    
            return cleaned_data
            
    except (json.JSONDecodeError, IOError):
        # Corrupted JSON recovery
        print("Warning: Corrupted JSON detected. Returning empty list.")
        return []

def save_progress(data: list) -> bool:
    """Saves progress data to JSON."""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving progress: {e}")
        return False

def add_solved_problem(name: str, difficulty: str, topic: str, attempts: int = 1, mistakes: int = 0) -> dict:
    """Adds a newly solved problem or updates an existing one."""
    if not name.strip():
        return {"success": False, "message": "Problem name cannot be empty."}
        
    data = load_progress()
    
    # Check for duplicates, if exists, maybe increment revision
    for p in data:
        if p['name'].lower() == name.lower():
            p['revision_count'] += 1
            p['date_solved'] = datetime.now().strftime("%Y-%m-%d") # Update last solved date
            save_progress(data)
            return {"success": True, "message": f"Updated revision count for '{name}'!"}
            
    new_entry = {
        "id": len(data) + 1,
        "name": name,
        "difficulty": difficulty,
        "topic": topic,
        "date_solved": datetime.now().strftime("%Y-%m-%d"),
        "attempts": attempts,
        "mistakes": mistakes,
        "revision_count": 0
    }
    
    data.append(new_entry)
    
    if save_progress(data):
        return {"success": True, "message": f"Successfully tracked '{name}'!"}
    else:
        return {"success": False, "message": "Failed to save to JSON."}

def get_stats() -> dict:
    """Returns advanced statistics from progress data."""
    data = load_progress()
    
    stats = {
        "total": len(data),
        "Easy": 0,
        "Medium": 0,
        "Hard": 0,
        "topics": {},
        "total_revisions": 0
    }
    
    for p in data:
        diff = p.get('difficulty', 'Unknown')
        if diff in stats:
            stats[diff] += 1
            
        topic = p.get('topic', 'Unknown')
        stats["topics"][topic] = stats["topics"].get(topic, 0) + 1
        
        stats["total_revisions"] += p.get("revision_count", 0)
        
    return stats

def get_revision_suggestions() -> list:
    """
    Smart revision mode: Suggests old problems, or problems with high mistakes.
    """
    data = load_progress()
    if not data:
        return []
        
    suggestions = []
    today = datetime.now()
    
    for p in data:
        try:
            date_solved = datetime.strptime(p['date_solved'], "%Y-%m-%d")
            days_ago = (today - date_solved).days
            
            # Suggest if it's been more than 7 days, OR if mistakes > 0 and low revision count
            if days_ago > 7:
                suggestions.append({"reason": f"Solved {days_ago} days ago", "problem": p})
            elif p.get('mistakes', 0) > 0 and p.get('revision_count', 0) == 0:
                suggestions.append({"reason": "Had mistakes, needs review", "problem": p})
        except ValueError:
            continue
            
    # Sort so most critical are first
    suggestions.sort(key=lambda x: x["problem"].get("mistakes", 0), reverse=True)
    return suggestions[:5] # Return top 5
