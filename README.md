# AI Horoskop - Generátor Personalizovaných Horoskopů

## O Projektu

**AI Horoskop** je proof-of-concept aplikace pro generování personalizovaných horoskopů pomocí umělé inteligence. Aplikace vytváří unikátní horoskopy na základě jména, data narození a astrologických výpočtů.

## Co Aplikace Dělá?

Aplikace vám umožňuje:

- 📅 **Zadání Osobních Údajů** - Vaše jméno a datum narození (v evropském formátu DD.MM.RRRR)
- 🌟 **Automatické Určení Znamení** - Systém automaticky určí vaše astrologické znamení
- 🔮 **Generování Horoskopů** - AI vytvoří unikátní horoskop speciálně pro vás
- 📊 **Dva Typu Horoskopů**:
  - **BASIC** - Základní verze (4 sekce)
  - **PROFI** - Rozšířená verze (9 sekcí s hlubší analýzou)

## Sekce Horoskopu

### BASIC verze obsahuje:

- **Definice Znamení** - Charakteristika vašeho astrologického znamení
- **Silné a Slabé Stránky** - Kladné vlastnosti a jak pracovat se slabinami
- **Práce a Kariéra** - Profese a pracovní styl
- **Vztahy a Partnerství** - Milostné vztahy a kompatibilita

### PROFI verze navíc obsahuje:

- **Zdraví a Pohoda** - Zdravotní tipy a péče o sebe
- **Finance** - Finanční doporučení
- **Duchovní Rozvoj** - Životní motto a inspirace
- **Praktické Tipy** - Rady pro každodenní život
- **Odpovědi na Osobní Otázky** - Odpovědi specifické pro vaše znamení

## Výstup

Aplikace generuje horoskop v podobě:

- 📄 **PDF dokumentu** - Snadno čitelný a tisknutelný formát
- 🎨 **Pěkného designu** - Esteticky zpracované a snadné na čtení

## Jak to Funguje?

1. Zadáte své osobní údaje
2. Systém vypočítá vaše astrologické údaje (znamení, astrologické číslo)
3. Umělá inteligence (Google Gemini) vygeneruje personalizovaný horoskop
4. Horoskop se převede do PDF a vytiskne/stáhne

## Technologie

Aplikace využívá:

- **Google Gemini AI** - Pro generování horoskopů
- **Astrologické výpočty** - Pro určení znamení a numerologie
- **HTML/PDF konverze** - Pro tvorbu finálního dokumentu

## Externí Závislosti

Aby aplikace fungovala, vyžaduje následující externí služby:

### 🤖 Google Gemini API

- **Popis**: Generuje personalizované horoskopy pomocí umělé inteligence
- **Verze**: gemini-2.5-flash nebo gemini-2.5-flash-lite
- **Požadavek**: API klíč od Google Cloud
- **Použití**: Generování textových sekcí horoskopů

### 🗄️ MongoDB

- **Popis**: Databáze pro ukládání horoskopů a uživatelských dat
- **Požadavek**: Připojovací řetězec (connection string)
- **Použití**: Ukládání metadat horoskopů, přístupových kódů a PDF souborů
- **Kolekce**:
  - `access_codes` - Validační tokeny
  - `horoscopes` - Metadata horoskopů
  - `horoscopes_pdf` - PDF soubory (GridFS)

### 📄 Gotenberg

- **Popis**: Konvertuje HTML do PDF formátu
- **Požadavek**: Běžící Docker kontejner nebo web služba
- **Použití**: Převod vygenerovaného HTML horoskopu na PDF
- **Port**: Obvykle 3000

## Instalace Závislostí

### MongoDB

```bash
# Via Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Gotenberg

```bash
# Via Docker
docker run -d -p 3000:3000 --name gotenberg gotenberg/gotenberg:latest
```

### Google Gemini API

1. Jděte na [Google Cloud Console](https://console.cloud.google.com)
2. Vytvořte nový projekt
3. Povolte Generative Language API
4. Vytvořte API klíč

## Konfigurační Proměnné

Aplikace vyžaduje následující proměnné v souboru `.env`:

```
GEMINI_API_KEY=váš_api_klíč_zde
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent

MONGO_DB_URL=mongodb://localhost:27017
MONGO_DB_NAME=horoscope_db

GOTENBERG_API_URL=http://localhost:3000/forms/chromium/convert/html
GOTENBERG_AUTH_USERNAME="gotenberg"
GOTENBERG_AUTH_PASSWORD="gotenberg"
```

## Proof-of-Concept

Toto je experimentální projekt demonstrující možnosti generování personalizovaných textů pomocí AI. Horoskopy jsou generovány pro zábavu a inspiraci.

---

**Vytvořeno jako proof-of-concept projekt pro generování personalizovaných horoskopů s AI.**
