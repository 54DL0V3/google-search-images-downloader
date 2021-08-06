from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

IMAGE_PER_PERSON = 200

urllib3.disable_warnings(InsecureRequestWarning)

with open("vn_famous_persons.json", "r", encoding="UTF-8") as f:
    vn_famous_persons = json.load(f)
maxcount = 1000

# chromedriver = 'D:\Downloads\chromedriver_win32\chromedriver.exe'
firefoxdriver = 'geckodriver-v0.29.1-linux64/geckodriver'


def login_facebook(browser, username, password):
    browser.get("https://www.facebook.com/")
    username_ele = browser.find_element_by_css_selector('#email')
    username_ele.send_keys(username)
    password_ele = browser.find_element_by_css_selector('#pass')
    password_ele.send_keys(password)
    btn_elements = browser.find_elements(By.TAG_NAME, value='button')
    for btn_element in btn_elements:
        if btn_element.get_attribute("name") == "login":
            btn_element.click()
            break


def download_from_facebook(search_urls, storage_path="storage", username=None, password=None):
    # options = webdriver.ChromeOptions()
    options = webdriver.FirefoxOptions()
    options.add_argument('--no-sandbox')
    # options.add_argument('--headless')

    try:
        # browser = webdriver.Chrome(chromedriver, options=options)
        browser = webdriver.Firefox(executable_path=firefoxdriver, options=options)
    except Exception as e:
        print(f'No found chromedriver in this environment.')
        print(f'Install on your machine. exception: {e}')
        sys.exit()

    login_facebook(browser, username, password)

    # for key in vn_famous_persons.keys():
    #     print(">>> {} <<<".format(key))

    count = 0

    for search_url in search_urls:
        print(">>> Searching url = {}".format(search_url))
        url_split = search_url.split("/")
        if len(url_split) > 2:
            dirs = os.path.join(storage_path, url_split[2])
            if len(url_split) > 4:
                if search_url.split("/")[3] != "groups":
                    dirs = os.path.join(dirs, url_split[3])
                else:
                    dirs = os.path.join(dirs, url_split[4])
            elif len(url_split) > 3:
                dirs = os.path.join(dirs, url_split[3])
        else:
            dirs = os.path.join(storage_path, urls)

        if not os.path.exists(dirs):
            os.makedirs(dirs)

        browser.set_window_size(1280, 1024)
        try:
            browser.get(search_url)
        except Exception as e:
            print(e)
            print("ERROR while searching url: {}".format(search_url))
        time.sleep(1)

        print(f'Getting you a lot of images. This may take a few moments...')

        element = browser.find_element(By.TAG_NAME, value='body')

        # Scroll down
        # for i in range(30):
        for i in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)

        try:
            browser.find_element_by_id('smb').click()
            for i in range(50):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)
        except Exception as e:
            print(e)
            for i in range(10):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)

        print(f'Reached end of page.')
        time.sleep(0.5)

        # Get a elements
        print("Finding image a class")
        a_elements = browser.find_elements(By.TAG_NAME, value="a")
        a_element_class_dict = dict()
        largest_class_member = None
        n_member = 0
        for a_element in a_elements:
            a_element_class = a_element.get_attribute('class')
            if a_element_class not in a_element_class_dict:
                a_element_class_dict[a_element_class] = 1
            else:
                a_element_class_dict[a_element_class] = a_element_class_dict[a_element_class] + 1

            if largest_class_member is None or a_element_class_dict[a_element_class] > n_member:
                largest_class_member = a_element_class
                n_member = a_element_class_dict[a_element_class]

        print(f"Found class: {largest_class_member} - {n_member}")
        image_a_elements = []
        for a_element in a_elements:
            if a_element.get_attribute('class') == largest_class_member:
                image_a_elements.append(a_element)
        print(len(image_a_elements))

        # Get image a elements
        print("Getting images urls")
        urls = []
        for image_a_element in image_a_elements:
            counter = 0
            click_success = False
            while counter < 5 and click_success is False:
                try:
                    # click on image
                    image_a_element.click()
                    click_success = True

                except Exception as e:
                    print(e)
                    counter += 1
                    print(f"Click failed - Retry {counter}")
                    time.sleep(0.2)
                    continue

                if click_success:
                    # get pop-up image link
                    image_elements = browser.find_elements(By.TAG_NAME, value='img')
                    for image_element in image_elements:
                        if image_element.get_attribute("data-visualcompletion") == "media-vc-image":
                            src = image_element.get_attribute("src")
                            if src is not None:
                                urls.append(src)
                    browser.back()
                    time.sleep(0.1)

        print(f"Found: {len(urls)} images")


        # # Get image elements
        # img_elements = browser.find_elements(By.TAG_NAME, value='img')
        # print(f"Found: {len(img_elements)} image elements")
        # urls = []
        # for img_element in img_elements:
        #     src = img_element.get_attribute("src")
        #     if src is not None:
        #         urls.append(src)


        total = len(urls)
        if urls:
            for url in urls:
                # url = url.split("imgurl=")[1]
                # url = url.split("&imgrefurl=")[0]
                url = url.replace("%3A", ":")
                url = url.replace("%2F", "/")
                # url = url.split("%")[0]
                count += 1
                file_name = url.split("?")[0].split("/")[-1]
                print("Downloading iamges: {}/{} - Filename: {}".format(count, total, file_name), end="\r")

                try:
                    res = requests.get(url, verify=False, stream=True)
                    rawdata = res.raw.read()
                    with open(os.path.join(dirs, 'img_' + str(count) + "_" + file_name), 'wb') as f:
                        f.write(rawdata)
                except Exception as e:
                    print('Failed to write rawdata.')
                    print(e)
            print("\n Done \n")

    browser.close()
    return count


# Main block
def main():
    # parse args
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--email",
                        type=str,
                        help="Facebook account email")
    parser.add_argument("--password",
                        type=str,
                        help="Facebook account password")
    parser.add_argument("--urls",
                        type=str,
                        help="Path to file .json")

    args = parser.parse_args()

    with open(args.urls, "r", encoding="UTF-8") as f:
        list_urls = json.load(f)["facebook"]
    t0 = time.time()
    count = download_from_facebook(search_urls=list_urls, username=args.email, password=args.password)
    t1 = time.time()

    total_time = t1 - t0
    print(f'\n')
    print(f'Download completed. [Successful count = {count}].')
    print(f'Total time is {str(total_time)} seconds.')


if __name__ == '__main__':
    main()
