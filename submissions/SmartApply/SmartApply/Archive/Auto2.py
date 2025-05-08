import os
import time
import pyautogui  # NEW import for file upload simulation
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
openai_api_key = os.environ["OPENAI_API_KEY"]

from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

# Step 1: Create a helper function to handle file upload popup
def upload_file_popup(file_path):
    print("Waiting for upload popup to appear...")
    time.sleep(2)  # Wait for popup to open (adjust if needed)
    pyautogui.write(file_path)
    time.sleep(1)
    pyautogui.press('enter')
    print("File path entered and submitted!")

# Step 2: Configure the browser
browser = Browser(
    config=BrowserConfig(
        chrome_instance_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',  # corrected path with raw string
    )
)

# Step 3: Personal details dictionary
personal_details = {
    "Email": "r2raviteja@gmail.com",
    "password": "-",
    "First name": "Raviteja",
    "middle name": "",
    "Last name": "Rachamadugu",
    "Phone number": "+49 15216 442399",
    "Language": "English",
    "Secondary Phone": None,
    "Street Address": None,
    "City": "Munich",
    "State": "Germany",
    "Zip / Postal Code": None,
    "Country": "Germany",
    "LinkedIn profile": "https://www.linkedin.com/in/rraviteja/"
}

# Step 4: Create the agent
agent = Agent(
    task=f"""
    Apply for the Data Analyst position at ESDS by filling the form fields in sequential order.

    Context:
    Here are the user's personal details: {personal_details}

    Instructions:
    1. Navigate to: https://jobs.ashbyhq.com/taxfix.com/b9706f28-08c6-4163-a4cd-9f322368fbc6
    2. Wait for page load (5 seconds)
    3. After page load, detect input fields by their index order (starting from 0).
    4. Fill each input field in the strict forward sequence (index 0, 1, 2, 3, etc.).
       - Match the field label to the best possible entry from the given personal details.
       - If no matching detail is available, leave the field blank and move to the next index.
    5. After filling a field, wait 5 seconds before moving to the next.
    6. For file uploads like Resume:
       - Click on the Upload button to trigger the file picker popup.
       - Wait 2 seconds.
       - Then simulate typing the file path and press Enter automatically using an external helper (don't wait for user manually).
       - Use this file path: C:/Users/960ra/PycharmProjects/SmartApply/CV.pdf
    7. After all fields are processed, submit the form.

    Important Rules:
    - Only move forward (never go back to previous fields)
    - If a field is missing or doesn't match any data, skip it without stopping
    - Don't spend extra time searching deeply for fields — only fill by index
    - Don't modify fields already filled
    - Strictly maintain 5 seconds pause between each field
    """,
    llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp'),
    browser=browser,
)

# Step 5: Define main function
async def main():
    await agent.run()

    # After agent fills everything and clicks upload, simulate the file upload
    upload_file_popup(r'C:/Users/960ra/PycharmProjects/SmartApply/CV.pdf')

    input('Press Enter to close the browser...')
    await browser.close()

# Step 6: Run
if __name__ == '__main__':
    asyncio.run(main())
