from crewai import Crew, Process
from .agents import FinancialManagerAgents
from .tasks import FinancialManagerTasks

class FinancialManagerCrew:
    def __init__(self):
        self.agents = FinancialManagerAgents()
        self.tasks = FinancialManagerTasks()
    
    def manage_budget(self, user_input):
        # The context is now derived from the user_input within the task
        budget_agent = self.agents.create_budget_agent()
        # The context for the task will be the user_input itself.
        budget_task = self.tasks.create_budget_task(budget_agent, user_input)
        
        crew = Crew(
            agents=[budget_agent],
            tasks=[budget_task],
            process=Process.sequential,
            verbose=True
        )
        
        # The input for kickoff is now just the user query.
        return crew.kickoff()