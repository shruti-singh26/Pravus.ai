class KnowledgeArticleAgent:
    def __init__(self, retriever, llm):
        self.retriever = retriever  # Function to search knowledge articles
        self.llm = llm              # LLM for summarization/rephrasing

    def search(self, user_query: str, top_k: int = 3) -> str | None:
        docs = self.retriever(user_query, top_k=top_k)
        if not docs:
            return None

        relevant_contents = [
            doc.page_content if hasattr(doc, "page_content") else str(doc)
            for doc in docs if doc
        ]
        # Use LLM to synthesize a user-friendly answer
        prompt = (
            "You are a helpful assistant. Based on the following knowledge articles, "
            "answer the user's question in a clear, concise, and helpful way:\n\n"
            f"User question: {user_query}\n\n"
            "Knowledge articles:\n" +
            "\n---\n".join(relevant_contents)
        )
        summary = self.llm(prompt)
        return summary.strip() if summary else "\n\n".join(relevant_contents)