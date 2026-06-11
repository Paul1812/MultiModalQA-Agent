"""
MCP Controller — Central coordinator for the MultiModalQA-Agent pipeline.
Manages tool activation, data transfer between agents, and workflow state.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MCPContext:
    """Shared workflow state passed between agents."""
    model:      str  = "gpt-4o"
    use_ocr:    bool = True
    use_rag:    bool = True
    tools:      Dict[str, bool] = field(default_factory=dict)
    state:      Dict[str, Any]  = field(default_factory=dict)
    errors:     List[str]       = field(default_factory=list)

    def activate_tool(self, name: str):
        self.tools[name] = True
        logger.info(f"[MCP] Tool activated: {name}")

    def set(self, key: str, value: Any):
        self.state[key] = value

    def get(self, key: str, default=None):
        return self.state.get(key, default)

    def log_error(self, agent: str, err: str):
        msg = f"[{agent}] {err}"
        self.errors.append(msg)
        logger.error(msg)


class MCPController:
    """
    Central orchestrator — implements the Model Context Protocol (MCP).
    Decides which tools are activated based on input modality and config.
    """

    def __init__(self, model: str = "gpt-4o", use_ocr: bool = True, use_rag: bool = True):
        self.context = MCPContext(model=model, use_ocr=use_ocr, use_rag=use_rag)

        # Always-on tools
        self.context.activate_tool("input_classifier")
        self.context.activate_tool("answer_generator")

        if use_ocr:
            self.context.activate_tool("ocr_engine")
        if use_rag:
            self.context.activate_tool("vector_retrieval")

        logger.info(f"[MCP] Controller initialised. Active tools: {list(self.context.tools)}")

    def get_context(self) -> MCPContext:
        return self.context

    def transfer(self, from_agent: str, to_agent: str, data: Dict[str, Any]):
        """Log and store a data transfer between agents."""
        key = f"{from_agent}->{to_agent}"
        self.context.set(key, data)
        logger.info(f"[MCP] Data transfer: {from_agent} → {to_agent} | keys={list(data.keys())}")
        return data

    def handle_error(self, agent: str, error: Exception) -> str:
        """Error recovery: log and return a graceful fallback message."""
        msg = str(error)
        self.context.log_error(agent, msg)
        return f"⚠️ Agent '{agent}' encountered an issue: {msg}. Continuing with available data."

    @property
    def active_tools(self) -> List[str]:
        return [t for t, active in self.context.tools.items() if active]
