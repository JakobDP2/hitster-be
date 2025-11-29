import pandas as pd
import re

# --- INSTELLINGEN ---
input_bestand = 'Hitster_BE_208.xlsx'  # Zorg dat deze naam klopt!
output_bestand = 'songs.js'
# --------------------

def clean_spotify_id(link):
    """
    Haalt het ID uit verschillende soorten Spotify links:
    1. spotify:track:12345
    2. https://open.spotify.com/track/12345?si=...
    """
    link = str(link).strip()
    
    # Check of het veld leeg is
    if not link or link.lower() == 'nan':
        return ""
    
    # TYPE 1: De web link (https://open.spotify.com/track/ID...)
    if 'track/' in link:
        # Alles na 'track/' pakken
        na_track = link.split('track/')[1]
        # Alles voor het vraagteken pakken (om ?si=... weg te halen)
        clean_id = na_track.split('?')[0]
        return clean_id
        
    # TYPE 2: De URI (spotify:track:ID)
    elif 'spotify:track:' in link:
        # Het laatste stukje na de laatste dubbele punt
        return link.split(':')[-1]
    
    # Als het al gewoon een kaal ID is, sturen we het terug
    return link

print(f"Bezig met inlezen van '{input_bestand}'...")

try:
    df = pd.read_excel(input_bestand)
except Exception as e:
    print(f"FOUT: Kon bestand niet lezen. {e}")
    exit()

js_content = "const songs = [\n"

teller = 0
for index, row in df.iterrows():
    # Haal data op (past zich aan als kolommen net iets anders heten)
    artiest = row.get('Artiest') or row.get('Artist') or "Onbekend"
    titel = row.get('Titel') or row.get('Track Name') or row.get('Title') or "Onbekend"
    jaar = row.get('Jaartal') or row.get('Year') or row.get('Release Date') or "0000"
    link = row.get('Spotify Link') or row.get('Link') or row.get('Track URI') or ""
    
    # Hier gebeurt de magie
    clean_id = clean_spotify_id(link)
    
    # Alleen toevoegen als we een geldig ID hebben gevonden
    if clean_id and len(clean_id) > 5: 
        # repr() zorgt dat speciale tekens in titels geen errors geven
        js_line = f'  {{ id: {teller}, artist: {repr(str(artiest))}, title: {repr(str(titel))}, year: {jaar}, uri: "{clean_id}" }},'
        js_content += js_line + "\n"
        teller += 1

js_content += "];"

with open(output_bestand, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Klaar! {teller} liedjes verwerkt in '{output_bestand}'.")