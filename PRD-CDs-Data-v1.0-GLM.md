# Product Requirements Document – CD's Database (Music Manager)

**Projectnaam**: CD's Database (interne naam: MusicDB)  
**Versie**: 1.1 (Herzien)  
**Datum**: 03-01-2026  
**Auteur**: Eric Algera  
**Status**: Concept – v1 (Snapshot sync + PWA + AI-ondersteuning)

---

## 1. Executive Summary

**Wat is de CD's Database?**
De CD's Database is een intelligente webapplicatie voor het beheren van een fysieke muziekcollectie (CD's, DVD's, Blu-ray's). De applicatie draait als een self-hosted oplossing op een thuisserver binnen een Docker container. Het doel is om een centrale "single source of truth" te creëren voor de verzameling.

Gebruikers kunnen:
*   De volledige collectie beheren: CD's opvragen, toevoegen, wijzigen en verwijderen (soft-delete).
*   Metadata opslaan: O.a. covers (front/back), tracklists, genre, jaar en SPARS-code.
*   Geavanceerd zoeken: Zoeken op titel, artiest, track, jaar, met combinaties (EN/OF) en fuzzy search.
*   Gemakkelijke invoer: CD's toevoegen door middel van barcode-scanning (EAN/UPC) met automatische online dataverrijking.
*   Organiseren: Inzicht in waar een CD fysiek staat en sorteermechanismen om de kast te ordenen.
*   **AI Features**: Automatisch categoriseren of samenvatten van album reviews (indien beschikbaar).

**Voor wie?**
Voor verzamelaars met een uitgebreide fysieke muziekcollectie die behoefte hebben aan digitaal inzicht, beheersgemak en efficiëntie.

**Waarom bouwen we dit?**
Om de chaos van een grote verzameling om te zetten in gestructureerde data:
*   Elimineren van dubbele aankopen.
*   Snel vindbaar maken van specifieke tracks of albums.
*   Ondersteunen bij het fysiek organiseren van de kast.

---

## 2. Probleemstelling

**Huidige situatie:**
Er is momenteel geen centraal overzicht. Dit leidt tot:
*   Onzekerheid over bezit: "Heb ik deze CD al?"
*   Inefficiëntie: Tijd kwijt aan zoeken in fysieke kasten.
*   Verlies van overzicht: Onbekendheid over de exacte opslaglocatie (welke kast/plank).
*   Gebrek aan detail: Onwetendheid over specifieke versies (remasters) of trackdetails.

**Kans:**
Een Progressive Web App (PWA) die fungeert als een interactieve catalogus en inventory-systeem, toegankelijk vanaf elke device in huis, met de kracht van AI en metadata omgevingen om data-invoer te minimaliseren.

---

## 3. Doelstellingen & Goals

### 3.1 Functionele doelen
*   **CD Beheer (CRUD):** Snelle invoer via barcode (EAN/UPC) en automatische fetch van metadata (Discogs/MusicBrainz). Bewerkbare metadata inclusief SPARS-code en eigen opmerkingen.
*   **Inzicht & Statistieken:**
    *   Totale aantallen (totaal, per artiest, per genre, per jaar).
    *   Financieel inzicht (optioneel: aankoopwaarde).
    *   Duplicaten detection.
*   **Uitgebreid Zoeken:**
    *   Full-text search op alle velden.
    *   Filteren op metadata (bijv. "Jaar > 1990 AND Genre = Jazz").
    *   Zoeken op lyrics of trackinhoud (indien toegevoegd).
*   **Device Ondersteuning:**
    *   PWA: Installeerbaar als app op mobiel/tablet voor offline gebruik (read-only modus).
    *   Responsive design voor grote en kleine schermen.

### 3.2 Gebruikersdoelen (User Journeys)
*   "Ik wil weten of ik de CD 'The Mirror Pool' van Lisa Gerrard heb."
*   "Ik wil fysiek vinden waar de CD staat (bijv. Kast A, Plank 2)."
*   "Ik zien of ik dubbele CD's in mijn bezit heb."
*   "Ik wil op welke CD de track 'Swan' staat."
*   "Ik wil een lijst van alle jazz CD's uit de jaren 80."

---

