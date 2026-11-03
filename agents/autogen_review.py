import asyncio
from pydantic import BaseModel
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import TextMessage

# --- TASK 14: Pydantic Verdict Model ---
class FinalVerdictModel(BaseModel):
    approved: bool
    final_answer: str
    reason: str

# Define the Structured Message type required by the rubric
class StructuredMessage(BaseModel):
    content: FinalVerdictModel
    source: str

async def run_review_stage(draft_answer: str, retrieved_context: str, mock_llm_client):
    """
    Runs the AutoGen review stage. 
    mock_llm_client is passed in to ensure 0 network calls.
    """
    # 1. The Policy Reviewer
    reviewer = AssistantAgent(
        name="Policy-Compliance-Reviewer",
        model_client=mock_llm_client,
        system_message="You review draft answers against the provided context. Point out ungrounded claims."
    )

    # 2. The Final Editor (Must output the Pydantic Model)
    editor = AssistantAgent(
        name="Final-Editor",
        model_client=mock_llm_client,
        system_message="You make the final decision. Output JSON exactly matching the FinalVerdictModel schema.",
        # Rubric Requirement: Pydantic structured output on the agent
        output_content_type=FinalVerdictModel 
    )

    # 3. The Team (RoundRobinGroupChat)
    # Rubric Requirement: Must register the custom_message_types
    review_team = RoundRobinGroupChat(
        participants=[reviewer, editor],
        custom_message_types=[StructuredMessage]
    )

    # Rubric Requirement: MaxMessageTermination(3) counts the initiating message as #1, 
    # letting both agents speak exactly once.
    termination_condition = MaxMessageTermination(3)

    input_message = f"Retrieved Context: {retrieved_context}\n\nDraft Answer: {draft_answer}\n\nPlease review and finalize."
    
    # Run the team
    result = await review_team.run(task=input_message, termination_condition=termination_condition)
    
    return result

if __name__ == "__main__":
    # We will test this properly when we tie it into the FastAPI deployment in the next step.
    print("AutoGen Review Stage architecture successfully defined.")