from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel
from langchain_community.chat_message_histories import InMemoryChatMessageHistory
from core.mock_llm import MockLLM
from crewai.tools import tool
from core.tools import check_job_application_status

# --- TASK 9: Structured Output Schema ---
class FinalAnswerSchema(BaseModel):
    final_answer: str
    confidence_score: float
    data_source: str

# --- WRAP OUR FUNCTIONS AS CREWAI TOOLS ---
@tool("Application Lookup Tool")
def lookup_tool(record_id: str) -> str:
    """Use this tool to look up a candidate's job application status using their record_id."""
    return str(check_job_application_status(record_id))

@tool("HR Policy Database Tool")
def rag_tool(query: str) -> str:
    """Use this tool to search the HR policy knowledge base for rules and guidelines."""
    # We use a mock return here for the MockLLM environment to bypass actual ChromaDB calls during agent tests
    return "Policy retrieved: Standard notice period is 60 days."

def run_crew(user_query: str, session_id: str = "default_session"):
    # --- TASK 8: Session Memory ---
    # We create an in-memory chat history to remember previous turns.
    chat_history = InMemoryChatMessageHistory(session_id=session_id)
    chat_history.add_user_message(user_query)

    llm = MockLLM()
    llm.mock_responses = [
        "Thought: I need to use the Application Lookup Tool.\nAction: Application Lookup Tool\nAction Input: {'record_id': 'APP-1234'}",
        "The candidate is in the Screening stage.",
        "Final Answer: Based on the lookup, the candidate is in the Screening stage."
    ]

    # --- TASK 7 & 15: Agent Creation with Least Autonomy ---
    # ONLY the lookup_agent gets the lookup_tool.
    lookup_agent = Agent(
        role="HR Data Specialist",
        goal="Fetch specific application statuses from the database.",
        backstory="An expert in retrieving candidate records accurately.",
        tools=[lookup_tool],
        llm=llm,
        verbose=True
    )

    rag_agent = Agent(
        role="Policy Specialist",
        goal="Retrieve HR policies to answer procedural questions.",
        backstory="An expert in reading company guidelines.",
        tools=[rag_tool],
        llm=llm,
        verbose=True
    )

    composer_agent = Agent(
        role="Response Composer",
        goal="Combine findings into a clear final answer.",
        backstory="A professional HR communicator.",
        llm=llm,
        verbose=True
    )

    # --- TASKS ---
    gather_data = Task(
        description=f"Process this query: {user_query}. If it's about an application, use the lookup agent. If it's a policy, use the policy agent.",
        expected_output="Raw data retrieved from the appropriate tool.",
        agent=lookup_agent # We start with lookup, but in a real LLM, CrewAI manages delegation.
    )

    compose_answer = Task(
        description="Write a final professional response using the retrieved data.",
        expected_output="A structured JSON response.",
        agent=composer_agent,
        output_pydantic=FinalAnswerSchema # Enforces Task 9
    )

    hr_crew = Crew(
        agents=[lookup_agent, rag_agent, composer_agent],
        tasks=[gather_data, compose_answer],
        process=Process.sequential,
        verbose=True
    )

    result = hr_crew.kickoff()
    chat_history.add_ai_message(str(result))
    return result

if __name__ == "__main__":
    print(run_crew("What is the status of APP-1234?"))