## 4. Doelgroep & Persona’s

### 4.1 Doelgroep
Muziek-liefhebbers en verzamelaars met een thuisserver (HomeLab) en een fysieke collectie van 100+ CD's.

### 4.2 Persona’s
*   **Persona A – De Beheerder (Owner):**
    *   Wil snel schrijven en invoeren (scannen).
    *   Heeft behoefte aan back-ups en data-export.
    *   Zet metadata naar eigen hand (bijv. eigen genres indelen).
*   **Persona B – De Luisteraar (Gebruiker):**
    *   Gebruikt de app vaak op de telefoon in de luisterruimte.
    *   Zoekt op "Ik ben in de stemming voor..." (AI search?).
    *   Wil de cover zien voor de herkenning.

---

## 5. Scope & Non-scope

### 5.1 In scope v1 (MVP)
*   **Database:** Single-file SQLite database op de server.
*   **Metadata:**
    *   **Covers:** Front cover (verplicht), Back/Inner (optioneel). Max resolutie 800x800px (server-side resize). Opslag als bestand in `/covers` map, niet in DB.
    *   **Velden:** Titel, Artiest(en), Tracklist (nummer + titel + duur), Jaar, Genre, Label, EAN/UPC code, SPARS code, Vrij veld (Opmerkingen), Aankoopdatum, Eigen Rating (1-5 sterren), **Fysieke Locatie** (vrij invulbaar tekstveld bijv. "Kast 1 - Plank A").
*   **Invoer:**
    *   Handmatig invoer formulier.
    *   Zoeken op EAN/UPC via externe API (bijv. Discogs API). Meerdere resultaten tonen -> 1 kiezen -> data importeren.
*   **Zoeken:**
    *   Zoekbalk (global search).
    *   Geavanceerd zoeken (Boolean operators: AND, OR, NOT).
*   **Export/Backup:**
    *   "Snapshot": Export van database (SQL dump) + covers (ZIP file).
    *   Importeerbaarheid van snapshots voor herstel.
*   **Dragers:** Ondersteuning voor types: CD, SACD, DVD-Audio, Blu-ray Audio.

### 5.2 Niet in scope v1 (mogelijk v2+)
*   Afspelen van muziek (streaming via server).
*   Digitale rippes beheren (MB files).
*   Sociale features (delen van lijsten met vrienden).
*   Geautomatiseerde waardebepaling (koppelen met marktplaatsen).
*   Multi-user support (ingewikkelde rechten per gebruiker; blijft lokaal/privé).

---

## 6. Belangrijkste Features & Prioritering

### 6.1 Feature-overzicht met prioriteit

**P0 – Must Have (v1)**
*   Database structuur (SQLModel/SQLite).
*   CRUD operaties (CD toevoegen/bewerken/verwijderen).
*   Zoekfunctionaliteit (Titel, Artiest).
*   Frontend (React/Vue) met basis weergave (Lijst & Detail).
*   Invoer via EAN/UPC code + API koppeling (Discogs).

**P1 – Should Have (v1.1)**
*   Geavanceerd zoeken (Filters, Boolean).
*   PWA functionaliteit (Service Worker, Manifest, Offline cache).
*   Covers uploaden en tonen.
*   Export/Import (Snapshot) functionaliteit.
*   "Fysieke Locatie" veld en sorteren hierop.

**P2 – Nice to Have / v2+**
*   AI Integratie: "Zoek albums die depressief zijn" (Vector search / embeddings).
*   Statistieken dashboard (Grafieken: Genre verdeling, Jaar van uitgave).
*   Bulk import via CSV.
*   Dark/Light mode switch.

---

## 7. User Stories (kern)

### 7.1 Beheer
*   Als gebruiker wil ik CD's toevoegen door middel van een barcode scan (camera of toetsenbord), zodat ik niet alles hoef over te typen.
*   Als gebruiker wil ik meerdere artiesten aan een album kunnen koppelen (bijv. "Various Artists" of samenwerkingen).
*   Als gebruiker wil ik een aangepast veld "Plank" invullen zodat ik weet waar de CD staat.

