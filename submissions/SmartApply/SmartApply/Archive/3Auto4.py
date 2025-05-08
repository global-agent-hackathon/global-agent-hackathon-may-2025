import os
import sys
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.agent.views import ActionResult

import anyio

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
    )
)
controller = Controller()

import pandas as pd
df = pd.read_csv(r"JobsData.csv")
num_job = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # Default to 0 if not provided
job_url = df["Apply_URL"].iloc[num_job]
with open("JD.txt", "w", encoding="utf-8") as f:
    f.write(df["Combined"].iloc[num_job])

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
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[0])
            await file_inputs[0].set_input_files(resume_path)
            
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[1])
            await file_inputs[1].set_input_files(coverLetter_path)
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


@controller.action('Read file content from available file paths')
async def read_file(path: str, file_path: list[str]):
    if path not in file_path:
        return ActionResult(error=f'File path {path} is not available')

    async with await anyio.open_file(path, 'r') as f:
        content = await f.read()
    logger.info(f'Read file content: {content[:100]}...')  # Only log first 100 chars
    return ActionResult(extracted_content=content, include_in_memory=True)

@controller.registry.action('Handle text input with dropdown')
async def handle_text_with_dropdown(field_selector: str, text_value: str, browser: BrowserContext):
    try:
        page = await browser.get_current_page()
        
        # Type the text value
        element = await page.query_selector(field_selector)
        if not element:
            return ActionResult(error=f"Could not find input field with selector: {field_selector}")
            
        await element.fill(text_value)
        
        # Wait for dropdown to appear (3 seconds)
        await asyncio.sleep(3)
        
        # Try to find and click the first matching option in dropdown
        dropdown_options = await page.query_selector_all('ul[role="listbox"] li, .dropdown-menu li, [role="option"]')
        if dropdown_options:
            for option in dropdown_options:
                option_text = await option.text_content()
                if text_value.lower() in option_text.lower():
                    await option.click()
                    return ActionResult(extracted_content=f"Successfully entered {text_value} and selected from dropdown")
                    
        # If no dropdown appeared or no match found, just keep the typed text
        return ActionResult(extracted_content=f"Entered {text_value}, no matching dropdown option found")
        
    except Exception as e:
        return ActionResult(error=f"Failed to handle text with dropdown: {str(e)}")

# --- Personal Details --- #
@controller.action('Fetch my personal details for form filling')
async def fetch_personal_details():
    personal_details = {
        "Email": "r2raviteja@gmail.com",
        "password": "-",
        "First name": "Raviteja",
        "middle name": "",
        "Last name": "Rachamadugu",
        "Phone number": "15216442399",
        "Language": "English",
        "Secondary Phone": None,
        "Street Address": "8",
        "City": "Munich",
        "State": "Germany",
        "Zip / Postal Code": None,
        "Country": "Germany",
        "LinkedIn profile": "https://www.linkedin.com/in/rraviteja/"
    }
    logger.info(f'Fetched personal details.')
    return ActionResult(extracted_content=str(personal_details), include_in_memory=True)

@controller.registry.action('Select an option from a dropdown by visible text')
async def select_dropdown_by_text(dropdown_selector: str, option_text: str, browser: BrowserContext):
    try:
        page = await browser.get_current_page()
        
        # Find the dropdown element
        dropdown = await page.query_selector(dropdown_selector)
        if not dropdown:
            return ActionResult(error=f"Could not find dropdown with selector: {dropdown_selector}")
            
        # Click the dropdown to open it
        await dropdown.click()
        await asyncio.sleep(1)  # Wait for dropdown to open
        
        # Find all options (common selectors for dropdown options)
        option_selectors = [
            'option',  # Standard HTML select options
            'li[role="option"]',  # Common ARIA pattern
            '.dropdown-item',  # Bootstrap style
            '.select-dropdown li',  # Materialize style
            '[role="listbox"] [role="option"]'  # ARIA listbox pattern
        ]
        
        # Try each selector pattern until we find options
        options = []
        for selector in option_selectors:
            options = await page.query_selector_all(selector)
            if options:
                break
                
        if not options:
            return ActionResult(error="No dropdown options found with common selectors")
            
        # Find and click the matching option
        for option in options:
            text = await option.text_content()
            if option_text.lower() in text.lower():
                await option.click()
                return ActionResult(extracted_content=f"Selected '{option_text}' from dropdown")
                
        return ActionResult(error=f"Option with text '{option_text}' not found in dropdown")
        
    except Exception as e:
        return ActionResult(error=f"Failed to select dropdown option: {str(e)}")

@controller.registry.action('Fill location fields with dropdown selection')
async def fill_location_with_dropdown(field_selector: str, value: str, browser: BrowserContext):
    try:
        page = await browser.get_current_page()
        
        # Find the input field
        element = await page.query_selector(field_selector)
        if not element:
            return ActionResult(error=f"Could not find location field with selector: {field_selector}")
            
        # Clear the field first
        await element.fill('')
        await asyncio.sleep(0.5)
        
        # Type the value character by character with 1 second delays
        for char in value:
            await element.type(char)
            await asyncio.sleep(1)  # 1 second delay between characters
            
        # Wait longer for dropdown to appear (location services can be slow)
        await asyncio.sleep(3)
        
        # Try to find the dropdown options (common selectors for location dropdowns)
        dropdown_options = await page.query_selector_all(
            '.pac-container .pac-item, .autocomplete-dropdown li, ul[role="listbox"] li, [role="option"]'
        )
        
        if dropdown_options:
            best_match = None
            best_score = 0
            
            # Find the option that best matches our value
            for option in dropdown_options:
                option_text = await option.text_content()
                option_text = option_text.strip()
                
                # Simple matching - could be enhanced
                match_score = sum(
                    1 for word in value.lower().split() 
                    if word in option_text.lower()
                )
                
                if match_score > best_score:
                    best_score = match_score
                    best_match = option
            
            if best_match:
                await best_match.click()
                return ActionResult(
                    extracted_content=f"Filled location field with '{value}' and selected best match: '{await best_match.text_content()}'"
                )
            else:
                # If no good match, just click the first option
                await dropdown_options[0].click()
                return ActionResult(
                    extracted_content=f"Filled location field with '{value}' and selected first option: '{await dropdown_options[0].text_content()}'",
                    warning="No perfect match found in dropdown"
                )
                
        return ActionResult(
            extracted_content=f"Filled location field with '{value}' but no dropdown appeared",
            warning="No location dropdown appeared after typing"
        )
        
    except Exception as e:
        return ActionResult(error=f"Failed to fill location field: {str(e)}")

