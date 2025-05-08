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


@controller.registry.action('Select radio button safely')
async def safe_radio_select(browser: BrowserContext, question: str, value: str):
    page = await browser.get_current_page()
    
    try:
        # Find radio group by question text
        question_element = await page.query_selector(f'label:has-text("{question}")')
        if not question_element:
            return ActionResult(error=f"Question '{question}' not found")
            
        # Find the specific radio option
        radio = await page.query_selector(f'input[type="radio"][value="{value}"]')
        if not radio:
            return ActionResult(error=f"Option '{value}' not found")
            
        # Check if already selected
        if await radio.is_checked():
            return ActionResult(extracted_content=f"'{value}' already selected")
            
        # Attempt selection
        await radio.click()
        await asyncio.sleep(1)  # Allow UI update
        
        # Verify selection
        if await radio.is_checked():
            return ActionResult(extracted_content=f"Successfully selected '{value}'")
        else:
            return ActionResult(error="Selection failed after click")
            
    except Exception as e:
        return ActionResult(error=f"Radio selection error: {str(e)}")

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
        
    }

# --- Main Function --- #
from langchain_openai import ChatOpenAI
llmo = ChatOpenAI(
    model= "gpt-4.1-mini" # "gpt-4.1-nano" # "gpt-3.5-turbo",  # Free model
)

llmg=ChatGoogleGenerativeAI(model= 'gemini-1.5-flash')
llmo=llmo

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
**Rules**:  
    1. **Strict No-Submit Policy**: Under no circumstances click any submit/save/next buttons.
    2. **Sequential Fill**: Process fields in order (top-to-bottom). Never backtrack. Scroll up by 70 px after each field and wait 2 seconds. 
    3. **Error Handling**: Attempt each field twice → if failed, leave blank and move on.  
    4. **Skip Voluntary**: Ignore any voluntary demographic questions.
    5. **Stop Condition**: When you reach the last form field, STOP IMMEDIATELY without any further action.
   
    **Steps**:  
    1. Navigate to {job_url}. Wait 2s. Click "Apply" if present.  
    2. **Fill Fields**:  
       - **Personal Info**: Use {personal_details} for standard fields (name, email, etc.).
       - **Open-Ended Questions**:
           - Answer using {cv_content} ( 4-5 sentences).
       - **Dropdowns**: Call 'Select location from dropdown'.
       - **Files**: Upload directly, call 'Upload a file directly without opening file picker'.  Never click on file upload button.  
           - Resume: {resume_path}  
           - Cover Letter: {coverLetter_path} (if exists).  
    3. **Radio Buttons**: Call "Select radio button safely".
    4. **Checkboxes**: Click first matching option (e.g., "Accept Terms").  
    5. **On Error**: Call `"Ask user for information"` for missing data.  

    **Quality Control**:
    - Avoid generic responses like "Interested in [Company]".
    - Use full sentences and professional tone.

    **Final Action**: When no more fields are visible below the last filled field, STOP COMPLETELY.
            """  

            ,

            f"""
            Call "Ask user for information", User will verify and input any missing fields manually.
            
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
                #extend_planner_system_message=extend_planner_system_message,
                controller=controller,
                browser=browser,
                browser_context=context,
                available_file_paths=available_file_paths,
                max_actions_per_step=5,
                
            )
            
            result = await agent.run()
            
            # Log the result of each task
            logger.info(f"Task {i + 1} completed with result: {result.final_result()}")
            
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
