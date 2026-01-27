from crewai import Agent,Task,Crew,LLM
import os
llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)
user = input("Enter the prompt:")
email_writer = Agent(
    role="Email Writer",
    goal="Write a professional email of {topic} with professional tone under 120 words.",
    backstory="A professional email writer who write his email to convince people according to thier idea who knows about the trend and years of experience.",
    llm=llm
)
grammer = Agent(
    role="Grammer Checker",
    goal="to check the grammer of content written and remove rotten words",
    backstory="An english language master who knows all the english and expert in finding mistake like grammatical with years of experience",
    llm=llm
)
editor = Agent(
    role="Editor",
    goal="to edit the content written and remove rotten words and make it more professional and with a flow and easy to understand and give only an email.",
    backstory="An english language master who knows all the english and expert in finding mistake like grammatical with years of experience",
    llm=llm
)
email_task = Task(
    description="write an email according to {topic} under 120 words.",
    expected_output="an email content",
    agent=email_writer
)
grammer_task = Task(
    description="check the grammer of email and remove all sort of mistakes like grammatical and of other types.",
    expected_output="a grammer error free professional email.",
    agent=grammer
)
editor_task = Task(
    description="edit the content written and remove rotten words just an email.",
    expected_output="just an edited email.",
    agent=editor
)
crew = Crew(
    agents=[email_writer,grammer,editor],
    tasks=[email_task,grammer_task,editor_task],
    llm=llm
)
result = crew.kickoff(
    inputs={"topic":user}
)
print(result)