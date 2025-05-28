import os
import uuid
import redis
from dotenv import load_dotenv
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.redis import AsyncRedisSaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent, ToolNode, tools_condition
from langgraph.pregel import RetryPolicy
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langfuse.callback import CallbackHandler
from utils.schema import State
from mcp.client.sse import sse_client
from mcp import ClientSession

# Load environment variables
load_dotenv()

RetryPolicy()

# Initialize Langfuse
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    session_id=str(uuid.uuid4()),
    metadata={
        "agent_id": "report_generation_agent"
    }
)

# Predefined run id for tracing
predefined_run_id = str(uuid.uuid4())

# Redis Client
redis_client = redis.Redis.from_url('redis://localhost:6379', decode_responses=True)


class ScrapingAgent:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key='ollama',
            model='llama3.2',
            base_url='http://localhost:11434/v1',
        )
   
    # Core processing function: Build the agent, load tools, process user query
    async def process(self, session: ClientSession, request: str):
            client = MultiServerMCPClient({
                "server": {
                    "url": "http://127.0.0.1:9097/sse",
                    "transport": "sse",
                }
            })
            # Use Redis-based checkpointing
            async with AsyncRedisSaver.from_conn_string('redis://localhost:6379') as checkpointer:
                await checkpointer.checkpoints_index.create(overwrite=False)
                await checkpointer.checkpoint_blobs_index.create(overwrite=False)
                await checkpointer.checkpoint_writes_index.create(overwrite=False)

                # Load available tools dynamically from MCP
                tools = await client.get_tools()
                graph_builder = StateGraph(State)

                # Create ReAct-style agent
                agent = create_react_agent(self.llm,tools, checkpointer=checkpointer)

                graph_builder.add_node("scraping-agent", agent, retry=RetryPolicy(max_attempts=5))
                graph_builder.add_edge(START, "scraping-agent")

            
                tool_node = ToolNode(tools=tools)
                graph_builder.add_node("tools", tool_node.ainvoke)

                graph_builder.add_conditional_edges("scraping-agent", tools_condition)
                graph_builder.add_edge("tools", "scraping-agent")
                graph_builder.add_edge("scraping-agent", END)

                graph = graph_builder.compile(checkpointer=checkpointer)
                graph.name = "scraping-agent"

                try:
                    # Invoke the graph with the user request
                    response = await graph.ainvoke(
                        {"messages": [{"role": "user", "content": request}]},
                        config={
                            "configurable": {"thread_id": "1"},
                            "callbacks": [langfuse_handler],
                            "run_id": predefined_run_id
                        }
                    )

                    return {
                        "agent_response": response["messages"][-1].content,
                    }
                except Exception as e:
                    print(f"Error during agent processing: {str(e)}")

    # Entry point for running queries
    async def run_query(self, query: str) -> dict:
        server_url = "http://127.0.0.1:9097/sse"
        async with sse_client(url=server_url) as streams:
            async with ClientSession(*streams) as session:
                try:
                    await session.initialize()
                    return await self.process(session, query)
                except Exception as e:
                    print(f"Error during run_query: {str(e)}")

chat = ScrapingAgent()