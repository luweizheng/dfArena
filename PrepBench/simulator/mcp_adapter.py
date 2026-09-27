"""stdio MCP adapter for the PrepBench clarification HTTP session."""
import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clarification")

@mcp.tool()
async def ask(questions: list[str]) -> dict:
    """Ask the simulated user and wait for the complete answer."""
    async with httpx.AsyncClient(timeout=180, trust_env=False) as client:
        response = await client.post(
            os.environ["DFARENA_CLARIFIER_URL"],
            json={"session_id": os.environ["DFARENA_SESSION_ID"], "questions": questions},
        )
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    mcp.run(transport="stdio")
