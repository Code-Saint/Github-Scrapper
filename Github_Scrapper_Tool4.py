from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import traceback
import json

# Specify the path to chromedriver
cdp = "/home/ayush/Downloads/chromedriver-linux64/chromedriver"

# Create a Service object for chromedriver
service = Service(cdp)

# Initialize the WebDriver with the Service object
driver = webdriver.Chrome(service=service)

def going_for_raw(file_url):
    try:
        driver.get(file_url)
        # Locate the 'Raw' button using XPath and extract the URL
        raw_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[@data-testid='raw-button' and contains(@class, 'prc-Button-ButtonBase-c50BI')]")
            )
        )
        raw_url = raw_button.get_attribute("href")
        
        # Fetch the content using the requests module
        response = requests.get(raw_url)
        if response.status_code == 200:
            content = response.text
            
            # Check for the presence of "password" in the content
            if "password" in content:
                print(f"Password found in {raw_url}")
                print(f"Content snippet: {content[:100]}...")  # Displaying a snippet for context
        else:
            print(f"Failed to fetch raw file content. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error retrieving raw file URL: {e}")
        traceback.print_exc()

def link_loop(repo_page):
    try:
        driver.get(repo_page)
        # Locate all Python file links by updated selector
        file_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href$='.py']"))
        )
        for file_link in file_links:
            file_name = file_link.text
            if file_name.endswith(".py"):
                file_url = file_link.get_attribute("href")
                print(f"Processing Python file: {file_url}")
                going_for_raw(file_url)
    except Exception as e:
        print(f"Error processing files in {repo_page}: {e}")
        traceback.print_exc()

def process_user_repos(user_url):
    try:
        api_url = f"https://api.github.com/users/{user_url.split('/')[-1]}/repos"
        response = requests.get(api_url)
        if response.status_code == 200:
            repos = response.json()
            for repo in repos:
                repo_name = repo["name"]
                repo_url = repo["html_url"]
                print(f"Processing repository: {repo_name}")
                link_loop(repo_url)
        else:
            print(f"Failed to fetch repositories. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error processing user repositories: {e}")
        traceback.print_exc()

try:
    # Prompt the user to enter the GitHub user URL
    user_url = input("Enter the GitHub user URL: ").strip()
    if not user_url:
        raise ValueError("User URL cannot be empty.")

    # Process all repositories of the user
    print(f"Processing repositories for user: {user_url}")
    process_user_repos(user_url)
except Exception as e:
    print(f"Error processing user repositories: {e}")
    traceback.print_exc()
finally:
    # Quit the browser
    driver.quit()
