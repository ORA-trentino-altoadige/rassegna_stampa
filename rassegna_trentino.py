"""
Rassegna stampa Trentino-Alto Adige
Autore: Simone Magnolini (FBK)
Descrizione:
  - Raccoglie notizie da feed RSS di testate locali
  - Filtra per parole chiave
  - Genera un riassunto giornaliero in formato Markdown (e PDF opzionale)
"""

import feedparser
from datetime import datetime
from pathlib import Path
from textwrap import shorten
from fpdf import FPDF
import textwrap
import re


# =============================
# CONFIGURAZIONE
# =============================

# Fonti locali (RSS feed)
FEEDS = {
    "L'Adige": "https://www.ladige.it/rss",
    "Il Dolomiti": "https://www.ildolomiti.it/rss.xml",
    "Salto.bz": "https://www.salto.bz/rss.xml",
    "Südtirol News": "https://www.suedtirolnews.it/feed",
    "Rai TGR Trento": "https://www.rainews.it/tgr/trento/notiziari/video-nazio-rss",
    "Rai TGR Bolzano": "https://www.rainews.it/tgr/bolzano/notiziari/video-nazio-rss"
}

# Parole chiave per filtrare le notizie (puoi personalizzarle)
KEYWORDS = [
    "Trento", "Bolzano", "Val di Non", "Val Pusteria", "Pergine", "Trentino", "Alto Adige",
    "autonomia", "sanità", "università", "energia", "trasporti", "innovazione"
]

# Percorso di output
OUTPUT_DIR = Path("rassegna_stampa")
OUTPUT_DIR.mkdir(exist_ok=True)

# =============================
# FUNZIONI PRINCIPALI
# =============================

def estrai_notizie(feed_url, source):
    """Estrae notizie da un feed RSS"""
    feed = feedparser.parse(feed_url)
    notizie = []
    for entry in feed.entries:
        titolo = entry.title
        link = entry.link
        descrizione = getattr(entry, "summary", "")
        data_pubblicazione = getattr(entry, "published", "N/D")

        # Filtro per parole chiave
        if any(kw.lower() in titolo.lower() or kw.lower() in descrizione.lower() for kw in KEYWORDS):
            notizie.append({
                "fonte": source,
                "titolo": titolo,
                "link": link,
                "descrizione": descrizione,
                "data": data_pubblicazione
            })
    return notizie


def genera_rassegna():
    """Crea il file Markdown con la rassegna del giorno"""
    oggi = datetime.now().strftime("%Y-%m-%d")
    tutte_le_notizie = []

    for fonte, url in FEEDS.items():
        try:
            notizie = estrai_notizie(url, fonte)
            tutte_le_notizie.extend(notizie)
        except Exception as e:
            print(f"⚠️ Errore nella fonte {fonte}: {e}")

    if not tutte_le_notizie:
        print("Nessuna notizia trovata per oggi.")
        return None

    # Ordina per data e fonte
    tutte_le_notizie.sort(key=lambda x: (x["fonte"], x["data"]))

    # Genera contenuto Markdown
    md_path = OUTPUT_DIR / f"rassegna_{oggi}.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write(f"# 📰 Rassegna Stampa Trentino-Alto Adige – {oggi}\n\n")
        for n in tutte_le_notizie:
            f.write(f"## {n['titolo']}\n")
            f.write(f"**Fonte:** {n['fonte']}  \n")
            f.write(f"**Data:** {n['data']}  \n")
            f.write(f"🔗 [Leggi l’articolo]({n['link']})\n\n")
            f.write(f"{shorten(n['descrizione'], 300)}\n\n---\n\n")

    print(f"✅ Rassegna generata: {md_path}")
    return md_path


# =============================
# ESECUZIONE
# =============================

if __name__ == "__main__":
    md_file = genera_rassegna()
