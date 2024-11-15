import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime
import logging

class Flightera:
    def __init__(self):
        self._name = "Flightera"
        
    def get_flight(self, flight_code : str):
        try:
            url = f'https://www.flightera.net/en/flight/{flight_code}'
            headersList = {
             "Accept": "*/*",
             "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
            }
            
            payload = ""
            response = requests.request("GET", url, data=payload,  headers=headersList)
            soup = BeautifulSoup(response.content, "html.parser")
            element_title = soup.find(class_="text-xl")
            data = {
                "LINK":url,
                "DATE": None,
                "STATUS": None,
                "CODE": flight_code,
                "COMPANY": None,
                "COMPANY_CODE": None,
                "FROM": None,
                "TO": None
            }
            pattern = r"(.*) (.*)\s\s(\(.*\))"
            # Find all matches in the text
            matches = re.findall(pattern, element_title.get_text(strip=True))
            
            # Flatten the list of tuples into a single list (if needed)
            result = [group for match in matches for group in match]

            data['COMPANY'] =  result[0]
            data['COMPANY_CODE'] = result[1]
            day = soup.find('dd')
            data['DATE'] = day.get_text(strip=True)
            status = soup.find(attrs={"id":"liveStatusInd"})
            data['STATUS'] = status.get_text(strip=True)
            
            return data
        except Exception as ex:
            logging.error(ex)
            raise Exception("Dont exist fly")
        

    def get_history_last_flys(self, flight_code : str):
        try:
            url = f'https://www.flightera.net/en/flight/{flight_code}'
            headersList = {
             "Accept": "*/*",
             "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
            }
            
            payload = ""
            
            response = requests.request("GET", url, data=payload,  headers=headersList)
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find('table')
            data = {
                "LINK":[],
                "DATE": [],
                "STATUS": [],
                "FLIGHT NUMBER": [],
                "DESTINATION": [],
                "FROM": [],
                "FROM_DATE":[],
                "FROM_MESSAGE":[],
                "FROM_UTC":[],
                "TO": [],
                "TO_DATE":[],
                "TO_MESSAGE":[],
                "TO_UTC":[],
                "DEPARTED": [],
                "DEPARTED_MESSAGE":[],
                "ARRIVED": [],
                "ARRIVED_MESSAGE":[]
            }
            is_first_cell = True
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if is_first_cell:
                    is_first_cell = False
                    continue
                if len(cells) == 7:  # Adjust number if columns vary
                    cell_zero = [i.strip() for i in cells[0].get_text().split('\n') if len(i.strip()) > 2]
                    link = cells[0].find_all(href=True)[0]
                    data['LINK'].append('https://www.flightera.net' + link['href'])
                    data["DATE"].append(cell_zero[0])
                    data["STATUS"].append(cell_zero[1])
                    cell_one = [i.strip() for i in cells[1].get_text().split('\n') if len(i.strip()) > 2]
                    data["FLIGHT NUMBER"].append(cell_one[0])
                    data["DESTINATION"].append(cell_one[1])
                    cell_two = [i.strip() for i in cells[2].get_text().split('\n') if len(i.strip()) > 2]
                    if len(cell_two) == 5:
                        data["FROM"].append(cell_two[2])
                        data["FROM_DATE"].append(cell_two[-2])
                        data["FROM_MESSAGE"].append(cell_two[1])
                        data["FROM_UTC"].append(cell_two[-1])
                    else:
                        data["FROM"].append(cell_two[1])
                        data["FROM_DATE"].append(cell_two[-2])
                        data["FROM_MESSAGE"].append(None)
                        data["FROM_UTC"].append(cell_two[-1])
                    cell_three = [i.strip() for i in cells[3].get_text().split('\n') if len(i.strip()) > 2]
                    if len(cell_three) == 5:
                        data["TO"].append(cell_three[2])
                        data["TO_DATE"].append(cell_three[-2])
                        data["TO_MESSAGE"].append(cell_three[1])
                        data["TO_UTC"].append(cell_three[-1])
                    else:
                        data["TO"].append(cell_three[1])
                        data["TO_DATE"].append(cell_three[-2])
                        data["TO_MESSAGE"].append(None)
                        data["TO_UTC"].append(cell_three[-1])

                    cell_four = [i.strip() for i in cells[4].get_text().split('\n') if len(i.strip()) > 2]
                    if len(cell_four) == 2:
                        data["DEPARTED"].append(cell_four[0])
                        data["DEPARTED_MESSAGE"].append(cell_four[1])
                    else:
                        data["DEPARTED"].append(None)
                        data["DEPARTED_MESSAGE"].append(None)
                    cell_five = [i.strip() for i in cells[5].get_text().split('\n') if len(i.strip()) > 2]
                    if len(cell_five) == 2:
                        data["ARRIVED"].append(cell_five[0])
                        data["ARRIVED_MESSAGE"].append(cell_five[1])
                    else:
                         data["ARRIVED"].append(None)
                         data["ARRIVED_MESSAGE"].append(None)
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            return df
        except Exception as ex:
            logging.error(ex)
            raise Exception("Dont exist fly")

    def get_history_by_date(self,flight_code : str, month : int, year: int):
        data_fly = self.get_flight(flight_code)
        month = datetime.date(2023, month, 1).strftime("%b")
        company = "+".join(data_fly['COMPANY'])
        url = f'https://www.flightera.net/en/flight/{company}/{flight_code}/{month}-{year}#flight_list'
        try:
            headersList = {"Accept": "*/*", "User-Agent": "Thunder Client (https://www.thunderclient.com)" }
            
            payload = ""
            
            response = requests.request("GET", url, data=payload,  headers=headersList)
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find('table')
            data = {
                    "LINK":[],
                    "DATE": [],
                    "STATUS": [],
                    "FROM": [],
                    "FROM_DATE":[],
                    "FROM_UTC":[],
                    "TO": [],
                    "TO_DATE":[],
                    "TO_UTC":[],
                    "DEPARTED_DATE":[],
                    "DEPARTED_MESSAGE":[],
                    "ARRIVED_DATE":[],
                    "ARRIVED_MESSAGE":[]
            }
            is_first_cell = True
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if is_first_cell:
                        is_first_cell = False
                        continue
                if len(cells) > 5:
                   
                    cell_zero = [i.strip() for i in cells[0].get_text().split('\n') if len(i.strip()) > 2]
                    link = cells[0].find_all(href=True)[0]
                    
                    data['LINK'].append('https://www.flightera.net' + link['href'])
                    data["DATE"].append(cell_zero[0])
                    data["STATUS"].append(cell_zero[1])
                    cell_one = [i.strip() for i in cells[1].get_text().split('\n') if len(i.strip()) > 2]
                  
                    data["FROM"].append(cell_one[-3])
                    data["FROM_DATE"].append(cell_one[-2])
                    data["FROM_UTC"].append(cell_one[-1])
                  
                    cell_two = [i.strip() for i in cells[2].get_text().split('\n') if len(i.strip()) > 2]
                  
                    data["TO"].append(cell_two[-3])
                    data["TO_DATE"].append(cell_two[-2])
                    data["TO_UTC"].append(cell_two[-1])
                    
            
                    cell_three = [i.strip() for i in cells[3].get_text().split('\n') if len(i.strip()) > 2]
          
               
                    if len(cell_three) == 3:
                        data["DEPARTED_DATE"].append(cell_three[-2])
                        data["DEPARTED_MESSAGE"].append(cell_three[-1])
                    else:
                        data["DEPARTED_DATE"].append(None)
                        data["DEPARTED_MESSAGE"].append(None)
                    
                    cell_four = [i.strip() for i in cells[4].get_text().split('\n') if len(i.strip()) > 2]
                    if len(cell_four) == 3:
                        data["ARRIVED_DATE"].append(cell_four[-2])
                        data["ARRIVED_MESSAGE"].append(cell_four[-1])
                    else:
                        data["ARRIVED_DATE"].append(None)
                        data["ARRIVED_MESSAGE"].append(None)
                    
         
            response = pd.DataFrame(data)
            response['YEAR'] = year
            return response.to_dict(orient="records")
        except Exception as ex:
            logging.error(ex)
            raise Exception("Dont exist")