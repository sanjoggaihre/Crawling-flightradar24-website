from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

url = 'https://www.flightradar24.com/data/airports'
driver = webdriver.Chrome()
driver.get(url)


def crawler():
   
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    f = requests.get(url, headers = headers)
    soup = BeautifulSoup(f.text, 'html.parser')
    formatted_res = soup.prettify()

    pattern = r'^(https://www.flightradar24.com/data)'
    all_urls = []
    for link in soup.find_all('a'):
        all_urls.append(link.get("href"))
    crawling_urls = [string_ for string_ in all_urls if re.search(pattern, str(string_))]


    ###Extracting all the navbar urls related to www.flightradar24.com/data/airport 
    navbar = soup.find_all(id = "data-section-nav")
    pattern = r'href=\S*'
    matched_words = re.findall(pattern, str(navbar))
    navbar_urls = [matched_word.replace('/data', ('https://www.flightradar24.com/data')).replace('href=' , '').strip('"') for matched_word in matched_words]

    return[navbar_urls, crawling_urls]
 

def find_country_and_airport():
    data_ = driver.find_element(By.TAG_NAME, "tbody")
    data_ = data_.text.replace(' ', '')
    data_list = data_.split('\n')

    # print(data_list)
    # print(len(data_list))

    for i in data_list:
        if len(i) <=1:
            data_list.remove(i)
        
    # print(data_list)
    # print(len(data_list))

    country_list = []
    no_of_airports = []
    for i in range(0,len(data_list)):
        if i%2 == 0:
            country_list.append(data_list[i])
        else:
            target_string = data_list[i]
            no_of_airports.append(int(re.sub(r"[A-Za-z]",'',target_string)))
    country_airports = {}

    country_airports['country_name'] = country_list
    country_airports['no_of_airports'] = (no_of_airports)

    df = pd.DataFrame(country_airports)
    df.to_csv('country.csv', index=False)

def extract_aircraft_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    f = requests.get(url, headers = headers)
    soup = BeautifulSoup(f.text, 'html.parser')
    aircraft_code = []
    no_of_flights = []
    aircraft_family = []
    for row in soup.find_all(class_ = "border-top"):
        aircraft_code.append(row.find("a").get_text())
        no_of_flights.append(row.find("span").get_text())
    for row in soup.find_all(class_ = "aircraft-family"):
        aircraft_family.append(row.get_text())    
    try:
        aircraft = {
            '   Aircraft_family' : aircraft_family,
            '   Aircraft_family_code': aircraft_code,
            '   No_of_aircrafts': no_of_flights
        }
        df = pd.DataFrame(aircraft)
        df.to_csv("aircraft.csv", index= False)
    except exception as e:
        print(e)

def main():
    navurl, urls_present_in_page = crawler()
    print("crawling_urls: ",urls_present_in_page)
    print("Navbar_urls: ",navurl)
    find_country_and_airport()
    extract_aircraft_info(navurl[3])

if __name__ == "__main__":
    main()