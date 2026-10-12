"""Contract implemented by each coding-agent adapter."""
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from pathlib import Path


class AgentAdapter(ABC):
    name: str

    def add_options(self, parser: ArgumentParser) -> None:
        """Register options specific to this agent."""

    def forwarded_options(self, args: Namespace) -> list[str]:
        return []

    def model_label(self, model: str) -> str:
        return model

    @abstractmethod
    def settings(self, args: Namespace) -> dict:
        """Resolve model and reasoning settings without copying credentials."""

    @abstractmethod
    def prepare(self, args: Namespace, target: Path, info: dict) -> tuple[list[str], list[str]]:
        """Write isolated config; return Docker flags and stdin-driven CLI command."""

    @abstractmethod
    def configure_local_mcp(self, config_dir: Path, name: str, command: list[str],
                            environment: dict[str, str], *,
                            startup_timeout_seconds: int = 30,
                            tool_timeout_seconds: int = 180) -> None:
        """Add a local MCP server to prepared isolated config.

        Timeouts are seconds. Adapters document native timeout differences.
        The benchmark owns the service command, environment and file mounts.
        """

    @abstractmethod
    def archive_sessions(self, config_dir: Path, run: Path) -> str | None:
        """After container shutdown, archive session data only; return relative path."""

    @abstractmethod
    def metrics(self, events: list[dict], completed: bool, source: str) -> dict:
        """Normalize native events to shared usage fields; retain native details."""
