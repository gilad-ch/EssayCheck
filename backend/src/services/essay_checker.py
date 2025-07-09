import logging
from utils.openAI import prompt_llm 
from config.llmPrompts import essay_test_system_prompt, essay_test_user_prompt

logger = logging.getLogger(__name__)


def calculate_results(results: dict, essay: str) -> dict:
    """
    Calculates and updates the results dictionary with content, language, and complete scores,
    as well as conclusions based on essay length. Returns the updated results dict.
    """
    # Ensure 'suggestions' key exists
    if 'suggestions' not in results or not isinstance(results['suggestions'], list):
        results['suggestions'] = []

    # Calculate content score
    content_criterias = results.get("content", {}).get("criterias", [])
    content_score = sum(criterion.get("score", 0) for criterion in content_criterias)
    if content_criterias:
        content_score /= len(content_criterias)
    else:
        content_score = 0

    # Calculate language score
    language_criterias = results.get("language", {}).get("criterias", [])
    language_score = sum(criterion.get("score", 0) for criterion in language_criterias)
    if language_criterias:
        language_score /= len(language_criterias)
    else:
        language_score = 0

    # Calculate essay length in lines (assuming 12 words per line)
    essay_word_count = len(essay.split())
    essay_lines_count = essay_word_count // 12

    # Handle length-based rules
    if essay_lines_count <= 10:
        # Essay too short, automatic fail
        results['general_conclusion'] = 'החיבור קצר מדי – נפסל אוטומטית.'
        results['complete_score'] = 0.0
        results['length_conclusion'] = 'אורך החיבור אינו תקין.'
        return results
    elif 10 < essay_lines_count <= 19:
        language_score = max(0, language_score - 1)
        results['length_conclusion'] = 'החיבור קצר מדי – נוכתה נקודה מציון השפה .'
        results['suggestions'].append(
            "וודא שאורך החיבור תואם את הטווח המותר: 25-50 שורות."
        )
    elif 20 <= essay_lines_count <= 24:
        language_score = max(0, language_score - 2)
        results['length_conclusion'] = 'החיבור קצר מדי – נוכו 2 נקודות מציון השפה .'
        results['suggestions'].append(
            "וודא שאורך החיבור תואם את הטווח המותר: 25-50 שורות."
        )
    elif 25 <= essay_lines_count <= 50:
        results['length_conclusion'] = 'אורך החיבור תקין. אין ניכוי נקודות.'
    elif essay_lines_count > 50:
        results['general_conclusion'] = 'החיבור ארוך מהמותר – נפסל אוטומטית .'
        results['complete_score'] = 0.0
        return results

    # Update results with calculated scores
    if 'content' not in results:
        results['content'] = {}
    if 'language' not in results:
        results['language'] = {}
    results['content']['score'] = content_score
    results['language']['score'] = language_score
    results['complete_score'] = (content_score + language_score) * 2.0
    return results

async def check_essay_with_ai(question: str, essay: str) -> dict:
    """
    Uses OpenAI's API to check the essay against the question.
    Returns a dictionary with the results.
    """
    try:
        logger.info("Starting essay evaluation")
        logger.debug(f"Question: {question}")
        logger.debug(f"Essay (truncated): {essay[:200]}...")

        # Proceed with LLM evaluation
        prompt = essay_test_user_prompt.format(question=question, essay=essay)
        response = await prompt_llm(system_message=essay_test_system_prompt, prompt=prompt) 
        response = calculate_results(response, essay)

        logger.info("Essay evaluation completed successfully")
        logger.debug(f"LLM Response: {response}")

        return response

    except Exception as e:
        logger.exception("Error occurred during essay evaluation")
        raise ValueError(f"Error checking essay with AI: {e}")
