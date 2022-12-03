from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from slack_sdk import WebClient

import os
from time import sleep
from pathlib import Path

# # Environment variables
from dotenv import dotenv_values
config = {
    **dotenv_values(".env"),
    **dotenv_values(".env.secret"),
    **os.environ,
}

USERNAME = config.get("USERNAME")
PASSWORD = config.get("PASSWORD")
SLACK_BOT_TOKEN = config.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL = config.get("SLACK_CHANNEL")

if not USERNAME or not PASSWORD:
    print("Exiting because a required env var is not set (USERNAME, PASSWORD).")
    print("Exiting.")
    exit()

# # File store
store = Path('files')
store_dir = store.absolute()
print(f"{store_dir = }")

# # Setup browser
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('window-size=1920x1080')
prefs = {'download.default_directory': str(store_dir)}
options.add_experimental_option('prefs', prefs)

browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 10)

# # Crawl
# ## Login page
browser.get("https://transfer.dp-ds.de/ThinClient/WTM/public/index.html#/login")

elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input#inputUsername')))
elem.send_keys(USERNAME)

elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input#password')))
elem.send_keys(PASSWORD)

elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#signIn')))
elem.click()

# ## Main page
wait.until(EC.url_matches('https://transfer.dp-ds.de/ThinClient/WTM/public/index.html#/main'))

# expand directories
elem_expansion = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.fa-chevron-right')))
for elem in reversed(elem_expansion):
    elem.click()

# if we don't sleep, the last directory expanded is not yet loaded before the next code runs
sleep(1)

# find/download files
filenames_new = []
elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.file-ico + div.file-name')))
print(f'{len(elems)} files found on website')
for elem in elems:
    filename = elem.text
    if store_dir.joinpath(filename).exists():
        print(f'OLD file {filename!r} found')
    else:
        print(f'NEW file {filename!r} found')
        elem.click()
        filenames_new.append(filename)

if len(filenames_new) > 0:
    print("Sleeping 5s waiting for downloads to finish")
    sleep(5)
    print(f"These are the new files: {filenames_new}")
else:
    print("No new files.")
    print("Exiting.")
    exit()

browser.close()

# # Send files to Slack
if not SLACK_BOT_TOKEN or not SLACK_CHANNEL:
    print("Not sending Slack message because a required env var is not set (SLACK_BOT_TOKEN, SLACK_CHANNEL).")
    print("Exiting.")
    exit()

client = WebClient(SLACK_BOT_TOKEN)
client.auth_test()

for filename in filenames_new:
    path = store.joinpath(filename)
    upload_text_file = client.files_upload_v2(
        channels=SLACK_CHANNEL,
        title=path.name,
        file=str(path),
        initial_comment="MOOOOOIN",
    )

print("Done.")
