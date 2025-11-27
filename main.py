from dotenv import load_dotenv

import os

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_openai_tools_agent,AgentExecutor
from todoist_api_python.api import TodoistAPI

load_dotenv()

todoist_api_key = os.getenv("TODOIST_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

todoist = TodoistAPI(todoist_api_key)

@tool
def add_task(task,desc = None):
    """add a new task to the user's task list."""
    todoist.add_task(content=task,
                     description = desc)
@tool
# def finish_task(task_id,desc = None):
#     """delete the finished task in user's task list when user said that task is finished"""
#     tasks = todoist.get_tasks()
#     for t in tasks:
#         if t.content.strip().lower() == task.lower():
#             todoist.complete_task(t.id)
#             return f"Completed task: {task}"
#
#     return f"Task not found: {task}"
#     todoist.complete_task(task_id= , description = desc)

@tool
def show_tasks():
    """show all the tasks from the todoist."""
    results_paginator = todoist.get_tasks()
    bad_keywords = ["[Watch]","read","subscribe","youtube"]
    tasks = []
    for task_list in results_paginator:
        for task in task_list:
            tasks.append(task.content)
    return tasks

def tasks():
    pass


tools = [add_task,show_tasks]

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.5-flash',
    google_api_key = gemini_api_key,
    temperature = 0.3

)
system_prompt = """You are a helpful assistant. you will help me to add tasks. 
                 you will help the user finish existing tasks.
                you will help me to show existing tasks. if the user asks to show the tasks: for example, "show me the tasks"
                print out the tasks to the user. print them in the bullet list format.
                you will help me to delete finished tasks. if the user asks to finish the tasks: for exmaple,"buy milk is finished"
                delete the that task.
                """

prompt = ChatPromptTemplate.from_messages([("system", system_prompt),
                                    MessagesPlaceholder("history"),
                                    ("user", "{input}"),
                                    MessagesPlaceholder("agent_scratchpad"),
                                    ])

# chain = prompt | llm | StrOutputParser()
agent = create_openai_tools_agent(llm,tools,prompt)
agent_executor = AgentExecutor(agent=agent,tools = tools,verbose = False)
# response = chain.invoke({"input":user_input})


history = []
while True:
    user_input = input("Please type something:")
    response = agent_executor.invoke({"input":user_input,"history":history})
    print(response['output'])
    history.append(HumanMessage(content = user_input))
    history.append(AIMessage(content=response['output']))