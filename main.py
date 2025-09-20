import os
import asyncio
import webbrowser

from dotenv import load_dotenv
from klavis import Klavis
from klavis.types import McpServerName
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StreamableHttpMcpToolAdapter, StreamableHttpServerParams
from autogen_ext.tools.mcp import mcp_server_tools


load_dotenv()

async def main() -> None:
    klavis_client = Klavis(api_key=os.getenv("KLAVIS_API_KEY"))

    # Create MCP server instance
    response = klavis_client.mcp_server.create_server_instance(
        server_name=McpServerName.GMAIL,
        user_id="demo_user",
    )

    # Handle OAuth authorization if required
    if getattr(response, "oauth_url", None):
        webbrowser.open(response.oauth_url)
        input("Press Enter after completing OAuth authorization...")

    server_params = StreamableHttpServerParams(
        url=response.server_url,
        timeout=30.0,
        sse_read_timeout=300.0,
        terminate_on_close=True,
    )

    adapters = await mcp_server_tools(server_params)

    model_client = OpenAIChatCompletionClient(model="gpt-4")
    agent = AssistantAgent(
        name="MailAI",
        model_client=model_client,
        tools=adapters,
        system_message="You are a helpful Gmail assistant.",
    )

    await Console(
        agent.run_stream(
            task="Find My Latest Emails",
            cancellation_token=CancellationToken()
        )
    )

if __name__ == "__main__":
    asyncio.run(main())
