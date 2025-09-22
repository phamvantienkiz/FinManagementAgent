from crewai import Task

class FinancialManagerTasks:
    def create_budget_task(self, agent, user_query):
        return Task(
            description=f"""Analyze the user's detailed request and create a personalized budget plan.
            The user's request is: '{user_query}'
            
            Break down the user's income, fixed expenses, and savings goals.
            Provide a clear, actionable spending plan for variable categories like food and entertainment.
            The final output MUST be in natural, conversational Vietnamese.""",
            agent=agent,
            expected_output="A detailed, personalized budget plan in Vietnamese, presented in a clear markdown format. The plan should include specific monetary allocations for spending categories and actionable recommendations."
        )
    
    def create_debt_payoff_task(self, agent, context):
        return Task(
            description="""Create a debt payoff strategy for user with debts: {debts}, 
            interest rates: {interest_rates}, and available monthly payment: {monthly_payment}""",
            agent=agent,
            expected_output="A prioritized debt payoff plan with timeline and interest savings",
            context=context
        )