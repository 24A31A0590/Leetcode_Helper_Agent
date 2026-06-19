import re

# Comprehensive mapping of keywords to DSA topics
PATTERN_KEYWORDS = {
    "Arrays": ["array", "list", "nums", "elements", "subarray", "sequence"],
    "Strings": ["string", "characters", "substring", "palindrome", "anagram", "word"],
    "Hashing": ["hash", "map", "dictionary", "frequency", "count", "unique", "duplicates", "two sum"],
    "Stack": ["stack", "LIFO", "valid parentheses", "monotonic", "next greater"],
    "Queue": ["queue", "FIFO", "level order"],
    "Recursion": ["recursion", "recursive", "fibonacci", "combinations", "permutations", "backtrack"],
    "Binary Search": ["binary search", "sorted array", "log n", "search insert", "rotated"],
    "Greedy": ["greedy", "minimum number of", "maximum number of", "intervals", "merge"],
    "Sliding Window": ["sliding window", "contiguous", "subarray", "maximum sum", "longest substring"],
    "Two Pointers": ["two pointers", "left and right", "two sum", "palindrome", "container"],
    "Linked List": ["linked list", "node", "next pointer", "head", "reverse list"],
    "Trees": ["tree", "binary tree", "root", "leaf", "bst", "lowest common ancestor", "inorder", "preorder", "postorder"],
    "Graphs": ["graph", "edge", "vertex", "nodes", "dfs", "bfs", "shortest path", "connected components", "cycle"],
    "Heap": ["heap", "priority queue", "kth largest", "top k", "smallest"],
    "Dynamic Programming": ["dynamic programming", "dp", "memoization", "tabulation", "knapsack", "longest common", "optimal substructure"],
    "Backtracking": ["backtracking", "combinations", "permutations", "subsets", "n-queens", "sudoku"]
}

def detect_patterns(problem_statement: str) -> dict:
    """
    Advanced pattern detection engine using heuristic keyword matching.
    Returns primary pattern, secondary pattern, and confidence score.
    """
    if not problem_statement or not problem_statement.strip():
        return {
            "primary_pattern": "Unknown",
            "secondary_pattern": "None",
            "confidence_score": 0.0
        }

    statement_lower = problem_statement.lower()
    scores = {topic: 0 for topic in PATTERN_KEYWORDS}

    # Calculate scores based on keyword occurrences
    total_matches = 0
    for topic, keywords in PATTERN_KEYWORDS.items():
        for keyword in keywords:
            # Use regex to match whole words to avoid partial matches (e.g., "node" in "anode")
            matches = len(re.findall(rf'\b{re.escape(keyword)}\b', statement_lower))
            if matches > 0:
                # Weight specific keywords slightly higher (e.g. 'dp' vs 'array')
                weight = 1.5 if topic in ["Dynamic Programming", "Graphs", "Trees"] else 1.0
                scores[topic] += matches * weight
                total_matches += matches * weight

    # Sort topics by score
    sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    primary = "Unknown"
    secondary = "None"
    confidence = 0.0

    if sorted_topics and sorted_topics[0][1] > 0:
        primary = sorted_topics[0][0]
        # Calculate confidence as ratio of primary score to total matches (max 0.95 for heuristics)
        confidence = min(0.95, round((sorted_topics[0][1] / total_matches) + 0.1, 2))
        
        if len(sorted_topics) > 1 and sorted_topics[1][1] > 0:
            secondary = sorted_topics[1][0]

    # Special logic: If Tree/Graph AND Recursion are high, usually it's Tree/Graph DFS.
    if primary == "Recursion" and secondary in ["Trees", "Graphs"]:
        primary, secondary = secondary, primary # Swap to prefer structural patterns over procedural ones

    return {
        "primary_pattern": primary,
        "secondary_pattern": secondary,
        "confidence_score": confidence
    }
