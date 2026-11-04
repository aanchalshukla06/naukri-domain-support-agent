from typing import Any, List, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

class MockLLM(LLM):
    mock_responses: List[str] = []
    current_index: int = 0

    @property
    def _llm_type(self) -> str:
        return "mock_llm"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # Feed the mock responses sequentially to the CrewAI agents
        if self.current_index < len(self.mock_responses):
            response = self.mock_responses[self.current_index]
            self.current_index += 1
            return response
        
        return "Final Answer: Reached the end of mock responses."