from textwrap import dedent

from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools


## Transport Agent
transport_agent = Agent(
    
)