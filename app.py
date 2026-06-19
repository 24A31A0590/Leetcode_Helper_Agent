import streamlit as st
import pandas as pd
from agents.parser import extract_constraints
from agents.pattern_detector import detect_patterns
from agents.solver import generate_approaches, generate_code
from agents.debugger import debug_code
from agents.tracker import add_solved_problem, get_stats, load_progress, get_revision_suggestions

# Configure page
st.set_page_config(
    page_title="LeetCode Mentor AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Dark Glassmorphism CSS
st.markdown("""
<style>
    /* Global Theme Variables */
    :root {
        --bg: #0B1120;
        --card-bg: rgba(30, 41, 59, 0.7);
        --border: rgba(255, 255, 255, 0.08);
        --primary: #38BDF8;
        --secondary: #8B5CF6;
        --success: #22C55E;
        --warning: #F59E0B;
        --danger: #EF4444;
        --text: #F8FAFC;
        --muted: #94A3B8;
    }

    /* App Background */
    .stApp {
        background-color: var(--bg);
        color: var(--text);
    }
    
    /* Headers with Gradient */
    .gradient-text {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: var(--muted);
        margin-bottom: 30px;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
        border: 1px solid var(--border);
    }
    .badge-primary { background-color: rgba(56, 189, 248, 0.1); color: var(--primary); }
    .badge-secondary { background-color: rgba(139, 92, 246, 0.1); color: var(--secondary); }
    .badge-success { background-color: rgba(34, 197, 94, 0.1); color: var(--success); }
    .badge-warning { background-color: rgba(245, 158, 11, 0.1); color: var(--warning); }
    
    /* Custom divider */
    hr {
        border-top: 1px solid var(--border);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown('<h2 class="gradient-text" style="font-size: 1.8rem;">🧠 AI Mentor</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        mode = st.radio(
            "Navigation", 
            ["📊 Dashboard", "🧩 Solve Problem", "💡 Hints", "🐛 Debugger", "📈 Progress", "🔄 Revision"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown('<p style="color: #94A3B8; font-weight: bold;">Quick Stats</p>', unsafe_allow_html=True)
        stats = get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Solved", stats['total'])
        with col2:
            st.metric("Revisions", stats['total_revisions'])
            
        st.progress(min(stats['total'] / 100, 1.0)) # Assuming 100 is the goal
        st.caption("Road to 100 problems")

    # Routing
    if mode == "📊 Dashboard":
        render_dashboard(stats)
    elif mode == "🧩 Solve Problem":
        render_solve_problem_ui()
    elif mode == "💡 Hints":
        render_hints_ui()
    elif mode == "🐛 Debugger":
        render_debug_ui()
    elif mode == "📈 Progress":
        render_progress_ui()
    elif mode == "🔄 Revision":
        render_revision_ui()

def render_dashboard(stats):
    st.markdown('<div class="gradient-text">Welcome Back!</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your DSA journey at a glance.</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''
        <div class="glass-card">
            <h3 style="color: var(--success); margin:0;">Easy</h3>
            <h1 style="margin:0;">{stats["Easy"]}</h1>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <div class="glass-card">
            <h3 style="color: var(--warning); margin:0;">Medium</h3>
            <h1 style="margin:0;">{stats["Medium"]}</h1>
        </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''
        <div class="glass-card">
            <h3 style="color: var(--danger); margin:0;">Hard</h3>
            <h1 style="margin:0;">{stats["Hard"]}</h1>
        </div>
        ''', unsafe_allow_html=True)

def render_solve_problem_ui():
    st.markdown('<div class="gradient-text">Problem Solver</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Paste a LeetCode problem, and let the AI break it down.</div>', unsafe_allow_html=True)
    
    problem_statement = st.text_area(
        "Problem Statement",
        height=200,
        placeholder="Paste your problem description here..."
    )

    if st.button("Analyze & Solve", type="primary", use_container_width=True):
        if not problem_statement.strip():
            st.error("Please enter a problem statement.")
            return

        # Store in session state for hints tab
        st.session_state['current_problem'] = problem_statement

        with st.spinner("🧠 AI is analyzing constraints and detecting patterns..."):
            constraints_data = extract_constraints(problem_statement)
            pattern_data = detect_patterns(problem_statement)
            
            # --- Analysis Section ---
            st.markdown("### 📊 Problem Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("#### 🔍 Properties")
                st.write(f"**Input Type:** `{constraints_data['input_type']}`")
                st.write(f"**Expected Output:** `{constraints_data['expected_output']}`")
                
                st.markdown("#### 📐 Constraints")
                for c in constraints_data["constraints"]:
                    st.markdown(f"- `{c}`")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("#### 🧩 Detected Patterns")
                
                if pattern_data['primary_pattern'] != "Unknown":
                    st.markdown(f'<span class="badge badge-primary">Primary: {pattern_data["primary_pattern"]}</span>', unsafe_allow_html=True)
                if pattern_data['secondary_pattern'] != "None":
                    st.markdown(f'<span class="badge badge-secondary">Secondary: {pattern_data["secondary_pattern"]}</span>', unsafe_allow_html=True)
                
                st.write(f"**Confidence:** `{pattern_data['confidence_score'] * 100}%`")
                
                st.markdown("#### ⚠️ Edge Cases")
                for e in constraints_data["edge_cases"]:
                    st.markdown(f"- {e}")
                st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("⚡ Generating approaches..."):
            approaches = generate_approaches(problem_statement)
            
            st.markdown("### 💡 Strategy")
            if "brute_force" in approaches:
                with st.expander("🐌 Brute Force"):
                    st.write(f"**Logic:** {approaches['brute_force']['logic']}")
                    st.write(f"**Explanation:** {approaches['brute_force']['explanation']}")
                    st.markdown(f'<span class="badge badge-warning">Time: {approaches["brute_force"]["time_complexity"]}</span> <span class="badge badge-success">Space: {approaches["brute_force"]["space_complexity"]}</span>', unsafe_allow_html=True)
            
            if "better" in approaches:
                with st.expander("🚀 Better Approach"):
                    st.write(f"**Logic:** {approaches['better']['logic']}")
                    st.write(f"**Explanation:** {approaches['better']['explanation']}")
                    st.markdown(f'<span class="badge badge-primary">Time: {approaches["better"]["time_complexity"]}</span> <span class="badge badge-success">Space: {approaches["better"]["space_complexity"]}</span>', unsafe_allow_html=True)

            if "optimal" in approaches:
                with st.expander("⚡ Optimal Solution", expanded=True):
                    st.write(f"**Logic:** {approaches['optimal']['logic']}")
                    st.info(f"**Why it works:** {approaches['optimal']['why_it_works']}")
                    st.write(f"**Dry Run:** {approaches['optimal']['dry_run']}")
                    st.markdown(f'<span class="badge badge-success">Time: {approaches["optimal"]["time_complexity"]}</span> <span class="badge badge-success">Space: {approaches["optimal"]["space_complexity"]}</span>', unsafe_allow_html=True)

        with st.spinner("💻 Generating code templates..."):
            codes = generate_code(problem_statement)
            if codes:
                st.markdown("### 💻 Starter Code")
                tab_py, tab_java, tab_cpp = st.tabs(["🐍 Python", "☕ Java", "⚙️ C++"])
                with tab_py: st.code(codes.get("Python", ""), language="python")
                with tab_java: st.code(codes.get("Java", ""), language="java")
                with tab_cpp: st.code(codes.get("C++", ""), language="cpp")

def render_hints_ui():
    st.markdown('<div class="gradient-text">Progressive Hints</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Get nudged in the right direction without seeing the answer.</div>', unsafe_allow_html=True)
    
    if 'current_problem' not in st.session_state:
        st.info("Please go to 'Solve Problem' and analyze a problem first.")
        return
        
    hints = generate_hints(st.session_state['current_problem'])
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("Click to reveal hints sequentially:")
    
    for i, hint in enumerate(hints):
        with st.expander(f"Reveal Hint {i+1}"):
            st.write(hint)
    st.markdown('</div>', unsafe_allow_html=True)

def render_debug_ui():
    st.markdown('<div class="gradient-text">Smart Debugger</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Paste your code to detect syntax and deep logic errors.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        language = st.selectbox("Language", ["Python", "Java", "C++"])
    with col2:
        user_code = st.text_area("Your Code", height=300, placeholder="Paste your code here...")

    if st.button("Debug Code", type="primary"):
        with st.spinner("Hunting for bugs..."):
            result = debug_code(user_code, language)
            
            if result.get("status") == "error":
                st.error(result["message"])
            elif result.get("status") == "success":
                st.success(result["message"])
            else:
                st.error(result["message"])
                for idx, bug in enumerate(result["bugs"], 1):
                    st.markdown(f'''
                    <div class="glass-card" style="border-left: 4px solid var(--danger);">
                        <h4 style="margin-top:0;">{idx}. {bug["type"]}</h4>
                        <p>{bug["explanation"]}</p>
                    </div>
                    ''', unsafe_allow_html=True)
                    
            if "suggestion" in result:
                st.info(f"💡 Suggestion: {result['suggestion']}")
                
            if "corrected_code" in result and result["corrected_code"] != user_code:
                st.markdown("### 🛠️ Proposed Fix")
                st.code(result["corrected_code"], language=language.lower())

def render_progress_ui():
    st.markdown('<div class="gradient-text">Progress Tracker</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Log New Solved Problem", expanded=True):
        with st.form("add_problem_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Problem Name")
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            with col2:
                topic = st.selectbox("Primary Topic", ["Arrays", "Strings", "Hashing", "Dynamic Programming", "Trees", "Graphs", "Binary Search", "Two Pointers", "Other"])
                attempts = st.number_input("Attempts to Solve", min_value=1, value=1)
                
            mistakes = st.number_input("Number of Logic/Syntax Mistakes Made", min_value=0, value=0)
            
            submitted = st.form_submit_button("Save to History", use_container_width=True)
            if submitted:
                res = add_solved_problem(name, difficulty, topic, attempts, mistakes)
                if res["success"]:
                    st.success(res["message"])
                else:
                    st.error(res["message"])

    st.markdown("### 🏆 Your History")
    data = load_progress()
    if data:
        df = pd.DataFrame(data)
        # Handle cases where new schema keys might be missing in visualization
        if 'attempts' not in df.columns: df['attempts'] = 1
        if 'mistakes' not in df.columns: df['mistakes'] = 0
        
        display_df = df[["date_solved", "name", "difficulty", "topic", "attempts", "mistakes", "revision_count"]]
        display_df.columns = ["Date Solved", "Problem", "Difficulty", "Topic", "Attempts", "Mistakes", "Revisions"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No problems tracked yet.")
def generate_hints(problem):
    hints = [
        "Think about the data structure that can reduce time complexity.",
        "Try identifying the pattern in the problem.",
        "Can you optimize by storing previous values?"
    ]
    return hints

def render_revision_ui():
    st.markdown('<div class="gradient-text">Smart Revision</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-curated problems you should review today based on spacing and mistakes.</div>', unsafe_allow_html=True)
    
    suggestions = get_revision_suggestions()
    
    if not suggestions:
        st.success("You're all caught up! No problems need urgent revision right now.")
        return
        
    for idx, item in enumerate(suggestions):
        p = item["problem"]
        reason = item["reason"]
        
        # Color coding difficulty
        diff_color = "var(--success)" if p['difficulty'] == "Easy" else "var(--warning)" if p['difficulty'] == "Medium" else "var(--danger)"
        
        st.markdown(f'''
        <div class="glass-card" style="border-left: 4px solid {diff_color};">
            <h3 style="margin:0;">{p['name']} <span style="font-size:1rem; font-weight:normal; color:var(--muted);">({p['topic']})</span></h3>
            <p style="color: var(--primary); font-weight: bold; margin-top: 5px;">⚠️ {reason}</p>
            <p style="margin: 0; color: var(--muted); font-size: 0.9rem;">
                Last Solved: {p['date_solved']} | Mistakes Made: {p.get('mistakes', 0)} | Revisions: {p.get('revision_count', 0)}
            </p>
        </div>
        ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
