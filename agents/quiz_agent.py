# In agents/quiz_agent.py

# NOTE: The Cerebras client (cb) is passed into the run function.
# The complexity_level is not used here but is accepted for function signature consistency.

# 🎯 FIX: ADD FLOWCHART GENERATION LOGIC
def run(cb, simplified_text, query, chat_history): 
    
    # 1. --- QUIZ GENERATION PROMPT (Task 1) ---
    quiz_prompt = f"""
    Based ONLY on the following simplified explanation about: {query}, 
    create **one** multiple-choice comprehension question with four options (A, B, C, D) and indicate the answer.
    
    Format your response STRICTLY as:
    QUESTION: [The question]
    A) [Option 1]
    B) [Option 2]
    C) [Option 3]
    D) [Option 4]
    ANSWER: [A/B/C/D]
    
    [SIMPLIFIED TEXT]: {simplified_text}
    """
    quiz_completion = cb.chat.completions.create(
        model="llama3.1-8b", 
        messages=[{"role": "user", "content": quiz_prompt}],
        max_tokens=400,
        temperature=0.5
    )
    quiz_text = quiz_completion.choices[0].message.content

    # 2. --- FLOWCHART GENERATION PROMPT (Task 2: Creative Use of Cerebras) ---
    flowchart_prompt = f"""
    Analyze the following simplified text. Your goal is to extract the main sequence of events, dependencies, or steps.
    
    Format your output **STRICTLY** using the Mermaid flowchart syntax (graph TD; A[Step 1] --> B[Step 2]). Do not include any introductory text or explanations.
    
    [SIMPLIFIED TEXT]: {simplified_text}
    """
    flowchart_completion = cb.chat.completions.create(
        model="llama3.1-8b", 
        messages=[{"role": "user", "content": flowchart_prompt}],
        max_tokens=300, # Smaller max_tokens for this structured task
        temperature=0.0 # Low temperature for precise syntax
    )
    flowchart_text = flowchart_completion.choices[0].message.content

    # 3. --- RETURN BOTH RESULTS ---
    # The quiz agent now returns a dictionary containing both outputs.
    return {
        "quiz_text": quiz_text,
        "flowchart_text": flowchart_text.strip()
    }