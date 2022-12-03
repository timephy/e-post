from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from slack_sdk import WebClient

from time import sleep
import os
from pathlib import Path

# during dev load from file, after dev credentials will be env vars
from dotenv import load_dotenv
load_dotenv()

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")

if USERNAME is None or PASSWORD is None or SLACK_BOT_TOKEN is None:
    print("Exiting because a required env var is not set.")
    exit()


# # File store
store = Path('files')
store_dir = store.absolute()
print(f"{store_dir = }")

# # Setup browser
options = webdriver.ChromeOptions()
# options.add_argument("download.default_directory=/Users/timguggenmos/code/e-post/files")
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

print("Sleeping 5s waiting for downloads to finish")
sleep(5)

print(f"These are the new files: {filenames_new}")
browser.close()

# # Send files to Slack
client = WebClient(SLACK_BOT_TOKEN)
client.auth_test()

for filename in filenames_new:
    path = store.joinpath(filename)
    upload_text_file = client.files_upload(
        channels=SLACK_CHANNEL,
        title=f"File: {path}",
        file=str(path),
        initial_comment="Here is the file:",
    )

print("Done.")
