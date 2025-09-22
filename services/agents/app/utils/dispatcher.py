from app.utils.intent_classifier import classify_intent
from app.agentics.financial_manager.crew import FinancialManagerCrew
# from app.agentics.investment_advisor.crew import InvestmentAdvisorCrew # Placeholder
# from app.agentics.financial_analyst.crew import FinancialAnalystCrew # Placeholder
from app.utils.pinecone import upsert_history
import re

def dispatcher(query: str, user_id: str, agent_key: str = None):
    """
    Dispatches a user query to the appropriate agent crew, executes the task,
    and saves the conversation history to Pinecone.
    """
    if not agent_key:
        # If no command, use LLM to classify intent
        try:
            agent_key = classify_intent(query)
        except Exception as e:
            print(f"Intent classification failed: {e}. Defaulting to financial_manager.")
            agent_key = "financial_manager"

    # Extract the core query text without the command
    text_only_query = re.sub(r'/\w+\s*', '', query).strip()

    # Initialize result variable
    result = None

    # Route to the correct crew
    if agent_key == "financial_manager":
        crew = FinancialManagerCrew()
        result = crew.manage_budget(text_only_query)
    elif agent_key == "investment_advisor":
        # crew = InvestmentAdvisorCrew() # Placeholder for future implementation
        # result = crew.provide_advice(text_only_query)
        print(f"Investment advisor not implemented. Defaulting to financial manager.")
        crew = FinancialManagerCrew()
        result = crew.manage_budget(text_only_query)
    elif agent_key == "financial_analyst":
        # crew = FinancialAnalystCrew() # Placeholder for future implementation
        # result = crew.analyze_market(text_only_query)
        print(f"Financial analyst not implemented. Defaulting to financial manager.")
        crew = FinancialManagerCrew()
        result = crew.manage_budget(text_only_query)
    else:
        # Fallback to a default or general-purpose crew if classification is unclear
        agent_key = "financial_manager"
        crew = FinancialManagerCrew()
        result = crew.manage_budget(text_only_query)

    # Save the interaction to Pinecone
    if result:
        try:
            upsert_history(chat_id=user_id, query=text_only_query, response=result, namespace=agent_key)
        except Exception as e:
            # Log the error but don't block the response to the user
            print(f"Error upserting to Pinecone: {e}")

    return result