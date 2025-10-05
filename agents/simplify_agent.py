import os
from cerebras.cloud.sdk import Cerebras

# NOTE: The Cerebras client (cb) is passed into the run function from orchestrator.py

def build_simplification_instruction(complexity_level):
    """Generates the adaptive prompt instructions based on the user's need."""
    if complexity_level == "elementary-dyslexia":
        return (
            "Provide a complete explanation using simple, common words and clear, concise sentences. "
            "Break the text into short paragraphs (2-3 sentences each) to aid readability and comprehension. "
            "The output must be detailed enough to fully cover the topic."
        )
    elif complexity_level == "high-school-adhd":
        return (
            "Provide a thorough, comprehensive explanation. Use descriptive headings and numbered lists to structure "
            "the answer logically. Ensure all key facts are covered and **BOLD** any crucial terminology."
        )
    elif complexity_level == "plain-language-clarity":
        return (
            "Summarize clearly, maintaining the main facts but systematically eliminating complex academic jargon "
            "and passive voice. Do not simplify sentence structure unless necessary for clarity."
        )
    elif complexity_level == "standard-research":
        return "Act as a research assistant. Synthesize the provided context into a concise, factual, and professional summary suitable for an expert audience. Do not simplify the language."
    
    return "Provide a detailed, comprehensive explanation."

def check_for_override(cb, query):
    """
    Uses a fast, low-token LLM call to classify if the user is asking for a specific level change.
    Returns: The new complexity level string, or None if no override is detected.
    """
    classification_prompt = f"""
    Analyze the user's request: '{query}'
    
    If the request contains strong keywords indicating a desired change in complexity, output the new level EXACTLY as shown below. Otherwise, output 'NONE'.
    
    Keywords for Levels:
    - KID, CHILD, SIMPLE, EASIER, DYSLEXIA: elementary-dyslexia
    - STANDARD, ADVANCED, PROFOUND, EXPERT: plain-language-clarity
    
    Output ONLY the desired level string or 'NONE'.
    """
    
    try:
        chat_completion = cb.chat.completions.create(
            model="llama3.1-8b", # Use a fast model for classification
            messages=[{"role": "user", "content": classification_prompt}],
            max_tokens=20, # Keep this extremely small for speed
            temperature=0.0
        )
        result = chat_completion.choices[0].message.content.strip().lower()
        
        if result in ["elementary-dyslexia", "plain-language-clarity"]:
            return result
        return None
        
    except Exception as e:
        # Fallback if the classification API fails
        return None


# 🎯 RUN FUNCTION WITH OVERRIDE LOGIC
def run(cb, context, query, complexity_level, chat_history): 
    
    # 1. Check for verbal override
    new_level = check_for_override(cb, query)
    if new_level:
        complexity_level = new_level # Temporarily switch the level
    
    # 2. Build instructions based on the (potentially overridden) level
    instruction = build_simplification_instruction(complexity_level)
    
    # 3. Build system prompt and message list (memory)
    system_prompt = f"""
    You are an expert accessibility tutor. Your primary goal is to simplify complex text 
    based on the user's level. You must also maintain the flow of the conversation.
    
    [TARGET INSTRUCTIONS]: {instruction}
    
    CRITICAL RULE: **If the search context (below) contains irrelevant or unhelpful information (e.g., quiz links), you MUST ignore that context and use your general knowledge to provide a concise, factual explanation instead.**
    """

    messages = []
    messages.append({"role": "system", "content": system_prompt})

    for msg in chat_history[-6:]: 
        if msg["role"] == "user":
            messages.append({"role": "user", "content": msg["content"]})
        
    final_user_content = f"""
    Based on the conversation history and the following context, please provide the next response:
    [RESEARCH CONTEXT]: {context}
    
    USER'S NEW QUERY: {query}
    
    Provide ONLY the simplified explanation text. Do NOT include any introductory or concluding phrases.
    """
    messages.append({"role": "user", "content": final_user_content})
    
    # 4. Execute the main LLM call
    chat_completion = cb.chat.completions.create(
        model="llama3.1-8b", 
        messages=messages, 
        max_tokens=800,
        temperature=0.2
    )
    return chat_completion.choices[0].message.content