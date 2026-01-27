from crewai import Agent,Task,Crew,LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import os

load_dotenv()


llm = LLM(model="groq/llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"))


search_tool = SerperDevTool()

topic=input("Enter a Essay you want to learn about: ")

researcher_agent = Agent(
    role = "researcher",
    goal = "gather accurate and relevant information on a given topic of essay",
    backstory = "you are an expert researcher skilled at finding accurate and relevant information",
    llm = llm,
    tools = [search_tool]
)
researcher_task = Task(
    description = f"conduct thorough research on the essay: {topic} using available tools",
    expected_output = "a detailed report on including key facts, statistics, and insights",
    agent = researcher_agent
)
writer_agent = Agent(
    role = "Writer",
    goal="Once all the information is gathered write accurate and sensible essay connecting your relation with writer and use easy words of 50 lines.",
    backstory="An expert writer with years of experience.",
    llm= llm
)
writer_task = Task(
    description="write the information sequence and remove any misunderstanding and irrelevant information and use easy words",
    expected_output="a well written essay with paragraphing and brilliant content.",
    agent=writer_agent
)
editor = Agent(
    role="Editor",
    goal="your goal is to check and remove any misunderstanding and make the essay sequencially and remove any disinformation and check everything is according to essay",   
    backstory="a professional editor with years of experience",
    llm=llm
)
editor_task = Task(
    description="A highly skilled content Editor who reviews and enhances written material for clarity, accuracy, and flow. The Editor corrects grammatical errors, improves sentence structure, aligns tone with the intended audience, removes redundancies, and ensures the content meets quality and formatting standards without altering the core message.",
    expected_output="A polished, final version of the content with improved grammar, clarity, structure, and tone, while fully preserving the original meaning. The output should be clean, coherent, professional, and ready for use or publication, with no explanations or commentary.",
    agent=editor
)
crew = Crew(
    agents=[researcher_agent,writer_agent,editor],
    tasks= [researcher_task,writer_task,editor_task],
)
result=crew.kickoff(inputs={"topic": topic})
print(result)