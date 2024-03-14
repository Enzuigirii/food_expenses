from __future__ import annotations

import pathlib

from envparse import Env
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def get_driver() -> webdriver:
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--allow-profiles-outside-user-dir')
    options.add_argument('--enable-profile-shortcut-manager')
    options.add_argument(f'user-data-dir={script_directory}/userdata')
    options.add_argument('--profile-directory=Profile 1')
    options.add_argument(f'--user-agent={user_agent}')
    serv = Service(executable_path='/home/alexandr/food_expenses/chromedriver')
    return webdriver.Chrome(service=serv, options=options)


script_directory = pathlib.Path().absolute()
save_path_temp_files: str = f'{script_directory}/tempdata'
temp_json_shipments : str = 'json_shipments'
sbermarket_url: str = 'https://sbermarket.ru/user/shipments'

env = Env()
env.read_envfile()

DB_HOST: str = env.str('DB_HOST')
DB_PORT: str = env.str('DB_PORT')
DB_NAME: str = env.str('DB_NAME')
DB_USER: str = env.str('DB_USER')
DB_PASS: str = env.str('DB_PASS')
DATABASE_URL: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
