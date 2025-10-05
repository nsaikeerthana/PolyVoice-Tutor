import os
from exa_py import Exa
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs 

from .simplify_agent import run as run_simplifier_agent
from .quiz_agent import run as run_quiz_agent

# NOTE: The global client initialization block below should be REMOVED from this file
# if you are initializing the clients in app.py (which is the final, working architecture).

# --- RESEARCH AGENT FUNCTIONALITY (Updated for dependency injection) ---
def run_research_agent(exa, query, num=5):
    """
    Step 1: Research Agent - Uses Exa to find web content snippets.
    """
    result = exa.search_and_contents(
        query,
        type="auto",
        num_results=num,
        # Increased RAG size for more context
        text={"max_characters": 2000} 
    )
    return result.results

# --- ORCHESTRATOR FUNCTION (CORRECTED SIGNATURE AND LOGIC) ---
def run_pipeline(cb, exa, query, complexity_level, chat_history): 
    """
    ORCHESTRATOR: Manages the flow (Research -> Simplify -> Quiz) with memory.
    """
    # 1. 🔍 STEP 1: RESEARCH AGENT (Data Retrieval/RAG Context)
    sources = run_research_agent(exa, query, 5) 

    context = ""
    for i, s in enumerate(sources, 1):
        # Increased snippet length for better context transfer to the LLM
        context += f"Source {i}. {s.title}: {s.text[:1800]}...\n" 
        
    references = [{"title": s.title, "url": s.url} for s in sources]

    # 2. 📝 STEP 2: SIMPLIFIER AGENT (Cerebras Call 1)
    simplified_text = run_simplifier_agent(cb, context, query, complexity_level, chat_history)

    # 3. ❓ STEP 3: QUIZ AGENT (Cerebras Call 2 - Now returns a dictionary)
    # FIX 1: The quiz agent now returns {'quiz_text': ..., 'flowchart_text': ...}
    quiz_results = run_quiz_agent(cb, simplified_text, query, chat_history) 

    # 4. FINAL RETURN
    return {
        "simplified_text": simplified_text,
        "quiz_text": quiz_results["quiz_text"],     # FIX 2: Unpack the quiz text
        "flowchart_text": quiz_results["flowchart_text"], # FIX 3: Unpack the new flowchart text
        "references": references 
    }