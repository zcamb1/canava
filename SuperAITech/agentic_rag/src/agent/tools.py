from utils import neo4j_driver
from text2cypher import Text2Cypher

answer_given_description = {
    "type": "function",
    "function": {
        "name": "respond",
        "description": "If the conversation already contains a complete answer to the question, use this tool to extract it. Additionally, if the user engages in small talk, use this tool to remind them that you can only answer questions about movies and their cast.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "Respond directly with the answer",
                }
            },
            "required": ["answer"],
        },
    },
}


def answer_given(answer: str):
    """Extract the answer from a given text."""
    return answer


text2cypher_description = {
    "type": "function",
    "function": {
        "name": "text2cypher",
        "description": "Query the database with a user question. When other tools don't fit, fallback to use this one.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user question to find the answer for",
                }
            },
            "required": ["question"],
        },
    },
}


def text2cypher(question: str):
    """Query the database with a user question."""
    quesion = Trans(question)
    t2c = Text2Cypher(neo4j_driver)
    t2c.set_prompt_section("question", question)
    cypher = t2c.generate_cypher()
    try:
        records, _, _ = neo4j_driver.execute_query(cypher)
        return [record.data() for record in records]
    except Exception as e:
        return [f"{cypher} cause an error: {e}"]
    
similarity_search_description = {
    "type": "function",
    "function": {
        "name": "respond",
        "description": "If the conversation already contains a complete answer to the question, use this tool to extract it. Additionally, if the user engages in small talk, use this tool to remind them that you can only answer questions about movies and their cast.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "Respond directly with the answer",
                }
            },
            "required": ["answer"],
        },
    },
}


def similarity_search(answer: str):
    """Extract the answer from a given text."""
    return answer