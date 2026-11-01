from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

MIN_SCORE = 0.30  # below this, the assistant says it doesn't know

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_metadata={"hnsw:space": "cosine"},
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

PROMPT = """You are an assistant for IronStore employees.
Answer only using the context below.
Cite each fact like this: (Document title, p.N).
If the context does not answer the question, say you don't know and suggest
asking the relevant department. If documents disagree, point out both.

Context:
{context}

Question: {question}"""

def stream_answer(question: str):
    """Yields the answer one piece at a time."""
    results = db.similarity_search_with_relevance_scores(question, k=4)
    results = [(doc, score) for doc, score in results if score >= MIN_SCORE]

    if not results:
        yield "I couldn't find that in the IronStore documents. Please check with the relevant department."
        return

    context = "\n\n".join(
        f"[{doc.metadata['title']}, p.{doc.metadata['page'] + 1}]\n{doc.page_content}"
        for doc, _ in results
    )

    for chunk in llm.stream(PROMPT.format(context=context, question=question)):
        if chunk.content:
            yield chunk.content


if __name__ == "__main__":
    print("IronStore Assistant (type 'quit' to exit)\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        if question:
            print(f"\nAssistant: {stream_answer(question)}\n")