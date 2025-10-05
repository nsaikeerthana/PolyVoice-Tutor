
# PolyVoice: The Adaptive Accessibility Tutor
PolyVoice is a generative AI multi-agent system designed to transform complex academic content into personalized, accessible learning experiences. It solves the critical accessibility gap for students with learning differences (Dyslexia, ADHD) by delivering filtered, simplified lessons via an adaptive, conversational interface.

The unique value of PolyVoice lies in its ability to adapt content structure based on the user's profile and cognitive needs, a feat enabled by the speed of the Cerebras Llama API.

The Dual-Agent Reasoning Loop
For every query, the system executes two specialized LLM agents in sequence:

Agent	Sponsor Tool Used	Unique Task & Accessibility Benefit
Simplifier Agent	Cerebras Llama 3.1	Adaptive Filtering: Enforces strict structural constraints (e.g., short sentences for Dyslexia, chunked steps for ADHD) on the content derived from RAG.
Quiz Agent	Cerebras Llama 3.1	Structured Evaluation: Generates a clean, predictable, multiple-choice quiz format (QUESTION/A/B/C/D/ANSWER), ensuring immediate comprehension checking.

Stateful Conversation (Memory)
The system maintains conversational flow by passing the full chat_history list through the orchestrator to the Simplifier Agent, allowing the tutor to ask and respond to contextual follow-up questions ("What are the three types of that?") without losing the thread.

. Project Structure
polyvoice_project/
├── .env                          
├── requirements.txt              
├── Dockerfile                    
├── docker-compose.yml            
├── app.py                        
└── agents/
    ├── orchestrator.py           
    ├── simplify_agent.py         
    ├── quiz_agent.py           
    └── voice_agent.py

    
2. Prerequisites
You must have the following running locally or accessible via API:

Docker Desktop (Required for containerization and local testing).

API Keys from the following services, saved in your local .env file:

CEREBRAS_API_KEY

EXA_API_KEY

ELEVEN_API_KEY

3. Local Execution (For Development/Testing)
For fast iteration without Docker, run the project inside a virtual environment:


# 1. Create and activate environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Use 'source venv/bin/activate' on Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit app
streamlit run app.py

4. Dockerized Deployment (For Final Demo)
To run the application exactly as it would be deployed (via Docker Compose):

Bash

# 1. Stop any old containers and build the new image
# The build installs all dependencies (ffmpeg, python libs)
docker-compose build

# 2. Run the container and expose port 8501
docker-compose up

# 3. Access the application in your browser:
# http://localhost:8501
