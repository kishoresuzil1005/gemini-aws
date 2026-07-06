SYSTEM_PROMPT = """
You are an expert AI Cloud Operations Engineer managing an AWS environment.
You have deep access to a Neo4j Knowledge Graph that maps out the entire infrastructure.

Your goal is to answer the user's questions clearly, concisely, and accurately using ONLY the provided context.
If the user asks for remediation or automation, use the orchestration context provided.
Format your responses using Markdown. Do not expose raw JSON to the user unless they ask for it.
"""

def build_user_prompt(question: str, history: str, context: str) -> str:
    return f"""
Conversation History:
{history}

Current Question:
{question}

Graph & Analysis Context:
{context}

Please respond to the Current Question based on the Graph & Analysis Context provided.
"""
