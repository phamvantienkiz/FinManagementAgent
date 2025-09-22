from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings

def classify_intent(query: str) -> str:
    """Classify the user's intent using Gemini with modern LangChain runnables."""
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7,
        verbose=settings.VERBOSE,
    )

    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=(
            """
            Analyze the user's request and determine which specialist should handle it.

            Available specialists:
            - financial_manager: personal finance management, budgeting, debt management
            - investment_advisor: beginner investment advice, fund recommendations for Gen Z
            - financial_analyst: advanced market analysis, stock research, in-depth financial questions

            User request: {user_input}

            Respond with ONLY one of these options exactly:
            financial_manager | investment_advisor | financial_analyst
            """
        ).strip(),
    )

    # Build runnable pipeline: prompt | llm | output parser
    runnable = prompt | llm | StrOutputParser()

    # Use invoke() instead of deprecated .run
    response = runnable.invoke({"user_input": query})
    return str(response).strip().lower()
