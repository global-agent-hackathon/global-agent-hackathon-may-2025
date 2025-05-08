import os
import platform
import sys
import asyncio
import logging
from pathlib import Path
import json
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.agent.views import ActionResult

import anyio

from patchright.async_api import BrowserContext

# Load environment variables
_ = load_dotenv(find_dotenv())

# Setup logging
logger = logging.getLogger(__name__)

# Add parent directory to system path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Browser and Controller
browser = Browser(
    config=BrowserConfig(
        headless=False,
        chrome_instance_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        ))
controller = Controller()

import pandas as pd
df = pd.read_csv(r"JobsData.csv")
num_job = 0
num_job = int(sys.argv[1]) if len(sys.argv) > 1 else 6  # Default to 0 if not provided

job_url = df["Apply_URL"].iloc[num_job]

with open("CL.txt", "w", encoding="utf-8") as f:
    f.write(df["Coverletter"].iloc[num_job])


# --- Actions --- #
@controller.registry.action('Upload a file directly without opening file picker')
async def upload_resume_and_cover_letter(resume_path: str, coverLetter_path: str, browser: BrowserContext):
    import os
    if not os.path.isfile(resume_path):
        return ActionResult(error=f"Resume file '{resume_path}' does not exist.")
    if not os.path.isfile(coverLetter_path):
        return ActionResult(error=f"Cover letter file '{coverLetter_path}' does not exist.")

    page = await browser.get_current_page()

    # Find all input[type="file"] elements
    file_inputs = await page.query_selector_all('input[type="file"]')
    num_inputs = len(file_inputs)
    
    if num_inputs == 0:
        return ActionResult(error="No file input fields found on the page.")
        
    try:
        if num_inputs == 1:
            # If only one input, upload resume
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[0])
            await file_inputs[0].set_input_files(resume_path)
            return ActionResult(extracted_content="Uploaded resume to single file input.")
            
        elif num_inputs == 2:
            # If two inputs, upload resume first, then cover letter
            #await page.evaluate("(element) => element.style.display = 'block'", file_inputs[0])
            #await file_inputs[0].set_input_files(resume_path)
            
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[1])
            await file_inputs[1].set_input_files(resume_path)#coverLetter_path)
            return ActionResult(extracted_content="Uploaded resume and cover letter to two file inputs.")
            
        elif num_inputs >= 3:
            # If three or more inputs, use specific indices
            # Resume goes to index 1, cover letter to index 2
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[1])
            await file_inputs[1].set_input_files(resume_path)
            
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[2])
            await file_inputs[2].set_input_files(coverLetter_path)
            return ActionResult(extracted_content="Uploaded resume and cover letter to specific file inputs (indices 1 and 2).")

        return ActionResult(extracted_content=f"Successfully handled file uploads for {num_inputs} file input(s).")
    except Exception as e:
        return ActionResult(error=f"Upload failed: {str(e)}")

@controller.action('Ask user for information')
def ask_human(question: str) -> str:
    answer = input(f'\n{question}\nInput: ')
    return ActionResult(extracted_content=answer)

@controller.registry.action('Select location from dropdown')
async def select_location_from_dropdown(browser: BrowserContext, location: str):
    try:
        page = await browser.get_current_page()
        
        # Wait for and find the location input field using the specific class and role
        location_input = await page.wait_for_selector('input[role="combobox"]._input_v5ami_28', timeout=5000)
        if not location_input:
            return ActionResult(error="Could not find location input field")
        
        # Clear existing value and type the location
        await location_input.click()
        await location_input.fill("")  # Clear first
        await location_input.type(location, delay=200)  # Type slowly to trigger suggestions
        
        # Wait for dropdown options to appear
        await page.wait_for_timeout(2000)  # Wait for suggestions to load
        
        # Look for the suggestion list and first option
        suggestion_list = await page.wait_for_selector('[role="listbox"]', timeout=6000)
        if suggestion_list:
            # Find all options
            options = await page.query_selector_all('[role="option"]')
            if options and len(options) > 0:
                # Click the first option
                await options[0].click()
                return ActionResult(extracted_content=f"Successfully selected location: {location}")
            
        return ActionResult(error="Could not find location suggestions")
            
    except Exception as e:
        return ActionResult(error=f"Failed to select location: {str(e)}")

with open("CV.txt", "r") as file:
    cv_content = file.read()

