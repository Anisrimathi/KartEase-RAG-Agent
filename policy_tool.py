import os
import time

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_chroma import Chroma


# ---------------------------------------------------------
# 1. Load environment variables
# ---------------------------------------------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Please add it to your .env file."
    )


# ---------------------------------------------------------
# 2. Chroma configuration
# ---------------------------------------------------------

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "kartease_policies"


# ---------------------------------------------------------
# 3. Gemini models
# ---------------------------------------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    
)


# ---------------------------------------------------------
# 4. Connect to existing Chroma database
# ---------------------------------------------------------

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings,
)


# ---------------------------------------------------------
# 5. Policy search function
# ---------------------------------------------------------

def search_policies(question: str) -> str:
    """
    Search KartEase policy documents and generate an answer
    using only the retrieved policy information.
    """

    # Retrieve top 3 relevant chunks
    results = vectorstore.similarity_search_with_score(
        question,
        k=3
    )

    if not results:
        return (
            "Sorry, I can only help with KartEase orders and policies."
        )

    # -----------------------------------------------------
    # Build context from retrieved documents
    # -----------------------------------------------------

    context_parts = []

    for document, score in results:

        source = document.metadata.get(
            "source",
            "unknown"
        )

        source_name = os.path.basename(source)

        context_parts.append(
            f"Source: {source_name}\n"
            f"Content:\n{document.page_content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # -----------------------------------------------------
    # Prompt Gemini
    # -----------------------------------------------------

    prompt = f"""
You are the KartEase customer support assistant.

Answer the customer's question ONLY using the policy
information provided in the context below.

Do not use outside knowledge.

If the answer cannot be found in the provided policy
context, respond EXACTLY with:

Sorry, I can only help with KartEase orders and policies.

When you answer using the policy documents, include
the relevant source filename at the end.

Example:

You have 10 days from delivery to return a phone.
(Source: returns_and_refunds.md)

Policy Context:
{context}

Customer Question:
{question}
"""

    # -----------------------------------------------------
    # Call Gemini
    # -----------------------------------------------------

    for attempt in range(3):

        try:

            response = llm.invoke(prompt)

            # Some LangChain versions return response.content
            # as a string, while others may return a list.
            content = response.content

            if isinstance(content, str):
                return content

            if isinstance(content, list):

                text_parts = []

                for item in content:

                    if isinstance(item, str):
                        text_parts.append(item)

                    elif isinstance(item, dict):
                        if "text" in item:
                            text_parts.append(
                                str(item["text"])
                            )

                if text_parts:
                    return "\n".join(text_parts)

            return str(content)

        except Exception as error:

            error_text = str(error)

            # -------------------------------------------------
            # Gemini quota exceeded
            # -------------------------------------------------

            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):
                return (
                    "Gemini free-tier quota has been reached. "
                    "Please try again after the quota resets."
                )

            # -------------------------------------------------
            # Temporary Gemini server error
            # -------------------------------------------------

            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            ):

                if attempt < 2:

                    print(
                        "\nGemini temporarily unavailable. "
                        "Retrying in 5 seconds..."
                    )

                    time.sleep(5)

                    continue

            # -------------------------------------------------
            # Other errors
            # -------------------------------------------------

            raise error


# ---------------------------------------------------------
# 6. Test the policy tool directly
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("KartEase Policy Search")
    print("=" * 60)

    question = input(
        "\nAsk a KartEase policy question: "
    )

    answer = search_policies(question)

    print("\nAnswer:")
    print(answer)