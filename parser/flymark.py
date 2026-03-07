import pandas as pd
import json
from bs4 import BeautifulSoup
from io import StringIO
import re, datetime

def get_competition_data_from_protocol(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        
    comp_name_tag = soup.find('a', class_='competition-link')
    comp_name = comp_name_tag.text.strip() if comp_name_tag else "Unknown"
    comp_link = comp_name_tag.get('href') if comp_name_tag else ""
    
    date_match = re.search(r'\d{4}', comp_name)
    if date_match:
        year = int(date_match.group(0))
        # Defaulting to Jan 1st since exact month/day aren't in the HTML
        comp_date = datetime.date(year, 1, 1)
    else:
        comp_date = None
    
    metadata = {}
    
    if comp_link:
        metadata['competition_url'] = f"https://flymark.dance{comp_link}"
        comp_id_match = re.search(r'/(\d+)$', comp_link)
        if comp_id_match:
            metadata['competition_id'] = int(comp_id_match.group(1))
            
    category_tag = soup.find('h2', class_='category-title')
    if category_tag:
        metadata['category'] = category_tag.text.strip()
        
    back_btn = soup.find('a', class_='back-btn')
    if back_btn and back_btn.get('href'):
        stream_link = back_btn.get('href')
        metadata['stream_url'] = f"https://flymark.dance{stream_link}"
        section_match = re.search(r'sectionId=(\d+)', stream_link)
        if section_match:
            metadata['section_id'] = int(section_match.group(1))

    stats_div = soup.find('div', class_='stats-summary')
    if stats_div:
        for span in stats_div.find_all('span'):
            text = span.text.strip()
            if ':' in text:
                key, val = text.split(':', 1)
                metadata[key.strip().lower()] = int(val.strip())

    return {
        'competition_name': comp_name,
        'date': comp_date,
        'metadata': metadata
    }

def get_adjudicators(f):
    """
    Retrieve the judges' information from the given html
    """
    data = []

    with open(f, 'r', encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')

        # The card is an anchor tag <a> containing the ID
        cards = soup.select(".judge-card") 

        for card in cards:
            letter_el = card.select_one(".judge-letter")
            name_el = card.select_one(".judge-name")
            city_el = card.select_one(".judge-city")
            
            # metadata
            href = card.get('href', '')
            judge_id = href.split('/')[-1] if href else ""

            data.append({
                "letter": letter_el.text.strip().replace('.', '') if letter_el else "",
                "name": " ".join(name_el.text.split()) if name_el else "Unknown",
                "city": city_el.text.strip() if city_el else "",
                "id": judge_id
            })

    return data


def get_competitors(f):
    """
    Retrieve the competitors' information from the given html
    """
    data = []

    with open(f, 'r', encoding='utf-8') as fp:
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
            
            # Extract links to determine if Solo or Couple and get IDs
            dancer_links = cells[2].select("a.dancer-link")
            dancers = []
            for link in dancer_links:
                dancers.append({
                    "name": " ".join(link.text.split()),
                    "id": link.get('href', '').split('/')[-1]
                })
            if not len(dancers):
                dancers = [{
                    "name": f"Dancer #{number}",
                    "id": None
                }]

            # Determine type
            participation_type = "couple" if len(dancers) == 2 else "solo"

            # metadata
            club_cell = cells[4]
            club_link = club_cell.select_one("a.club-link")
            club_data = {
                "name": " ".join(club_cell.text.split()),
                "id": ""
            }
            if club_link:
                club_data["name"] = " ".join(club_link.text.split())
                club_data["id"] = club_link.get('href', '').split('/')[-1]

            # trainers
            trainer_cell = cells[5]
            trainer_links = trainer_cell.select("a.trainer-link")
            trainers = []
            for link in trainer_links:
                trainers.append({
                    "name": " ".join(link.text.split()),
                    "id": link.get('href', '').split('/')[-1]
                })

            # Construct entry
            entry = {
                "number": number,
                "place": place,
                "type": participation_type,
                "city": " ".join(city.split()),
                
                # Detailed Dancer Info
                "dancers": dancers,
                
                # Club Info
                "club_name": club_data["name"],
                "club_id": club_data["id"],
                
                # Trainer Info
                "trainers": trainers
            }

            data.append(entry)

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
            dance_name_el = section.select_one(".dance-title")
            if not dance_name_el:
                continue
                
            dance_name = dance_name_el.text.strip()
            dance = dance_name[0] 
            
            table_el = section.select_one(".round-table")
            if not table_el:
                continue

            table_html = str(table_el)
            df = pd.read_html(StringIO(table_html))[0]
            df.rename(columns={"№": "number", "Place": "place"}, inplace=True)

            df["number"] = df["number"].astype(str)
            df.set_index("number", inplace=True)
            data[dance] = df
            
    if as_json:
        return json.dumps({
            dance: df.to_json(orient='split') 
            for dance, df in data.items()
        })
    return data