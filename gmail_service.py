# gmail_service.py

import os
from dotenv import load_dotenv

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from composio_langchain import ComposioToolSet, App

load_dotenv()

# 1. Initialize environment and API key
composio_api_key = os.getenv("COMPOSIO_API_KEY")  # Make sure .env contains COMPOSIO_API_KEY

# 2. Set up the LLM and function-calling prompt
llm = ChatOpenAI()  
prompt = hub.pull("hwchase17/openai-functions-agent")  

# 3. Build the Composio toolset and extract the Gmail “send email” action
composio_toolset = ComposioToolSet(api_key=composio_api_key)
tools = composio_toolset.get_tools(actions=["GMAIL_SEND_EMAIL"])

# 4. Create an OpenAI Functions agent that knows about GMAIL_SEND_EMAIL
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

async def send_email(to_addrs: list[str], subject: str, body: str) -> None:
    """
    Sends a plain-text email to one or more recipients via the Gmail MCP integration.

    Parameters:
      - to_addrs: List of recipient email addresses (e.g. ["alice@example.com", "bob@example.com"])
      - subject:  Subject line for the email
      - body:     Plain-text body of the email
    """
    # Build a single comma-separated “to” string
    to_field = ", ".join(to_addrs)

    # Construct the task for the agent. 
    # The GMAIL_SEND_EMAIL action expects a payload that includes 'to', 'subject', and 'body'.
    task = (
        f"Send an email with:\n"
        f"- To: {to_field}\n"
        f"- Subject: {subject}\n"
        f"- Body:\n{body}"
    )

    # Invoke the agent. Because we pulled only GMAIL_SEND_EMAIL above, 
    # the agent knows how to map this natural-language instruction into the correct function call.
    result = agent_executor.invoke({"input": task})

    # Optionally, you can inspect the result to confirm success
    print("GMAIL_SEND_EMAIL result:", result)


# Example usage (for testing outside of an async context):
# --------------------------------------------
# import asyncio
#
# if __name__ == "__main__":
#     recipients = ["alice@example.com", "bob@example.com"]
#     subj = "🚀 Drive Folder Updated"
#     body_text = "The following files were changed:\n- report.pdf (edited)\n- budget.xlsx (added)"
#
#     asyncio.run(send_email(recipients, subj, body_text))
# --------------------------------------------
