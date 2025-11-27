import pandas as pd
import re

# --- INSTELLINGEN ---
input_bestand = 'Hitster_BE_208.xlsx'  # Zorg dat je bestand EXACT zo heet
output_bestand = 'songs.js'
# --------------------

def clean_spotify_id(link):
    """Haalt het ID uit een link of URI"""
    link = str(link).strip()
    # Als het leeg is of 'nan' (Not a Number)
    if link == '' or link.lower() == 'nan':
        return ""
    
    # Pakt het laatste stukje na de slash of dubbele punt
    # Werkt voor: https://open.spotify.com/track/12345
    # Werkt voor: spotify:track:12345
    if 'track' in link:
        parts = re.split(r'[:/]', link)
        return parts[-1].split('?')[0] # Weghalen van ?si=... troep
    return link

print(f"Bezig met inlezen van '{input_bestand}'...")

try:
    # We gebruiken read_excel ipv read_csv
    df = pd.read_excel(input_bestand)
except FileNotFoundError:
    print(f"FOUT: Kan het bestand '{input_bestand}' niet vinden in deze map.")
    print("Check of de naam exact klopt (hoofdletters!).")
    exit()
except Exception as e:
    print(f"Er ging iets mis bij het openen: {e}")
    exit()

# Even checken of de kolommen kloppen
print("Gevonden kolommen:", df.columns.tolist())

js_content = "const songs = [\n"

teller = 0
for index, row in df.iterrows():
    # Pas deze namen aan als ze in je Excel anders heten!
    # Ik gok op: 'Artiest', 'Titel', 'Jaartal', 'Spotify Link'
    # We gebruiken .get() zodat het niet crasht als een kolom net anders heet
    
    # Zoek flexibel naar artiest
    artiest = row.get('Artiest') or row.get('Artist') or "Onbekend"
    
    # Zoek flexibel naar titel
    titel = row.get('Titel') or row.get('Track Name') or row.get('Title') or "Onbekend"
    
    # Zoek flexibel naar jaartal
    jaar = row.get('Jaartal') or row.get('Year') or row.get('Release Date') or "0000"
    
    # Zoek flexibel naar link
    link = row.get('Spotify Link') or row.get('Link') or row.get('Track URI') or ""
    
    # ID schoonmaken
    clean_id = clean_spotify_id(link)
    
    if clean_id: # Alleen toevoegen als er een link is
        # We gebruiken repr() om veilig om te gaan met aanhalingstekens in titels (zoals "Don't")
        js_line = f'  {{ id: {teller}, artist: {repr(str(artiest))}, title: {repr(str(titel))}, year: {jaar}, uri: "{clean_id}" }},'
        js_content += js_line + "\n"
        teller += 1

js_content += "];"

with open(output_bestand, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Succes! Er zijn {teller} liedjes omgezet naar '{output_bestand}'.")