### 7.2 Zoeken
*   Als gebruiker wil ik zoeken op "Pool" en zowel results zien voor titels als voor artiesten bevatte dit woord.
*   Als gebruiker wil ik een filter kunnen toepassen (bijv. Genre: Rock AND Jaar: 1990-2000).

### 7.3 Organiseren
*   Als gebruiker wil ik een rapportage genereren dat de CD's sorteert op "Fysieke Locatie" en vervolgens op Artiest, zodat ik mijn kast in één keer kan ordenen.
*   Als gebruiker wil ik een visuele indicator zien als ik een dubbele CD probeer toe te voegen (op basis van EAN code).

### 7.4 Backup en inlezen
*   Als beheerder wil ik periodiek een "Snapshot" downloaden (database + afbeeldingen) als back-up.
*   Als beheerder wil ik na een crash of update een oude snapshot terug kunnen zetten.

---

## 8. UX & UI Richtlijnen

### 8.1 Algemene principes
*   **Mobile First:** De app wordt vaak gebruikt terwijl iemand bij de CD-kast staat.
*   **Performance:** Snelle laadtijden, trage animaties vermijden bij grote lijsten.
*   **Cover Centric:** In lijstweergaven is de cover het belangrijkste herkenningspunt.

### 8.2 Specifiek
*   **Kleurenpalet:** Donker thema als standaard (Dark Mode) om ogen te sparen in lage lichtruimtes, met een hoog contrast accentkleur (bijv. groen voor 'bezit', rood voor 'duplicaat').
*   **Navigatie:** Eenvoudige tab-balk onderaan op mobiel (Home, Zoeken, Toevoegen, Instellingen).

### 8.3 Taal & toegankelijkheid
*   **Taal:** Nederlands.
*   **Toegankelijkheid:** WCAG 2.1 AA compliance (focus states, screenreader support).

---

## 9. Technische Requirements

### 9.1 Architectuur & stack

*   **Server (thuisserver - Docker)**
    *   **Language:** Python 3.11+
    *   **Environment:** `uv` voor dependency management, `.env` voor secrets.
    *   **Framework:** FastAPI (hoge performance, async support).
    *   **Data Validation:** Pydantic v2.
    *   **Database:** SQLModel (wraps SQLAlchemy) + SQLite.
    *   **AI:** Pydantic-AI + Google Gemini (voor metadata verrijking of semantic search in latere fase).
    *   **External API:** Python-Discogs-client (of MusicBrainz).

*   **Frontend (Web/PWA)**
    *   **Framework:** Vue.js 3 (of React). *Suggestie: Vue.js is vaak lichter en makkelijker voor single-developer projecten.*
    *   **State Management:** Pinia (Vue) of Context API (React).
    *   **PWA:** Vite PWA plugin.
    *   **UI Component Library:** Headless UI of PrimeVue (voor mobiele componenten).

### 9.2 Data & modellen (globaal)

*   **CD Model:**
    *   `id`: UUID
    *   `title`: String
    *   `artists`: List[String] (Many-to-Many relatie voor normalize)
    *   `barcode`: String (Indexed)
    *   `year`: Int
    *   `genre`: String
    *   `spars_code`: String (AAD, ADD, DDD)
    *   `cover_path`: String
    *   `physical_location`: String
    *   `created_at`: DateTime

*   **Track Model:**
    *   `id`: UUID
    *   `cd_id`: ForeignKey
    *   `number`: Int
    *   `title`: String
    *   `duration`: String (MM:SS)

### 9.3 Security & Deployment
*   **Container:** Docker image gepushed naar私有 registry (of lokaal builden).
*   **Netwerk:** Draait in een Docker netwerk, reverse proxy via Nginx Proxy Manager of Traefik.
*   **Auth:** OAuth2 (Google) optioneel, anders een simpele username/password flow (HTTP Basic Auth of JWT). Omdat het thuis is, is basic auth over HTTPS vaak voldoende.
*   **HTTPS:** Zelf-signed certificaat of Let's Encrypt (via DuckDNS/No-IP).
*   **Privacy:** Data verlaat nooit de server (behalve voor Discots API lookups, logs niet naar buiten).

---

## 10. Rapportage & Logging

