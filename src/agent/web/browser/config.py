from dataclasses import dataclass
from typing import List, Literal
from getpass import getuser
from pathlib import Path
import os

@dataclass
class BrowserConfig:
    headless:bool=False
    wss_url:str=None
    browser_instance_dir:str=None
    downloads_dir:str=None
    browser:Literal['chrome','firefox','edge']='edge'
    user_data_dir:str=None
    timeout:int=60*1000
    slow_mo:int=300

SECURITY_ARGS = [
	'--disable-web-security',
	'--disable-site-isolation-trials',
	'--disable-features=IsolateOrigins,site-per-process',
]

BROWSER_ARGS=[
    '--no-sandbox',
	'--disable-blink-features=IdleDetection',
	'--disable-blink-features=AutomationControlled',
	'--disable-infobars',
	'--disable-background-timer-throttling',
	'--disable-popup-blocking',
	'--disable-backgrounding-occluded-windows',
	'--disable-renderer-backgrounding',
	'--disable-window-activation',
	'--disable-focus-on-load',
	'--no-first-run',
	'--no-default-browser-check',
	'--no-startup-window',
	'--window-position=0,0',
    '--remote-debugging-port=9222'
]

IGNORE_DEFAULT_ARGS=['--enable-automation']