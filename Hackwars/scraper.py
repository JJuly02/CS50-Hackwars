import requests
from bs4 import BeautifulSoup

def scrape(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Custom logic to find potential usernames/passwords goes here
        # For example, finding all instances of a particular class
        names = soup.find_all(class_='potential-username')
        names_list = [name.text for name in names]

        return names_list
    except requests.RequestException as e:
        return f"An error occurred: {e}"
