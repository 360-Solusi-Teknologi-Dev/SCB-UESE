from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_workflow(driver, workflow, context, presets, team, screen, tab):
    results = {}

    for step in workflow:
        action = step.get("action")
        field = step.get("field")  # e.g., "name" or "account_number"

        # Lookup the selector from presets for this field
        try:
            selector = presets[team][screen][tab][field]["selector"]
        except KeyError:
            raise Exception(f"Selector not found for {team}/{screen}/{tab}/{field}")
        
        if action == "switch_to_frame":
            iframe = driver.find_element(By.CSS_SELECTOR, selector)
            driver.switch_to.frame(iframe)

        if action == "click":
            driver.find_element(By.CSS_SELECTOR, selector).click()

        elif action == "input":
            value = context.get(step.get("value_from"), "")
            el = driver.find_element(By.CSS_SELECTOR, selector)
            el.clear()
            el.send_keys(str(value))  # make sure value is string

        elif action == "wait_for":
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )

        elif action == "extract":
            text = driver.find_element(By.CSS_SELECTOR, selector).text
            print(f"DEBUG: Extracted text for {field}: {text}")
            results[step.get("as")] = text

        # Add other action handlers as needed

    return results