### 10.1 Rapportage
*   **Endpoints:**
    *   `/api/export` -> Genereert een ZIP file (DB dump + Images).
    *   `/api/report/duplicates` -> JSON lijst van mogelijke dubbele albums (zelfde titel + artiest).
    *   `/api/report/location` -> Lijst gesorteerd op fysieke locatie.

### 10.2 Logging
*   **Server:** Python `logging` module. Levels: INFO, WARNING, ERROR.
    *   Logt API requests (als optioneel aanstaat i.v.m. privacy).
    *   Logt fouten bij Discots API calls.
    *   Logt Backup acties.

---

## 11. Risico’s, Aannames & Afhankelijkheden

### 11.1 Risico’s
*   **API Limits:** Discogs API heeft rate limits (zoals 60 requests/min). Oplossing: Caching in SQLite en requests beperken in UI.
*   **Data Verlies:** SQLite op een Docker volume kan kwetsbaar zijn zonder backups. *Mitigatie:* Geautomatiseerde backup snapshots naar een map die gemount wordt op de host.
*   **Tijd:** Handmatig invoeren van 1000+ CD's is arbeidsintensief. Scannen moet werken.

### 11.2 Aannames
*   Gebruiker heeft een stabiele thuisserver.
*   Gebruiker heeft moderne smartphone (iOS Safari / Chrome Android) voor PWA.
*   De meeste CD's hebben een unieke EAN/UPC code.

### 11.3 Afhankelijkheden
*   Discogs API account (Client ID/Secret).
*   Python packages ecosystem.
*   Github/Docker voor updates.

---

## 12. Roadmap & Fasering

### Fase 1: De Basis (MVP)
*   **Doel:** Data opslaan en bekijken.
*   **Taken:**
    *   Database model opzetten (SQLModel).
    *   Basis API endpoints (CRUD).
    *   Frontend: Lijstweergave en Detailpagina.
    *   Handmatige invoer formulier.

### Fase 2: Integratie & Gemak
*   **Doel:** Snel invoeren.
*   **Taken:**
    *   Integratie Discogs API (Zoeken op Barcode/Artiest).
    *   Frontend: Scan functionaliteit (Camera access) en import flow.
    *   Covers weergave en upload.

### Fase 3: Geavanceerd gebruik & PWA
*   **Doel:** Overal en snel toegang.
*   **Taken:**
    *   PWA implementatie (Offline support read-only).
    *   Geavanceerd zoeken (Filters).
    *   Export/Import functionaliteit (Snapshots).

### Fase 4: AI & Stats (Nice to have)
*   **Doel:** Intelligentie.
*   **Taken:**
    *   Integratie Gemini AI voor "Vraag & Antwoord" over de collectie.
    *   Dashboard met grafieken.

---

### Toelichting op wijzigingen en toevoegingen:

1.  **Terminologie:** Ik heb de term "Noodpakket" (uit je samenvatting) laten vallen en vervangen door een professionelere naam, tenzij dat een interne codenaam is die je perse wilt houden.
2.  **"Rationering" in titel:** Ik heb dit veranderd naar "Registratie & Beheer" of verwerkt in de features. Rationering betekent meestal schaarste-regeling, wat niet lijkt te passen. Ik neem aan je bedoelde *Rating* (beoordelen) of *Registreren*. Ik heb **Rating (1-5 sterren)** expliciet toegevoegd aan de scope.
3.  **Tech Stack:** Ik heb SQLModel en FastAPI bevestigd. Voor de frontend heb ik Vue.js als suggestie toegevoegd (vanwege de goede integratie met Python/FastAPI projecten en lage leercurve), maar React blijft een optie.
4.  **Covers:** Ik heb specifieke eisen toegevoegd (max 800x800px, aparte opslag). Dit is cruciaal voor de performance van de database en de app.
5.  **Locatie:** Een van de sterkste use-cases (fysiek vinden) was een beetje onderbelicht. Ik heb het veld `physical_location` expliciet gemaakt en toegevoegd aan de sorteer- en rapportage opties.
6.  **PWA & AI:** Omdat deze in je oorspronkelijke titel stonden, heb ik ze concreet gemaakt in de Roadmap en Scope.
7.  **Discogs:** De standaard voor CD-metadata. Ik heb dit als de primaire bron voor data-invoer genomen.
