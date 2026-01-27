import sys
import signal
import warnings
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2:")

if sys.platform == "win32":
    for sig in ("SIGHUP", "SIGTSTP", "SIGTTIN", "SIGTTOU", "SIGCONT"):
        if not hasattr(signal, sig):
            setattr(signal, sig, signal.SIGINT)

from crewai import Agent,Task,Crew,LLM

my_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key="ENTER_YOUR_API_KEY_HERE"
) 
storyteller = Agent(
    role="Story teller",
    goal="write 20 line horror story.",
    backstory="A professional story teller with 10 years of experience",
    llm=my_llm
)
story_task = Task(
    description="Write a well-written 20-line horror story with a clear start and end.",
    expected_output="A horror story, 20 lines long.",
    agent=storyteller
)

crew = Crew(
    agents=[storyteller],
    tasks=[story_task],
    llm=my_llm      
)
result = crew.kickoff()
print(result)