@controller.registry.action('Select a radio button by value')
async def select_radio_button(group_name: str, value: str, browser: BrowserContext):
    try:
        page = await browser.get_current_page()
        
        # Try different ways to find radio buttons
        selectors = [
            f'input[type="radio"][name="{group_name}"][value="{value}"]',
            f'input[type="radio"][name="{group_name}"] + label:has-text("{value}")',
            f'label:has-text("{value}") input[type="radio"]'
        ]
        
        for selector in selectors:
            element = await page.query_selector(selector)
            if element:
                await element.click()
                return ActionResult(extracted_content=f"Selected radio button '{value}' in group '{group_name}'")
                
        return ActionResult(error=f"Could not find radio button with value '{value}' in group '{group_name}'")
        
    except Exception as e:
        return ActionResult(error=f"Failed to select radio button: {str(e)}")

@controller.registry.action('Select a checkbox by label')
async def select_checkbox(label_text: str, browser: BrowserContext):
    try:
        page = await browser.get_current_page()
        
        # Try different ways to find checkboxes
        selectors = [
            f'input[type="checkbox"] + label:has-text("{label_text}")',
            f'label:has-text("{label_text}") input[type="checkbox"]',
            f'input[type="checkbox"][aria-label*="{label_text}"]'
        ]
        
        for selector in selectors:
            element = await page.query_selector(selector)
            if element:
                await element.click()
                return ActionResult(extracted_content=f"Selected checkbox with label '{label_text}'")
                
        return ActionResult(error=f"Could not find checkbox with label '{label_text}'")
        
    except Exception as e:
        return ActionResult(error=f"Failed to select checkbox: {str(e)}")

personal_details = {
        "Email": "r2raviteja@gmail.com",
        "password": "QWERTYu123456&",
        "First name": "Raviteja",
        "middle name": "",
        "Last name": "Rachamadugu",
        "Phone number": "15216442399",
        "Language": "English",
        "Secondary Phone": None,
        "Street Address": None,
        "City": "Munich",
        "State": "Germany",
        "Zip / Postal Code": None,
        "Country": "Germany",
        "Salary":"60000",
        "Notice period":"1 month",
        "LinkedIn profile": "https://www.linkedin.com/in/rraviteja/"
    }

# --- Main Function --- #
from langchain_openai import ChatOpenAI
llmo = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key= "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",
    model= "google/gemini-2.0-flash-exp:free",  # Free model
)

from langchain_groq import ChatGroq
llmq = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.7
)

llmg=ChatGoogleGenerativeAI(model='gemini-1.5-flash')
llmg=llmg

async def main():
    resume_path = Path('C:/Users/960ra/PycharmProjects/SmartApply/CV.pdf').resolve()
    coverLetter_path = Path('C:/Users/960ra/PycharmProjects/SmartApply/User/CL.docx').resolve()
    available_file_paths = [str(resume_path),str(coverLetter_path)]

    task = f"""
    Your main task is to successfully apply for the job. Think smartly and fill the form fields sequentially by index order.
    There will be many questions; the answers below are just for reference. Do not treat them as steps.
    Continue filling each field one by one until you reach the end page or submit the form.

    Instructions:
    1. Navigate to the job URL: {job_url}. (There may be remnants from a previous agent on another website.)
    2. Wait 1 second for the page to load. After clicking the apply button, the page may reload; start filling fields there.
    3. Use the provided  {personal_details} to fill in user information fields.
    4. Fill input fields in index order; proceed to the next only after filling the current field.
    5. Leave fields blank if no data is available and they are not mandatory.
    6. Wait 1 second after filling each field, then scroll up slightly.
    7. For file uploads, do not click. Instead, call "Upload a file directly without opening file picker" and provide:
        - Resume: {resume_path}
        - Cover letter: {coverLetter_path}
    8. If a question asks about:
        - User past experience,
        - Tools or platforms used,
        - Background, expertise, or projects,
       then call "Read file content from available file paths" and provide: file_path: {resume_path}
    9. Submit the form after filling all fields.
    10. Move only forward; do not retry previous steps. If unsure, skip.
    11. After clicking the 'Submit' button:
        - Wait 3–5 seconds.
        - Check if the page scrolls automatically, highlights any fields in red, or shows error messages.
        - If any required field is missing or marked invalid, do NOT consider the task successful.
        - Instead, extract and log the names or labels of the missing fields.
        - Try to fill the missing details again if possible.
    """

    agent = Agent(
        task=task,
        llm=llmg,
        controller=controller,
        browser=browser,
        available_file_paths=available_file_paths,
    )

    result = await agent.run()  # ⬅️ Capture the result

    await browser.close()

    # Save the output to a file
    output_file = Path('agent_output.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(result))

    
    #input('Press Enter to exit...')

# --- Entry Point --- #

if __name__ == '__main__':
    asyncio.run(main())
