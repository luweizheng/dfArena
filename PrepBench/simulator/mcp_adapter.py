"""stdio MCP adapter for the PrepBench clarification HTTP session."""
import os
import asyncio
import logging
import time
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clarification")
logger = logging.getLogger(__name__)
ASK_TIMEOUT_SECONDS = 160

@mcp.tool()
async def ask(questions: list[str]) -> dict:
    """Ask the simulated user and wait for the complete answer."""
    started = time.perf_counter()
    logger.info('Clarification HTTP request started (%d questions)', len(questions))
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(150, connect=5), trust_env=False) as client:
            response = await asyncio.wait_for(client.post(
                os.environ["DFARENA_CLARIFIER_URL"],
                json={"session_id": os.environ["DFARENA_SESSION_ID"], "questions": questions},
            ), timeout=ASK_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json()
    except (asyncio.TimeoutError, httpx.TimeoutException) as exc:
        raise RuntimeError('Clarification timed out; inspect simulator server.log before retrying.') from exc
    finally:
        logger.info('Clarification HTTP request finished after %.3fs', time.perf_counter() - started)

if __name__ == "__main__":
    mcp.run(transport="stdio")
