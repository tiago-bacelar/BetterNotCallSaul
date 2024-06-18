import logger
logger.pushTimer()

from transformers import pipeline

question_answerer = pipeline("question-answering", model="lfcc/bert-portuguese-squad")

def chatPT(context: str, prompt: str) -> str:
    result = question_answerer(question=prompt, context=context)
    return result['answer'], result['score']


logger.log(f"chatPT loaded. {logger.popTimer()} elapsed")