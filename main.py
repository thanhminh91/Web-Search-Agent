from playwright.sync_api import sync_playwright
from time import sleep
from getpass import getuser
from os import getcwd

cwd=getcwd()

with sync_playwright() as playwright:
    browser=playwright.chromium.launch_persistent_context(user_data_dir='',channel='msedge',headless=False,slow_mo=200,permissions=['geolocation'],
    args=['--disable-blink-features=AutomationControlled'])
    page=browser.new_page()
    page.goto('https://google.com')
    page.get_by_role('combobox').fill('Kochi')
    locater=page.get_by_role('listbox').get_by_role('option')
    print(locater.count())
    sleep(5)