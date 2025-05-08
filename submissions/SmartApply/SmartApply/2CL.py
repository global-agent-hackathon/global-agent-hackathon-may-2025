import os
import json
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
openai_api_key = os.environ["OPENAI_API_KEY"]
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
os.environ["GROQ_API_KEY"]
os.environ["OPENROUTER_API_KEY"]
os.environ["FIRECRAWL_API_KEY"]
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
import pandas as pd
import sys

def CL_gen(num_job):
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
        
    JD, CV = load_cv_jd(jd,cv)
    #print(JD)

    from datetime import datetime
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from agno.tools.reasoning import ReasoningTools

    # Final Premium Cover Letter Agent
    cover_letter_agent = Agent(
        name="Premium Cover Letter Writer",
        role="Craft world-class, ready-to-submit cover letters",
        model=OpenAIChat(id="gpt-4.1-nano"),
        tools=[ReasoningTools(add_instructions=True)],
        instructions=[
            "GENERAL RULES:",
            "1. Write a fully polished, powerful cover letter ready for direct submission.",
            "2. 3/4 page to 1 full page (300-400 words).",
            "3. Use professional but conversational tone.",
            "4. Showcase 4+ achievements with real metrics, technologies, and impact.",
            "5. No clichés like 'hardworking' or 'team player'.",
            "6. Tailor perfectly to the job and company.",
            "7. Finish with a strong closing and a polite call to action.",
            "HEADER AND STRUCTURE RULES:",
            "1. Start with applicant's full name, email, phone, city, country.",
            "2. Today's date (example: April 27, 2025), clean, no brackets.",
            "3. Company Address: Hiring Manager, Company Name, City, Country.",
            "4. Salutation: 'Dear Hiring Manager,'",
            "5. Write five paragraphs following the structure below:",
            "    - Introduction: Why you're applying and your excitement for the role.",
            "    - Skills and Achievements: 2-3 specific achievements tied to job needs.",
            "    - Fit for the Role: Show how your skills match their needs.",
            "    - Passion and Motivation: Why you’re drawn to the company and role.",
            "    - Closing: Call to action, thanking them for their time.",
            "TASK INSTRUCTIONS:",
            "1. Read the provided resume (CV) and job description (JD).",
            "2. Highlight key achievements and skills from the resume.",
            "3. Tailor the cover letter to match the job requirements in JD.",
            "4. Use professional language but keep a slight personal touch.",
            "5. Showcase 4+ achievements with real metrics, technologies, and impact.",
            "6. Be enthusiastic about the opportunity, closing with a call to action."
            "STRICT OUTPUT RULES:",
        "1. ONLY output the final cover letter text, nothing else.",
        "2. DO NOT include any introductory sentences, explanations, or follow-up questions.",
        "3. DO NOT add phrases like 'Here’s the final polished cover letter:' or 'Would you like me to format this further?'",
        "4. The output MUST start directly with the applicant's contact info and end with 'Sincerely, [Name]'.",
        "5. If the user asks for changes, regenerate the ENTIRE letter without commentary.",
        ],
        markdown=True
    )

    def generate_final_cover_letter(applicant_info, company_info, resume, job_description):
        today = datetime.today().strftime('%B %d, %Y')

        task = f"""
        Applicant Information:
        - Name: {applicant_info['name']}
        - Email: {applicant_info['email']}
        - Phone: {applicant_info['phone']}
        - Location: {applicant_info['location']}

        Date: {today}

        Company Information:
        - Hiring Manager: {company_info['hiring_manager']}
        - Company Name: {company_info['company_name']}
        - Location: {company_info['company_location']}

        Resume (CV):
        {resume}

        Job Description (JD):
        {job_description}

        Structure:
        [Your Full Name]  
        [Your Email]  
        [Your Phone Number]  
        [Your City, Country]  

        Date: [Today's Date]

        Dear Hiring Manager,

        Body

        Sincerely,  
        [Your Full Name]

        Instructions:
        - Write a full cover letter using the above details, following this structure:
        1. **Introduction**: State why you are applying, and express enthusiasm about the role.
        2. **Skills and Achievements**: Showcase 2-3 specific achievements from your resume, including metrics, technologies, and impact.
        3. **Fit for the Role**: Connect your experience to the skills and responsibilities mentioned in the job description. Show how you are a great match for the role.
        4. **Passion and Motivation**: Talk about why you are excited about the company and the role, and how they align with your values or career goals.
        5. **Closing**: Close with a polite call to action, thanking the hiring manager and expressing interest in discussing further.
        - Use a professional but slightly personal tone.
        - End with a clear and positive call to action.
        """

        return cover_letter_agent.run(task)

    if __name__ == "__main__":
        # Example dynamic input
        applicant_info = {
            "name": "Raviteja R",
            "email": "r2raviteja@gmail.com",
            "phone": "+49 15216 442399",
            "location": "Munich, Germany"
        }
        company_info = {
            "hiring_manager": "Hiring Manager",
            "company_name": "Blacklane",
            "company_location": "Berlin, Germany"
        }
        
        # Pass your resume (CV) and job description (JD) here as strings
        resume = CV #"""[Your resume text here]""" 
        job_description = JD # """[Job description text here]"""

        # Generate and print cover letter
        cover_letter = generate_final_cover_letter(applicant_info, company_info, resume, job_description)
        cover_letter_agent.print_response(cover_letter.content)

    with open("CL.txt", 'w', encoding='utf-8') as f:
            f.write(cover_letter.content)
    with open("CL.docx", 'w', encoding='utf-8') as f:
            f.write(cover_letter.content)
    with open("CV.txt", 'w', encoding='utf-8') as f:
            f.write(CV)
    df.at[num_job, "Coverletter"] = cover_letter.content
    df.to_csv("JobsData2.csv",index=False)

    from agno.agent import Agent
    from agno.models.openai import OpenAIChat

    cover_letter_review_agent = Agent(
        name="Cover Letter Review Agent",
        role="Strictly evaluate if a cover letter meets minimum criteria and score it (0-100)",
        model=OpenAIChat(id="gpt-4.1-nano"),
        instructions=[
            "GENERAL RULES:",
            "1. Score the cover letter **0-100** based ONLY on structural completeness, not content quality.",
            "2. Deduct points if sections are missing or incomplete (see scoring rubric).",
            "3. Output ONLY the score and missing sections (no explanations).",
            "",
            "SCORING RUBRIC:",
            "- **0/100**: Missing 3+ core sections OR severely truncated (e.g., only 1 paragraph).",
            "- **30/100**: Missing 2 core sections (e.g., no header, no closing).",
            "- **60/100**: Missing 1 core section (e.g., no call to action).",
            "- **80/100**: All sections present but too short (e.g., achievements lack metrics).",
            "- **100/100**: Fully structured with header, 5 paragraphs, metrics, and closing.",
            "",
            "CORE SECTIONS (must all exist for 60+ score):",
            "1. Header (Name, Email, Phone, Location, Date)",
            "2. Company Address Block",
            "3. Salutation ('Dear Hiring Manager,')",
            "4. Five paragraphs (Introduction, Skills, Fit, Motivation, Closing)",
            "5. Call to action + 'Sincerely, [Name]'",
            "",
            "OUTPUT FORMAT:",
            "Score: [X]/100 | Missing: [list missing sections or 'None']"
        ],
        markdown=True
    )

    def evaluate_cover_letter(cover_letter_text: str) -> str:
        task = f"""
        Evaluate this cover letter strictly against the scoring rubric:

        {cover_letter_text}
        """
        return cover_letter_review_agent.run(task)

    cover_letter_review_agent.print_response(cover_letter.content)
    #print(evaluate_cover_letter(cover_letter.content))  # Output: "Score: 30/100 | Missing: Company Address Block, Five paragraphs"



df = pd.read_csv(r"JobsData.csv")
"""num_job = len(df)
#num_job = 10
for i in range(num_job):
    if (df["score"].iloc[i]>60):
        CL_gen(i)
"""

num_job = 0
print(num_job)
num_job = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # Default to 0 if not provided

#print(df["score"].iloc[num_job])
if (df["score"].iloc[num_job]>=60):
    CL_gen(num_job)

df.to_csv("JobsData.csv",index=False)
df2 = df[['Title', 'Company', 'Location', "score","reason","recruiter_email", 'Description',"Coverletter"]]
df2 = df2.replace(',', '', regex=True)
df2.to_csv("JobsData2.csv",index=False)