import asyncio
from playwright.async_api import async_playwright

async def extract_visible_text(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        # Extract all visible text from the page
        visible_text = await page.evaluate("""
        () => {
            function getVisibleText(element) {
                if (!element) return '';
                if (element.nodeType === Node.TEXT_NODE) {
                    if (element.parentElement && window.getComputedStyle(element.parentElement).visibility !== 'hidden' && window.getComputedStyle(element.parentElement).display !== 'none') {
                        return element.textContent;
                    }
                    return '';
                }
                if (element.nodeType !== Node.ELEMENT_NODE) return '';
                const style = window.getComputedStyle(element);
                if (style.visibility === 'hidden' || style.display === 'none') return '';
                let text = '';
                for (const child of element.childNodes) {
                    text += getVisibleText(child);
                }
                return text;
            }
            return getVisibleText(document.body);
        }
        """)
        print(visible_text)
        return visible_text
        await browser.close()

url = "https://remotive.com/remote-jobs/data/senior-marketing-analyst-data-scientist-1991412"
raw_text = asyncio.run(extract_visible_text(url))

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

jd_preprocessing_agent = Agent(
    name="JD Preprocessing Agent",
    role="Extract and clean the main job description from raw, unstructured web page text.",
    model=OpenAIChat("gpt-4.1-nano"),
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "You will receive raw, unstructured text from a job board web page.",
        "Extract ONLY the main job description content, removing navigation, ads, footers, and unrelated sections.",
        "If possible, organize the output into sections: Title, Company, Location, Responsibilities, Requirements, Benefits, How to Apply, etc.",
        "Return the cleaned job description as a single string, ready for further processing.",
        "Do NOT add any commentary or extra text outside the cleaned job description.",
    ],
    markdown=True,
)

# raw_text = asyncio.run(extract_visible_text(job_url))

task = f"""
Extract and clean the main job description from the following raw web page text:

{raw_text}
"""

response = jd_preprocessing_agent.run(task)
cleaned_jd = response.content.strip()
with open("JD.txt", "w", encoding="utf-8") as f:
    f.write(cleaned_jd)
print(cleaned_jd)