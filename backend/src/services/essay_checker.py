import logging
from utils.openAI import prompt_llm 
from config.llmPrompts import essay_test_system_prompt, essay_test_user_prompt

logger = logging.getLogger(__name__)


def calculate_results(results: dict, essay: str) -> float:

    content_score = 0
    for criterion in results.get("content", {}).get("criterias", []):
        content_score += criterion.get("score", 0)
    
    if content_score:
        content_score = content_score / len(results.get("content", {}).get("criterias", []))

    language_score = 0
    for criterion in results.get("language", {}).get("criterias", []):
        language_score += criterion.get("score", 0)

    if language_score:
        language_score = language_score / len(results.get("language", {}).get("criterias", []))

    essay_word_count = len(essay.split())
    essay_lines_count = essay_word_count // 12

    if essay_lines_count <= 10:
        # The essay will not be checked, implying a score of 0.
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
        pass  
    elif essay_lines_count > 50:
        results['general_conclusion'] = 'החיבור ארוך מהמותר – נפסל אוטומטית .'
        results['complete_score'] = 0.0
        return results
    
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

        # Preliminary check for essay length to avoid unnecessary LLM call
        essay_word_count = len(essay.split())
        essay_lines_count = essay_word_count // 12

        if essay_lines_count <= 10:
            logger.info("Essay too short — rejected before LLM evaluation")
            return {
                "content": {"criterias": [], "score": 0},
                "language": {"criterias": [], "score": 0},
                "general_conclusion": 'החיבור קצר מדי – נפסל אוטומטית).',
                'length_conclusion' : 'אורך החיבור אינו תקין.',
                "complete_score": 0.0,
                "suggestions": [
                "וודא שאורך החיבור תואם את הטווח המותר: 25-50 שורות.",
            ]
            }

        if essay_lines_count > 50:
            logger.info("Essay too long — rejected before LLM evaluation")
            return {
                "content": {"criterias": [], "score": 0},
                "language": {"criterias": [], "score": 0},
                "general_conclusion": 'החיבור ארוך מהמותר – נפסל אוטומטית .',
                'length_conclusion' : 'אורך החיבור אינו תקין.',
                "complete_score": 0.0,
                "suggestions": [
                "וודא שאורך החיבור תואם את הטווח המותר: 25-50 שורות.",
            ]
            }

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
