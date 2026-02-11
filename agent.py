import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from aws_tools import get_aws_tools

load_dotenv()

def create_agent(use_mock=False):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)

    tools = get_aws_tools()

    system_msg = "You are an AWS assistant with tools to query AWS services like S3, EC2, and IAM resources. Provide clear, concise answers."
    if use_mock:
        system_msg += " Note: Connected to mock AWS environment."

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True,handle_parsing_errors=True,max_iterations=3)

    return agent_executor

def run_agent_interactive(agent_executor, environment_name):
    print(f"\nAWS Chatbot ({environment_name})")
    print("-" * 50)
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print("\nExiting session.")
            break

        if not user_input:
            print("\nPlease enter a valid query.")
            continue

        try:
            response = agent_executor.invoke({"input": user_input})
            print(f"\n{response['output']}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

def initialize_chatbot(use_mock=False):
    try:
        agent_executor = create_agent(use_mock=use_mock)
        return agent_executor
    except Exception as e:
        print(f"Failed to initialize chatbot: {str(e)}")
        return None
