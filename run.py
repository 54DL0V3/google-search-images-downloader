from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sys

import json
import os
import argparse

import requests
import urllib
import urllib3
from urllib3.exceptions import InsecureRequestWarning

import datetime
import time

IMAGE_PER_PERSON = 50

urllib3.disable_warnings(InsecureRequestWarning)


with open("vn_famous_persons.json", "r", encoding="UTF-8") as f:
    vn_famous_persons = json.load(f)
maxcount = 1000

# chromedriver = 'D:\Downloads\chromedriver_win32\chromedriver.exe'
firefoxdriver = 'geckodriver-v0.29.1-linux64/geckodriver'



def download_google_staticimages():

    # options = webdriver.ChromeOptions()
    options = webdriver.FirefoxOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')

    try:
        # browser = webdriver.Chrome(chromedriver, options=options)
        browser = webdriver.Firefox(executable_path = firefoxdriver, options= options)
    except Exception as e:
        print(f'No found chromedriver in this environment.')
        print(f'Install on your machine. exception: {e}')
        sys.exit()

    # for key in vn_famous_persons.keys():
    #     print(">>> {} <<<".format(key))
    list_name = vn_famous_persons["actor"]
    n_name = len(list_name)
    for i in range(0, n_name):
        name = list_name[i]
        print(">>> {} <<<".format(name))
        dirs = os.path.join("storage", name)
        search_string = name.replace("_", "+")
        if "(" not in search_string:
            search_string = "diễn viên " + search_string
        searchurl = 'https://www.google.com/search?q=' + search_string + '&source=lnms&tbm=isch'
        
        print(">>> Searching url = {}".format(searchurl))
        if not os.path.exists(dirs):
            os.mkdir(dirs)
        elif len(os.listdir(dirs)) > (IMAGE_PER_PERSON*0.8):
            print("This person already exist!")
            continue
        
        browser.set_window_size(1280, 1024)
        try:
            browser.get(searchurl)
        except Exception as e:
            print("ERROR while searching url: {} - name: {}".format(searchurl, name))
            continue
        time.sleep(1)

        print(f'Getting you a lot of images. This may take a few moments...')

        element = browser.find_element(By.TAG_NAME,value= 'body')

        # Scroll down
        #for i in range(30):
        for i in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

        try:
            browser.find_element_by_id('smb').click()
            for i in range(50):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)
        except:
            for i in range(10):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)

        print(f'Reached end of page.')
        time.sleep(0.5)
        # print(f'Retry')
        # time.sleep(0.5)

        # Below is in japanese "show more result" sentences. Change this word to your lanaguage if you require.
        # browser.find_element_by_xpath('//input[@value="Hiển thị thêm kết quả"]').click()

        a_elements = browser.find_elements(By.TAG_NAME, value= 'a')
        print("Number of elements found: {}".format(len(a_elements)))

        image_class_name = ""
        for a_element in a_elements:
            
            jaction = a_element.get_attribute("jsaction")
            target = a_element.get_attribute("target")
            if jaction is not None and "click:" in jaction:
                image_class_name = a_element.get_attribute("class")
                print(image_class_name)
                break
        
        # Click image
        element_counter = 0
        for a_element in a_elements:
            if a_element.get_attribute("class") == image_class_name and element_counter < IMAGE_PER_PERSON:
                a_element.click()
                element_counter += 1
                time.sleep(0.3)

        # Reget element
        a_elements = browser.find_elements(By.TAG_NAME, value= 'a')
        urls = []
        for a_element in a_elements:
            if a_element.get_attribute("class") == image_class_name:
                href = a_element.get_attribute("href")
                if href is not None:
                    urls.append(href)
                else:
                    break

        count = 0
        total = len(urls)
        if urls:
            for url in urls:
                url = url.split("imgurl=")[1]
                url = url.split("&imgrefurl=")[0]
                url = url.replace("%3A",":")
                url = url.replace("%2F","/")
                url = url.split("%")[0]
                count += 1
                print("Downloading iamges: {}/{}".format(count, total),end="\r")

                try:
                    res = requests.get(url, verify=False, stream=True)
                    rawdata = res.raw.read()
                    subfix = "." + url.split(".")[-1]
                    with open(os.path.join(dirs, 'img_' + str(count) + subfix), 'wb') as f:
                        f.write(rawdata)
                except Exception as e:
                    print('Failed to write rawdata.')
                    print(e)
            print("\n Done \n")

    browser.close()
    return count

# Main block
def main():
    t0 = time.time()
    count = download_google_staticimages()
    t1 = time.time()

    total_time = t1 - t0
    print(f'\n')
    print(f'Download completed. [Successful count = {count}].')
    print(f'Total time is {str(total_time)} seconds.')

if __name__ == '__main__':
    main()