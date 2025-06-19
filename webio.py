from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip

def load_speakers_text(driver,url:str)->str:
    '''Function opens a tab with speakers and returns CSV text.
    Inputs:
    driver: Selenium driver object
    URL: url of the tournament
    Output: copy-paste text of CSV'''
    driver.get(f'{url}/tab/speaker/')
    time.sleep(10)
    csvbutton = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvbutton.click()
    return pyperclip.paste()

def load_teams_ranks_text(driver,url:str,round:str)->str:
    '''Opens a tab with team ranking for a given round and returns CSV text.
    Inputs:
    driver: Selenium driver object
    URL: url of the tournament
    round: number of the round whose data function is getting
    Output: copy-paste text of CSV'''
    driver.get(f'{url}/results/round/{round}/?view=team')
    time.sleep(5)
    driver.get(f'{url}/results/round/{round}/?view=team')
    time.sleep(5)
    csvbutton = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvbutton.click()
    return pyperclip.paste()

def load_teams_debates_text(driver,url:str,round:str)->str:
    '''Opens a tab with teams who debated together in a given round and returns a CSV text.
    Inputs:
    driver: Selenium driver object
    URL: url of the tournament
    round: number of the round whose data function is getting
    Output: copy-paste text of CSV'''
    driver.get(f'{url}/results/round/{round}/?view=debate')
    time.sleep(5)
    vidi_dugme = driver.find_element("xpath",'/html/body/div[1]/div[2]/div/div/div/a[2]')
    vidi_dugme.click()
    time.sleep(5)
    driver.get(f'{url}/results/round/{round}/?view=debate')
    time.sleep(5)
    csvbutton = driver.find_element("xpath", "/html/body/div[1]/div[4]/div/div/div/div[1]/div/div[2]/button")
    csvbutton.click()
    return pyperclip.paste()

def export_file(file_name:str, content:str):
    '''Funkcija za izvoz podataka u csv fajl.'''
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(content)

def download_whole_tournament(url:str,br_rundi:int=5):
    '''Skida podatke sa celog turnira u formati koji Tabbycat daje kada se klikne na CSV dugme.
    Prikupljene podatke zapisuje u CSV fajlove.'''
    driver = webdriver.Chrome()
    teams_ranks = []
    teams_debates = []
    if url.endswith('/'):
        url = url[:-1] # So the program works whether the URL ends with slash or not

    speakers = load_speakers_text(driver,url)
    for i in range(1, br_rundi+1):
        teams_ranks = load_teams_ranks_text(driver,url,str(i))
        teams_debates = load_teams_debates_text(driver,url,str(i))  # Učitajte debate za prvu rundu, možete promeniti round po potrebi
        export_file(f'tournament_files/teams_ranks_round_{i}.csv', teams_ranks)
        export_file(f'tournament_files/teams_debates_round_{i}.csv', teams_debates)
    export_file('tournament_files/speakers.csv', speakers)
    

    driver.quit()