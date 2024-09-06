#Libraries
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import sqlite3


#Variables
link = "https://web.archive.org/web/20230908091635 /https://en.wikipedia.org/wiki/List_of_largest_banks"
database_name = "Banks.db"
table_name = "Largest_Banks"
log_file = "code_log.txt"
output_csv_file = "Largest_banks_data.csv"
exchange_rate_data = pd.read_csv('exchange_rate.csv')#Data has the rates of currency
pd.set_option('display.max_columns',None)

#Log function
def log_progress(message):
    time_format = '%Y-%m-%d %H:%M:%S'
    now = datetime.now()
    timestamps = now.strftime(time_format)
    with open(log_file , 'a') as file:
        file.write(timestamps+'  '+message+'\n')

#Extract function
def extract(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    dictionary = {
        'Rank': [],
        'Bank_Name': [],
        'MC_USD_Billion': []
    }
    table = soup.find('tbody')
    for index, row in enumerate(table.find_all('tr')):

        if row and index != 0:
            cols = row.find_all('td')
            dictionary['Rank'].append(cols[0].contents[0].replace('\n', ''))
            dictionary['Bank_Name'].append(cols[1].find_all('a')[1].contents[0].replace('\n', ''))
            dictionary['MC_USD_Billion'].append(cols[2].contents[0].replace('\n', ''))

    data = pd.DataFrame(dictionary , columns = list(dictionary.keys()))
    return data


def transform(data , exchange_rate):
    data['MC_USD_Billion'] = data['MC_USD_Billion'].astype(float)
    data['MC_EUR_Billion'] = np.round(data['MC_USD_Billion'] * exchange_rate['Rate'].loc[exchange_rate['Currency'] == 'EUR'].values[0] , 2)
    data['MC_GBP_Billion'] = np.round(data['MC_USD_Billion'] * exchange_rate['Rate'].loc[exchange_rate['Currency'] == 'GBP'].values[0] , 2)
    data['MC_INR_Billion'] = np.round(data['MC_USD_Billion'] * exchange_rate['Rate'].loc[exchange_rate['Currency'] == 'INR'].values[0],2)
    data.set_index('Rank', inplace=True)

    return data

def load_to_csv(data , file_name):
    data.to_csv(file_name)

def load_to_db(data , db_name , t_name ):
    conn = sqlite3.connect(db_name)
    data.to_sql(t_name, conn, if_exists='replace', index=False)

def run_query(query , connection):
    df = pd.read_sql(query, connection)
    print(df)



log_progress("ETL Process is started")
log_progress("Extracting process is started")
extracted_data = extract(link)
log_progress("Extracting process is ended")

log_progress("Transformation process is started")
transformed_data = transform(extracted_data, exchange_rate_data)
log_progress("Transformation process is ended")


log_progress('Loading to csv process is started')
load_to_csv(transformed_data , output_csv_file)
log_progress('Loading to csv process is ended')

log_progress('Loading to database process is started')
load_to_db(transformed_data , database_name , table_name)
log_progress('Loading to database process is ended')


