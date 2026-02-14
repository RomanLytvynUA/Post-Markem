import pandas as pd
import json
from bs4 import BeautifulSoup
from io import StringIO


def get_adjudicators(f):
    """
    Retrieve the judges' information from the given html
    """

    data = []

    with open(f) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

        cards = soup.select(".judge-card") 

        for card in cards:
            letter_el = card.select_one(".judge-letter")
            name_el = card.select_one(".judge-name")
            city_el = card.select_one(".judge-city")

            data.append({
                "letter": letter_el.text.strip().replace('.', '') if letter_el else "",
                "name": " ".join(name_el.text.split()) if name_el else "Unknown",
                "city": city_el.text.strip() if city_el else ""
            })

    return data


def get_competitors(f):
    """
    Retrieve the competitors' information from the given html
    """

    data = []

    with open(f) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        table = soup.select_one("table.couples-table")
        if not table:
            raise ValueError("Competitors table not found.")

        rows = table.select("tbody tr")

        for row in rows:
            cells = row.select("td")
            
            if len(cells) != 6: 
                raise ValueError("Unexpected format of table row.")

            number = cells[0].text.strip()
            place = cells[1].text.strip()
            city = cells[3].text.strip()
            club = cells[4].text.strip()
            coach = cells[5].text.strip()
            
            name = cells[2].text.strip()

            data.append({
                "number": number,
                "place": place,
                "name": " ".join(name.split()),
                "city": " ".join(city.split()),
                "club": " ".join(club.split()),
                "coach": " ".join(coach.split())
            })

    return data


def get_final_marks(f, as_json=False):
    """
    Retrieve the marks for each dance in the final and return them as pandas dataframe
    """

    data = {}
    
    with open(f, 'r', encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        
        sections = soup.select(".dance-section")
        
        for section in sections:
            dance_name = section.select_one(".dance-title").text.strip()
            dance = dance_name[0]
            
            table_html = str(section.select_one(".round-table"))
            df = pd.read_html(StringIO(table_html))[0]
            df.rename(columns={"№": "number", "Place": "place"}, inplace=True)

            df.set_index("number", inplace=True)
            data[dance] = df
            
    if as_json:
        return json.dumps({
            dance: df.to_json(orient='split') 
            for dance, df in data.items()
        })
    return data
