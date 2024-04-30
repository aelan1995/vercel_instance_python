import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_company(company_name):
    search_url = "https://bizfileonline.sos.ca.gov/search/business"

    # Configure Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    # Configure the WebDriver with headless mode
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(search_url)

    # Fill in the search form and submit
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/main/div/div[3]/div[1]/form/input")))
    search_box.send_keys(company_name)
    search_box.submit()

    # Wait for search results table to appear
    try:
        result_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/main/div[2]/table")))
    except:
        driver.quit()
        return {"has_results": False}

    # Scroll to bring the first result into view
    first_result_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/main/div[2]/table/tbody/tr[1]/td[1]/div")))
    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", first_result_element)

    # Click on the first element in the search results table using XPath
    first_result_xpath = "/html/body/div[2]/div/div[1]/div/main/div[2]/table/tbody/tr/td[1]/div"
    first_result = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, first_result_xpath)))
    
    # Click on the first result
    first_result.click()

    # Wait for the pop-up window to appear
    pop_up = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/main/div[3]/div/div[2]/div/div/table")))

    # Extract table content
    table_content = pop_up.get_attribute('outerHTML')

    # Extract title
    title_element = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div/main/div[3]/div/div[1]")
    title = title_element.text.strip()

    driver.quit()
    return title, table_content

if __name__ == "__main__":
    company_name = "{{1.company_name}}"
    title, table_content = search_company(company_name)
    if isinstance(table_content, str):
        # Parse HTML to JSON
        json_object = {}
        lines = table_content.split('<tr class="detail ">')
        for line in lines[1:]:
            label_start_index = line.find('<td class="label">') + len('<td class="label">')
            label_end_index = line.find('</td>', label_start_index)
            value_start_index = line.find('<td class="value">', label_end_index) + len('<td class="value">')
            value_end_index = line.find('</td>', value_start_index)
            label = line[label_start_index:label_end_index].strip().replace(' ', '_').lower()
            value = line[value_start_index:value_end_index].strip().replace('\n', ' ')
            json_object[label] = value
        
        # Include title in the JSON object
        json_object['title'] = title

        # Rearrange JSON object to have title first
        json_object = {"title": title, **json_object}

        # Store the JSON object in the `result` variable
        result = json.dumps(json_object)
        print(f"result = {result};")
    else:
        print("No results found.")