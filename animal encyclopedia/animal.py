from crewai import Agent, Task, Crew, LLM
from crewai_tools import ScrapeWebsiteTool
from google import genai
import os
search = ScrapeWebsiteTool(web_url="https://www.bbcearth.com/factfiles/animals/mammals/monkey")
print("=" * 50)
print(" ANIMAL ENCYCLOPEDIA BUILDER")
print("=" * 50)
animal = input("What animal to research? ")

llm = LLM(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)


researcher = Agent(
 role='Animal Researcher',
 goal='Find amazing facts about {topic}',
 backstory='You are a wildlife expert.',
 tools=[search],
 llm=llm)

fact_checker = Agent(
 role='Fact Checker',
 goal='Verify facts are true and interesting',
 backstory='You make sure all facts are correct.',
 llm=llm)

writer = Agent(
 role='Encyclopedia Writer',
 goal='Write fun encyclopedia entries for kids about {topic}',
 backstory='You write like National Geographic Kids!',
 llm=llm)

research_task = Task(
 description='Search for 10 amazing facts about {topic}',
 expected_output='10 interesting facts',
 agent=researcher)

check_task = Task(
 description='Check facts and pick the 5 best ones',
 expected_output='5 verified amazing facts',
 agent=fact_checker)

write_task = Task(
 description='Write a fun encyclopedia entry about {topic}',
 expected_output='Encyclopedia entry for kids',
 agent=writer)


crew = Crew(
agents=[researcher, fact_checker, writer],
tasks=[research_task, check_task, write_task]
)
result = crew.kickoff(
    inputs = {"topic":animal}
)
print(result)