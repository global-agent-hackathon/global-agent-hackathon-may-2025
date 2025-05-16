from agno.agent import Agent
from agno.models.google import Gemini

from agentTools.agentTools import AgentTools


class AgentsUtility:
    @staticmethod
    def terminalAgent(id: str, apiKey: str) -> Agent:
        return Agent(
            model=Gemini(api_key=apiKey, id=id),
            markdown=True,
            name="terminal agent",
            role=(
                "You are a smart and proactive terminal agent designed to execute shell commands based on natural language prompts. "
                "You should make intelligent assumptions to minimize unnecessary confirmations, and execute tasks smoothly by inferring user intent. "
                "If the command involves a known system directory (e.g., Documents, Desktop), first resolve its path using the getFolderLocation tool, "
                "then run the command using the terminal tool. Confirm only when executing potentially dangerous commands like file deletion or system changes. "
                "When you anticipate that a command may prompt for confirmation (e.g., installations or initializations), prepend the command with 'yes |' to bypass interactive prompts and ensure uninterrupted execution within the subprocess environment."
            ),
            tools=[AgentTools.getFolderLocation, AgentTools.runTerminalCommand]
        )

    @staticmethod
    def generalPurposeAgent(id: str, apiKey: str) -> Agent:
        return Agent(
            model=Gemini(id=id, api_key=apiKey),
            tools=[AgentTools.searchWeb()],
            name="general purpose agent",
            role=(
                "You are an intelligent assistant embedded in a search interface. "
                "In addition to helping with searches, you can summarize information, define words, and write small, precise code snippets. "
                "Keep all responses brief and focused, as this assistant is designed for quick, lightweight tasks."
            ),
            markdown=True)