personal_details = {
        "Email": "r2raviteja@gmail.com",
        "First name": "Raviteja",
        "Last name": "Rachamadugu",
        "Phone number": "15216442399",
        "Language": "English",
        "City": "Munich",
        "State": "Germany",
        "Zip / Postal Code": None,
        "Country": "Germany",
        "Salary":"60000",
        "Notice period":"1 month",
        "LinkedIn profile": "https://www.linkedin.com/in/rraviteja/",
        "github":"https://github.com/r6raviteja/utej",
        "Portfolio":"https://rraviteja.in",
        "Where did you here about us":"Linkedin",
        "Pronouns":"He/him",
    }

# --- Main Function --- #
from langchain_openai import ChatOpenAI
llmo = ChatOpenAI(
    model="gpt-3.5-turbo",  # Free model
)

from langchain_groq import ChatGroq
llmq = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.7
)

llmg=ChatGoogleGenerativeAI(model= "gemini-2.0-flash-exp")#model='gemini-1.5-flash')
llmg=llmg

async def main():
    async with await browser.new_context() as context:
        resume_path = Path('C:/Users/960ra/PycharmProjects/SmartApply/CV.pdf').resolve()
        coverLetter_path = Path('C:/Users/960ra/PycharmProjects/SmartApply/User/CL.docx').resolve()
        user_image_path = Path('C:/Users/960ra/PycharmProjects/SmartApply/User/pic.jpeg').resolve()
        available_file_paths = [str(resume_path), str(coverLetter_path), str(user_image_path)]
        #job_url = "https://jobs.ashbyhq.com/kin/30278e35-0b41-4290-8328-026153619a1f/application?utm_source=remotive.com&ref=remotive.com"


        # Define all tasks
        tasks = [

            f"""
                Rules:

                Strict Order: Fill fields one by one. Never return to completed fields.

                Attempt Limit: Try twice per field. If unsolved, leave blank and move next.

                Pause: After each field, scroll up and wait 3 seconds.

                Steps:

                Navigate to {job_url}. Wait 2 seconds. Click "Apply" if visible.

                Fill Fields:

                Use {personal_details} for personal info.

                Use {cv_content} for skills/experience (2-3 sentences).

                For dropdowns: Call "Select location from dropdown".

                For files: Call "Upload a file directly":

                Resume: {resume_path}

                Cover Letter: {coverLetter_path} (if exists).

                Checkboxes/Radio Buttons: Click relevant options (e.g., terms acceptance).

                If Stuck: Call "Ask user for information".

                Final Action: Stop after last field. Hand off to next agent. Do not submit.

                Note: No dummy data. Proceed sequentially. Prioritize accuracy over speed.
            """,

            f"""
            Call "Ask user for information" before clicking submit, User will input any missing fields manually.
            
            If user inputs "I confirm" then Submit and verify application status.
            Wait 3 seconds
            Don't consider task as success until you see a success screen or message.
            
            """
        ]

        # Create and run agents sequentially
        previous_result = None
        for i, task in enumerate(tasks):
            logger.info(f"Starting task {i + 1}: {task}")
            print(" Agent :"+str(i+1)+" starts here")
            agent = Agent(
                task=task,
                llm=llmg,
                planner_llm=llmo,
                controller=controller,
                browser=browser,
                browser_context=context,
                available_file_paths=available_file_paths,
                max_actions_per_step=5,
                
            )
            
            result = await agent.run()
            
            # Log the result of each task
            logger.info(f"Task {i + 1} completed with result: {result.final_result()}")
            
            """
            # If there's an error, log it and break
            if result.has_errors():
                logger.error(f"Error in task {i + 1}: {result.final_result()}")
                break
            """
            previous_result = result

        await browser.close()

        final_result = result.final_result()
        is_done = result.is_done()
        has_errors = result.has_errors()
        model_thoughts = result.model_thoughts()
        action_results = result.action_results()

        # Create a dictionary with all the data
        result_data = {
            "Final Result": final_result,
            "Is Done": is_done,
            "Has Errors": has_errors,
            "Model Thoughts": model_thoughts,
            "Action Results": action_results,
        }
        from json import JSONEncoder
        class CustomEncoder(JSONEncoder):
            def default(self, obj):
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                elif isinstance(obj, (list, tuple)):
                    return [self.default(item) for item in obj]
                elif isinstance(obj, dict):
                    return {key: self.default(value) for key, value in obj.items()}
                else:
                    return super().default(obj)


        # Save as JSON file
        output_file = Path('agent_output.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, cls=CustomEncoder, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    asyncio.run(main())
