from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
from tabulate import tabulate
import os

datalist = []
x = 0 #counter

#launch url
for num in [1,2,3,4]:
  url="https://journals.aps.org/search/results?sort=oldest&clauses=%5B%7B%22field%22:%22author%22,%22value%22:%22Steven%20G.%20Louie%22,%22operator%22:%22AND%22%7D%5D&page=" + str(num) + "&per_page=100"
  # create a new Firefox session
  driver = webdriver.Firefox()
  driver.implicitly_wait(30)
  driver.get(url)
  soup_level1=BeautifulSoup(driver.page_source, 'lxml')
  close_icon = driver.find_element_by_xpath("/html/body/div[9]/div/span[2]/a") 
  close_icon.click()
  for link in soup_level1.find_all('a', href=re.compile("abstract")):
    if link.get('class')==['tiny', 'button', 'radius']:
      print(link)
      print(link.name)
      print(link.get('href'))
      string="//a[@href=\'" + link.get('href') + "\']"
      python_button = driver.find_element_by_xpath(string)
      python_button.click() #click link
      soup_level2=BeautifulSoup(driver.page_source, 'lxml')
      print(soup_level2.find('div', class_="content").contents[0].text)
      abstract=str(soup_level2.find('div', class_="content").contents[0].text)
      print(soup_level2.find('h3').text)
      title=str(soup_level2.find('h3').text)
      print(soup_level2.find('h5', class_="authors").text)
      authors=str(soup_level2.find('h5', class_="authors").text)
      print(soup_level2.find('h5', class_="pub-info").text)
      pubinfo=str(soup_level2.find('h5', class_="pub-info").text)
      print(soup_level2.find('span', class_="doi-field").text)
      doi=str(soup_level2.find('span', class_="doi-field").text)
      df = pd.DataFrame([(doi, authors, title, abstract, pubinfo)], columns=["doi","authors","title","abstract","pubinfo"])
      datalist.append(df)
      driver.execute_script("window.history.go(-1)")
      x += 1
      print(x)
      driver.quit()


#combine all pandas dataframes in the list into one big dataframe
result = pd.DataFrame(columns=["doi","authors","title","abstract","pubinfo"])
result = pd.concat([pd.DataFrame(datalist[i]) for i in range(len(datalist))],ignore_index=True)
print(result.head())

#convert the pandas dataframe to JSON
json_records = result.to_json(orient='records')

#pretty print to CLI with tabulate
#converts to an ascii table
print(tabulate(result,tablefmt='psql'))

path = os.getcwd()
