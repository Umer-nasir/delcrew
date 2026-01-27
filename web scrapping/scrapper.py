from crewai_tools import tool

@tool
def joke_teller(name: str) -> str:
    return f"Why did {name} bring a ladder? Because the joke was on another level!"