import requests
from mcp.server.fastmcp import FastMCP
import uvicorn
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
from serpapi import GoogleSearch
import json

mcp = FastMCP("Agent")


api_key= "O4KP6449G7DD66ZC"

@mcp.tool()
def get_stock_price(market: str) -> str:
    """
    Desc: Get the latest stock price for a given market.
    Args:
        market (str): The stock market symbol (e.g., "IBM", "AAPL").
    Returns:
        str: The latest stock price in JSON format.
    """
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={market}&apikey={api_key}'
    r = requests.get(url)
    data = r.json()

    print(data)
    time_series = data.get("Time Series (Daily)", {})
    if not time_series:
        return "No data available."

    latest_date = max(time_series.keys())
    latest_close = time_series[latest_date]["4. close"]

    return f"{market} closing price on {latest_date}: ${latest_close}"

@mcp.tool()
def search_web(query: str) -> str:
    """
    Desc: Search the web for a given query.
    Args:
        query (str): The search query.
    Returns:
        str: The search results in JSON format.
    """
    params = {
        "engine": "google",
        "q": query,
        "api_key": "3a99dfe4c65588e212a12db407e909f4d9ba1cbd8c6af7c25a8402403b80cacd"
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", [])
    print(organic_results)
    
    return  json.dumps(organic_results, indent=2)

        

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    
    starlette_app = create_starlette_app(mcp_server, debug=True)
    port = 9097
    print(f"Starting MCP server with SSE transport on port {port}...")
    print(f"SSE endpoint available at: http://localhost:{port}/sse")
    
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)