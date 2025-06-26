import logging
from utils.openAI import prompt_llm 
from config.llmPrompts import essay_test_system_prompt, essay_test_user_prompt

logger = logging.getLogger(__name__)


async def check_essay_with_ai(question: str, essay: str) -> dict:
    """
    Uses OpenAI's API to check the essay against the question.
    Returns a dictionary with the results.
    """
    try:
        logger.info("Starting essay evaluation with LLM")
        logger.debug(f"Question: {question}")
        logger.debug(f"Essay (truncated): {essay[:200]}...")

        prompt = essay_test_user_prompt.format(question=question, essay=essay)
        response = await prompt_llm(system_message=essay_test_system_prompt, prompt=prompt) 

        logger.info("Essay evaluation completed successfully")
        logger.debug(f"LLM Response: {response}")

        return response

    except Exception as e:
        logger.exception("Error occurred during essay evaluation")
        raise ValueError(f"Error checking essay with AI: {e}")