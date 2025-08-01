import asyncio
from playwright import async_api

async def run_test():
    pw = None
    browser = None
    context = None
    
    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()
        
        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",         # Set the browser window size
                "--disable-dev-shm-usage",        # Avoid using /dev/shm which can cause issues in containers
                "--ipc=host",                     # Use host-level IPC for better stability
                "--single-process"                # Run the browser in a single process mode
            ],
        )
        
        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        context.set_default_timeout(5000)
        
        # Open a new page in the browser context
        page = await context.new_page()
        
        # Navigate to your target URL and wait until the network request is committed
        await page.goto("http://localhost:3000", wait_until="commit", timeout=10000)
        
        # Wait for the main page to reach DOMContentLoaded state (optional for stability)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=3000)
        except async_api.Error:
            pass
        
        # Iterate through all iframes and wait for them to load as well
        for frame in page.frames:
            try:
                await frame.wait_for_load_state("domcontentloaded", timeout=3000)
            except async_api.Error:
                pass
        
        # Interact with the page elements to simulate user flow
        # Click on 'Patient Login' to proceed to patient login page.
        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/div/a').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # Input patient ID 'Abhinav' in the Phone or Patient ID field and click Send OTP.
        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('Abhinav')
        

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # Input OTP '123456' and click Verify OTP button.
        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('123456')
        

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # Click the 'Toggle chat' button at index 14 to open the AI symptom checker chat interface.
        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/button[2]').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # Input a typical symptom description 'I have a headache and fever' into the chat input field and send it.
        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/div[3]/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('I have a headache and fever')
        

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/div[3]/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # Input a follow-up symptom description or answer to test if conversational context is maintained, despite the demo response.
        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/div[3]/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('My headache is severe and lasts for hours')
        

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/div/div/div[3]/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # Assertion: Verify the AI provides relevant symptom analysis and follow-up questions.
        response_locator = frame.locator('xpath=html/body/div/div/div/div[2]/div[last()]')
        response_text = await response_locator.inner_text()
        assert 'headache' in response_text.lower() or 'fever' in response_text.lower(), 'AI response should mention headache or fever'
        assert 'follow-up' in response_text.lower() or '?' in response_text, 'AI response should include follow-up questions or prompts'
        
        # Assertion: Verify conversational context is maintained with appropriate responses.
        followup_response_locator = frame.locator('xpath=html/body/div/div/div/div[2]/div[last()]')
        followup_response_text = await followup_response_locator.inner_text()
        assert 'severe' in followup_response_text.lower() and 'hours' in followup_response_text.lower(), 'AI response should acknowledge severity and duration of headache'
        assert 'headache' in followup_response_text.lower(), 'AI response should maintain context about headache'
        await asyncio.sleep(5)
    
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()
            
asyncio.run(run_test())
    