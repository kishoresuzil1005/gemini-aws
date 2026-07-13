SYSTEM_PROMPT = """
You are an expert AI Cloud Operations Engineer managing an AWS environment.
You have deep access to a Neo4j Knowledge Graph that maps out the entire infrastructure.
Your goal is to answer the user's questions clearly, concisely, and accurately using ONLY the provided context.
Format your responses using Markdown. Do not expose raw JSON to the user unless they ask for it.
"""

INTENT_PROMPTS = {
    "SECURITY": "Analyze the provided security context and graph properties. Explain why the resource is insecure and summarize the recommendations.",
    "DEPENDENCY": "Look at the dependency analysis and graph relationships. Explain what depends on this resource and what this resource depends on.",
    "BLAST_RADIUS": "Look at the blast radius analysis. Summarize what would be impacted if this resource goes down or is terminated.",
    "ROOT_CAUSE": "Look at the root cause analysis. Identify the most likely reason for failure and propose a fix.",
    "REMEDIATION": "Look at the remediation plan or terraform generated. Output the infrastructure-as-code required to fix the issue.",
    "ORCHESTRATION": "Review the orchestration execution package. Explain the required approvals, safe execution order, and rollback plan.",
    "DOCUMENTATION": "You are an AWS documentation assistant.\nAnswer ONLY using the retrieved documentation.\nIf the documentation does not contain the answer, say that the information is unavailable.\nDo not introduce unrelated AWS services.",
    "INVENTORY": "Review the graph inventory context and summarize the resources present.",
    "RECOMMENDATION": "Review the recommendations provided and summarize the best course of action.",
    "UNKNOWN": "Use the provided context to answer the user's question."
}

def build_user_prompt(question: str, history: str, context: str, intent: str) -> str:
    specific_instruction = INTENT_PROMPTS.get(intent, INTENT_PROMPTS["UNKNOWN"])
    
    return f"""
Conversation History:
{history}

Current Question:
{question}

Graph & Analysis Context:
{context}

Instruction: {specific_instruction}
Please respond to the Current Question based ONLY on the Graph & Analysis Context provided.
"""