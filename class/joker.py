from crewai import Agent, Task, Crew, LLM
from crewai.memory.storage.rag_storage import RAGStorage
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os


memory_storage = RAGStorage(type='chromadb',path='./chroma_joker_teller')

question = input("ASK A QUESTION TO YOUR AI TEAM: ")

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

friend = Agent(
    role="AI Best Friend",
    goal="Be friendly and remember user conversations to answer naturally that user ask in {topic}.",
    backstory="A loyal and chatty AI friend.",
    llm=llm
)

remember_task = Task(
    description="Remember everything about the user for future conversation.",
    expected_output="Accurate memory storage of user info.",
    agent=friend
)

editor = Agent(
    role="Editor",
    goal="Polish the final answer in 2-3 lines after others provide input.",
    backstory="An expert editor who loves brevity and clarity.",
    llm=llm
)

shorten_task = Task(
    description="Polish and shorten the final answer to 2-3 lines.",
    expected_output="Concise, clear, final answer.",
    agent=editor
)


crew = Crew(
    agents=[friend, editor], 
    tasks=[remember_task, shorten_task],  
    verbose=False,
    memory=True,
    memory_storage=memory_storage,
    output_log_file = "crew_logs.txt",
    embedder={
        "provider": "sentence-transformer",
        "config": {"model_name": "all-MiniLM-L6-v2"}
    }
)


result = crew.kickoff(inputs={"topic": question})
print("\n===== AI TEAM ANSWER =====")
print(result)