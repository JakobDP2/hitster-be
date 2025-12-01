import pandas as pd
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import io

# --- CONFIGURATIE ---
input_bestand = 'Hitster_BE.xlsx' 
output_pdf = 'hitster_kaarten.pdf'

# --- FORMATEN ---
CARD_SIZE = 65 * mm  
COLS = 3             
ROWS = 4             
CHUNK_SIZE = COLS * ROWS 

MARGIN_X = (210 * mm - (COLS * CARD_SIZE)) / 2
MARGIN_Y = (297 * mm - (ROWS * CARD_SIZE)) / 2

# Iets minder marge aan de zijkanten voor tekst, zodat het grotere font past
MAX_TEXT_WIDTH = CARD_SIZE - 4 * mm

def clean_spotify_id(link):
    link = str(link).strip()
    if not link or link.lower() == 'nan': return ""
    if 'track/' in link: return link.split('track/')[1].split('?')[0]
    elif 'spotify:track:' in link: return link.split(':')[-1]
    return link

def draw_wrapped_text(c, text, x_center, y_top, font_name, font_size, line_height):
    c.setFont(font_name, font_size)
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        width = c.stringWidth(test_line, font_name, font_size)
        if width < MAX_TEXT_WIDTH:
            current_line.append(word)
        else:
            if current_line: lines.append(' '.join(current_line))
            current_line = [word]
    if current_line: lines.append(' '.join(current_line))
    
    # Bij meerdere regels: begin iets hoger zodat het blok gecentreerd blijft rond y_top?
    # Nee, we laten het zakken vanaf y_top.
    for i, line in enumerate(lines):
        y_pos = y_top - (i * line_height)
        c.drawCentredString(x_center, y_pos, line)

print(f"Bezig met inlezen van '{input_bestand}'...")
try:
    df = pd.read_excel(input_bestand)
except Exception as e:
    print(f"FOUT: {e}")
    exit()

c = canvas.Canvas(output_pdf, pagesize=A4)
width, height = A4
total_cards = len(df)

for i in range(0, total_cards, CHUNK_SIZE):
    chunk = df.iloc[i:i+CHUNK_SIZE]
    
    # ---------------- PAGINA 1: QR ----------------
    row_idx = 0
    col_idx = 0
    c.setStrokeColorRGB(0.8, 0.8, 0.8) 
    c.setLineWidth(0.5)
    
    for idx_in_chunk, (index, row_data) in enumerate(chunk.iterrows()):
        x = MARGIN_X + (col_idx * CARD_SIZE)
        y = height - MARGIN_Y - ((row_idx + 1) * CARD_SIZE)
        
        c.rect(x, y, CARD_SIZE, CARD_SIZE)
        
        link = row_data.get('Spotify Link') or row_data.get('Link') or ""
        if clean_spotify_id(link):
            qr = qrcode.QRCode(box_size=10, border=0)
            qr.add_data(str(index))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            qr_size = 32 * mm 
            qr_x = x + (CARD_SIZE - qr_size) / 2
            qr_y = y + (CARD_SIZE - qr_size) / 2
            c.drawImage(ImageReader(img_buffer), qr_x, qr_y, width=qr_size, height=qr_size)

        col_idx += 1
        if col_idx >= COLS:
            col_idx = 0
            row_idx += 1
            
    c.showPage() 
    
    # ---------------- PAGINA 2: TEKST (AANGEPAST) ----------------
    row_idx = 0
    col_idx = 0
    
    for idx_in_chunk, (index, row_data) in enumerate(chunk.iterrows()):
        mirrored_col_idx = (COLS - 1) - col_idx
        x = MARGIN_X + (mirrored_col_idx * CARD_SIZE)
        y = height - MARGIN_Y - ((row_idx + 1) * CARD_SIZE)
        
        c.setStrokeColorRGB(0.9, 0.9, 0.9)
        c.rect(x, y, CARD_SIZE, CARD_SIZE)
        
        artiest = str(row_data.get('Artiest') or row_data.get('Artist') or "Onbekend")
        titel = str(row_data.get('Titel') or row_data.get('Track Name') or "Onbekend")
        raw_year = str(row_data.get('Jaartal') or row_data.get('Year') or "????")
        jaar = raw_year.split('.')[0] if '.' in raw_year else raw_year
        
        center_x = x + (CARD_SIZE / 2)
        
        # --- NIEUWE POSITIES ---

        # 1. ID (Rechtsboven)
        c.setFont("Helvetica", 7) 
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.drawRightString(x + CARD_SIZE - 3*mm, y + CARD_SIZE - 5*mm, str(index))
        c.setFillColorRGB(0, 0, 0)

        # 2. ARTIEST (Bovenaan)
        artist_upper = artiest.upper()
        # Y = iets onder de bovenrand
        draw_wrapped_text(c, artist_upper, center_x, y + CARD_SIZE - 12*mm, "Helvetica-Bold", 11, 4*mm)

        # 3. JAARTAL (Midden - ietsje omhoog geschoven voor meer ruimte onderaan)
        c.setFont("Helvetica-Bold", 42) 
        # y + (CARD_SIZE/2) - 3mm (was -5mm, dus hij gaat 2mm omhoog)
        c.drawCentredString(center_x, y + (CARD_SIZE/2) - 3*mm, jaar)

        # 4. TITEL (Onderaan - LAGER en GROTER)
        # Y = 11mm vanaf bodem (was 18mm, dus hij zakt flink)
        # Font = 10.5 (was 9)
        draw_wrapped_text(c, titel, center_x, y + 11*mm, "Helvetica", 10.5, 4*mm)

        # Volgende
        col_idx += 1
        if col_idx >= COLS:
            col_idx = 0
            row_idx += 1

    c.showPage()

c.save()
print(f"Klaar! Alain zou trots zijn. PDF: {output_pdf}")