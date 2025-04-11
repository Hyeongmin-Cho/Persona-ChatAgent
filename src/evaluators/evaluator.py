from src.chain.chains import create_retrieval_evaluator, create_response_evaluator

def evaluate_document_relevance(profile, document, message):
    evaluator = create_retrieval_evaluator()
    evaluation = evaluator.invoke({"profile": profile, "document": document, "message": message})
    decision = evaluation.decision == "yes"
    return decision


def evaluate_response_quality(profile, context, messages, response):
    evaluator = create_response_evaluator()
    evaluation = evaluator.invoke({"profile": profile, "context": context, "messages": messages, "response": response})
    decision = evaluation.decision == "yes"
    return decision