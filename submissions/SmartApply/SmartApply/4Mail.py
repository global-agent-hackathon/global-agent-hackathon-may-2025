from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from composio_langchain import ComposioToolSet, Action, App
llm = ChatOpenAI()
prompt = hub.pull("hwchase17/openai-functions-agent")

composio_toolset = ComposioToolSet(api_key="kc73e496wa2vqwzthdtta")
tools = composio_toolset.get_tools(actions=['GMAIL_SEND_EMAIL'])

import pandas as pd
import sys
df = pd.read_csv(r"JobsData.csv")
num_job = 0
num_job = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # Default to 0 if not provided
print(num_job)

job_url = df["Apply_URL"].iloc[num_job]
with open("CL.txt", "w", encoding="utf-8") as f:
    f.write(df["Coverletter"].iloc[num_job])

recr_email = df["recruiter_email"].iloc[num_job]

if len(str(recr_email)) < 4:
    recr_email = "r2raviteja@gmail.com"
JD = df["Combined"].iloc[num_job]

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

# Updated Recruiter Email Agent
recruiter_email_agent = Agent(
    name="Recruiter Email Agent",
    role="Compose a concise follow-up email to a recruiter after submitting job application.",
    model=OpenAIChat("gpt-4.1-nano", temperature=0.3),
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        """
        **Strict Rules:**
        1. NEVER use placeholders like [Name] or [Company]. Write generically if information is missing.
        2. NEVER include bullet points, numbered lists, or markdown in the email body.
        3. Keep the email to 2 short paragraphs maximum (3-4 sentences each).
        4. Mention the cover letter ONLY in the closing section.

        **Required Elements:**
        - State you've applied for the position
        - Highlight one specific qualification from the job description
        - Reference the cover letter at the end before your signature

        **Email Structure:**
        - Subject Line: "Follow-Up on [Job Title] Application" (use actual title or "the position")
        - Body:
          * Paragraph 1: Confirm your application and express enthusiasm about one key requirement from the JD
          * Paragraph 2: Offer additional value (portfolio/work sample if relevant) and invite discussion
        - Closing: Mention cover letter, then professional sign-off

        **Example Flow:**
        "I recently applied for [role] at [company]..."
        "My experience in [JD requirement] makes me particularly excited about..."
        "As detailed in my attached cover letter, I would bring [value]..."
        "I'd welcome the opportunity to discuss..."

        **Style:**
        - Professional but warm tone
        - Focus on value you bring (not just features)
        - Cover letter reference should be brief and natural

        **Output Format:**
        Return ONLY the complete email text ready to send:
        
        Subject: Follow-Up on [Job Title] Application
        
        Dear [Recruiter's Name or Hiring Manager],
        
        [Paragraph 1: Application confirmation + 1 key qualification]
        [Paragraph 2: Value add + call to action]
        
        As mentioned in my attached cover letter, [brief reinforcement]. 
        
        Best regards,
        Raviteja
        """
    ],
    markdown=True
)

response = recruiter_email_agent.run(f"{JD}")
recruiter_email_agent.print_response(response.content)

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
task = " mail to "+recr_email+"; attach file : CL.txt "+response.content

result = agent_executor.invoke({"input": task})
print(result)

application_confirmation_agent = Agent(
    name="Application Confirmation Agent",
    role="Send me a confirmation email when my bot submits a job application",
    model=OpenAIChat("gpt-4.1-nano", temperature=0.1),
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        """
        **Strict Rules:**
        1. ALWAYS include the exact job title and company name if available
        2. Keep the email extremely concise (1-2 sentences)
        3. Include the application timestamp
        4. Use a simple, direct format

        **Required Elements:**
        - Job title
        - Company name
        - Date/time of application
        - Simple confirmation message

        **Output Format:**
        Return ONLY the email text ready to send:
        
        Subject: (Utej.ai) Application Submitted: [Job Title] at [Company]
        
        Your application for [Job Title] at [Company] was submitted successfully on [Timestamp].
        
        - Your Utej.ai 
        """
    ],
    markdown=False
)

response = application_confirmation_agent.run(f"{JD}")
application_confirmation_agent.print_response(response.content)

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
task = " mail to : r2raviteja@gmail.com; attach file : CL.txt "+response.content

result = agent_executor.invoke({"input": task})
