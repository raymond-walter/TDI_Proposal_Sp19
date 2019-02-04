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

# import language toolkit
import numpy as np
import nltk
from nltk.corpus import stopwords
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import PorterStemmer

# start cleaning 
result['abstract_cleaned']=result['abstract'].str.lower()
result['abstract_cleaned']=result['abstract_cleaned'].str.replace('[^\w\s]','')
result['abstract_cleaned'].head()

# examples of defective cases
result['abstract_cleaned'][6]
result['abstract_cleaned'][7]

# partial clean up on math notation 
# need more general solution 
pattern = re.compile('displayinline')
result['abstract_cleaned']=result['abstract_cleaned'].apply(lambda x: pattern.sub('', x))
result['abstract_cleaned']=result['abstract_cleaned'].str.replace('nshttpwwww3org1998mathmathml', '')
result['abstract_cleaned']=result['abstract_cleaned'].str.replace('xml', '')
result['abstract_cleaned'][7]
result['abstract_cleaned']=result['abstract_cleaned'].str.replace('ab initio', 'abinitio')


#Tokenize data
stopwords = nltk.corpus.stopwords.words('english')
stopwords.append('mrowmsubmrowmi')

result['abstract_cleaned'] = result.apply(lambda row: nltk.word_tokenize(row['abstract_cleaned']), axis=1)

result['abstract_cleaned'] = result['abstract_cleaned'].apply(lambda x: [item for item in x if item not in stopwords])
#---Put all words in array, plot it out
all_words = result['abstract_cleaned'].sum()
#---Get frequency and plot
freq = nltk.FreqDist(all_words)


#---Stemming
stemmer = PorterStemmer()
stemmed_words = []
for w in all_words:
    stemmed_words.append(stemmer.stem(w))


stopwords.extend(['calculations','calculated','results','properties','found','within','show','agreement'])
result['abstract_cleaned'] = result['abstract_cleaned'].apply(lambda x: [item for item in x if item not in stop])#---Put all words in array, plot it out
all_words = result['abstract_cleaned'].sum()
#---Get frequency and plot
freq = nltk.FreqDist(all_words)
# Print and plot most common words
freq.most_common(20)
freq.plot(20)

result["year"]=result["pubinfo"].str.split().str[-1]
result["year"]=result["year"].str.replace('[^\w\s]','')
result["year"]=pd.to_numeric(result["year"])
bins=pd.cut(result["year"], [1974,1980,1990,2000,2010,2019], include_lowest=True)
for n in range(5):
  freq = nltk.FreqDist(result.groupby(bins)['abstract_cleaned'].sum()[n])
  freq.plot(20)


