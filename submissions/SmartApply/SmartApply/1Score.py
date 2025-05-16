import os
import json
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
import sys
import pandas as pd
def score(num_job):
    with open("JD.txt", "w", encoding="utf-8") as f:
        f.write(df["Combined"].iloc[num_job])

    def load_file(file_path: str):
        """
        Load content from a PDF, Word, or text file.
        """
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError("Unsupported file format. Please provide a .pdf, .docx, or .txt file.")
        documents = loader.load()
        return documents#"\n".join([doc.page_content for doc in documents])


    # Paths to the job description and resume files
    jd = "JD.txt"  # Replace with your file path
    cv = "CV.pdf"  # Replace with your file path

    def load_cv_jd(jd1= None, cv1= None):

        # Load the files
        try:
            job_description = load_file(jd1)
            resume1 = load_file(cv1)
            
            rjd = "\n".join([doc.page_content for doc in job_description])
            rcv = "\n".join([doc.page_content for doc in resume1])
            return rjd, rcv
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None
        
    JD, CV = load_cv_jd(jd,cv)
    #print(CV)


    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from agno.tools.reasoning import ReasoningTools

    resume_match_scorer_agent = Agent(
        name="Resume Match Scorer",
        role="Evaluate how well a given resume (CV) matches a provided Job Description (JD)",
        model=OpenAIChat("gpt-4.1-nano"),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=[
            "Compare the provided Resume (CV) and Job Description (JD).",
            "Analyze relevant aspects like skills, experience, education, certifications, and job requirements.",
            "Score the match between 0 and 100, where 100 means 'perfect match' and 0 means 'no match'.",
            "Consider how closely the resume's skills and experience align with the JD requirements.",
            "If important skills or experiences are missing, reduce the score proportionally.",
            "Return the output strictly as a JSON object with the following format: {\"match_score\": float, \"reasoning\": string}",
            "In 'reasoning', briefly explain why the score was given (2-4 lines).",
            "Do not add any extra text outside the JSON (no ```json block or commentary).",
        ],
        markdown=True,
    )

    query = " Compare both  Resume : [ " + CV + " ], Job description [" +JD+ " ] "
    response = resume_match_scorer_agent.run(query)
    resume_match_scorer_agent.print_response(response.content)

    import json

    # Assuming llmresponse.content is your model output
    raw_output = response.content.strip()

    # Try parsing as JSON
    try:
        parsed = json.loads(raw_output)
        score = parsed.get("match_score")
        reason = parsed.get("reasoning")
        #print("Score:", score)
        #print("Reason:", reason)
    except json.JSONDecodeError:
        print("Failed to parse JSON.")

    email_extractor_agent = Agent(
        name="Email Extractor",
        role="Extract email addresses from job descriptions",
        model=OpenAIChat("gpt-4.1-nano"),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=[
            "Extract any email addresses found in the provided text.",
            "Return ONLY the email address if found.",
            "If no email is found, return an empty string.",
            "Do not include any additional text, JSON formatting, or explanations.",
        ],
        markdown=False,  # disable Markdown formatting
    )
    # Test the email extractor
    query_email = "Extract email from this text: [" + JD + "]"  # Using CV instead of JD since it contains an email
    response_email = email_extractor_agent.run(query_email)
    #print(response_email.content.strip())  # strip() removes any extra whitespace
    recruiter_email = response_email.content

    # Update only the 9th row
    df.at[num_job, "score"] = score
    df.at[num_job, "reason"] = reason
    df.at[num_job, "recruiter_email"] = recruiter_email

    """
    # Read the content from CL.txt
    with open('CL.txt', 'r') as file:
        cl_content = file.read()

    # Assign the content to the DataFrame cell
    df.at[8, "Coverletter"] = cl_content
    """

    language_finder_agent = Agent(
        name="Language Finder",
        role="Check if a text contains only English and no mention of other languages.",
        model=OpenAIChat("gpt-4.1-nano"),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=[
            "Read the input text carefully.",
            "If any word refers to another language (like 'German', 'French', 'Spanish', etc.), even if written in English, return score 0.",
            "Only return score 1 if the text has no mention of any other language and is fully in English.",
            "Ignore context. Just the presence of any other language name means score 0.",
            "Return JSON only: {\"language_score\": int, \"reason\": string}",
            "In 'reasoning', clearly say which word caused score 0.",
            "No extra text or formatting outside the JSON.",
        ],
        markdown=True,
    )
    query = "Analyze this text for non-English content: [" + JD + "]"
    response = language_finder_agent.run(query)
    language_finder_agent.print_response(response.content)

    # Assuming llmresponse.content is your model output
    raw_output = response.content.strip()

    # Try parsing as JSON
    try:
        parsed = json.loads(raw_output)
        score = parsed.get("language_score")
        reason = parsed.get("reason")
        #print("Score:", score)
        #print("Reason:", reason)
    except json.JSONDecodeError:
        print("Failed to parse JSON.")

    if score==0:
        #print(1)
        df.at[num_job, "score"] = score
        df.at[num_job, "reason"] = reason

    df.to_csv("JobsData.csv",index=False)
    df2 = df[['Title', 'Company', 'Location', "score","reason","recruiter_email", 'Description',"Coverletter"]]
    df2 = df2.replace(',', '', regex=True)
    df2.to_csv("JobsData2.csv",index=False)

df = pd.read_csv(r"JobsData.csv")
num_job = 0
num_job = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # Default to 0 if not provided

#for i in range(2):
score(num_job)