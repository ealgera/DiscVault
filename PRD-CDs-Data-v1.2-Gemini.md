# Product Requirements Document – CD Manager (DiscVault)

**Projectnaam**: CD Manager (werknaam: DiscVault)
**Versie**: 1.2 (Toegevoegd: Tagging, Aangepast: PWA -> Mobile Web)
**Datum**: 02-01-2026
**Auteur**: Eric Algera (Redactie: Gemini)
**Status**: Concept – v1 (Mobile Web + Tagging + AI-Enriched)

---

## 1. Executive Summary

**Wat is de CD Manager?**
De CD Manager is een intelligente webapplicatie voor het beheren van fysieke muziekcollecties. De toepassing draait op een thuisserver in een Docker container en is geoptimaliseerd voor gebruik op mobiele apparaten.
De frontend is een responsive webapp die goed werkt op mobiel/tablet/desktop. De server is altijd actief; clients verbinden intern via LAN en extern via een reverse proxy (bijv. Nginx).

**Kernfunctionaliteiten:**

- CD’s toevoegen, wijzigen, archiveren/verwijderen (met historie)  
- Metadata en kenmerken opslaan (titel, artiest(en), tracks, jaar, codes, notities, fysieke locatie, covers, SPARS-code etc.)  
- Snel en uitgebreid zoeken (incl. combinaties EN/OF, “bevat”/LIKE, en zoeken op track)  
- CD’s gemakkelijk invoeren via barcode/UPC/EAN (mobiel) + met automatische online dataverrijking.  
- Rapportages en lijsten genereren voor ordenen en inzicht (per artiest/jaar/genre/locatie, duplicaten, ontbrekende data)
-   Organiseren: Inzicht in waar een CD fysiek staat en sorteermechanismen om de kast te ordenen.
-   **AI Features**: Automatisch categoriseren of samenvatten van album reviews (indien beschikbaar).

**Waarom bouwen we dit?**
Voor verzamelaars met een uitgebreide fysieke muziekcollectie die behoefte hebben om inzicht te krijgen in de verzameling, dubbele aankopen te voorkomen en fysiek snel de juiste CD te kunnen vinden.

---

## 2. Probleemstelling

**Huidige situatie:**

* We weten niet exact welke CD's of welke specifieke persingen we hebben.
* We weten niet of we dubbele CD's hebben.
* We weten niet waar een CD fysiek staat (in welke kast of doos).
* We weten niet op welke CD een bepaalde track staat.
* We missen de mogelijkheid om eigen kenmerken (sfeer, herkomst) aan een CD te hangen.
* Handmatige invoer kost tijd; online data is versnipperd; covers zijn niet consistent.


**Kans:**
Een applicatie die fungeert als de persoonlijke catalogus, altijd bereikbaar via de smartphone, met krachtige filter- en zoekmogelijkheden, en die:
- invoer frictieloos maakt (barcode → voorstel → bevestigen)  
- zoekbaarheid maximaliseert (incl. tracks en combinaties)  
- fysieke vindbaarheid ondersteunt (locatievelden + rapporten)  
- data lokaal houdt (privacy, geen cloud-lock-in)

---

## 3. Doelstellingen & Goals

### 3.1 Functionele doelen

* **Beheer & Invoer:**
* 
* **Tagging Systeem:** Flexibel toevoegen van eigen labels aan albums (P0).
* **Collectiebeheer**: CRUD + archief/historie met aanpasbare metadata zoals titel, artiest, jaar, en meer.  
* **Frictieloze invoer**: barcode/UPC/EAN + online lookup + handmatige correctie en automatische fetch van metadata (Discogs/MusicBrainz)  
* **Zoekervaring**:
  - snel zoeken (1 zoekbalk)  
  - geavanceerd zoeken, ook op metadata (EN/OF, filters, “bevat”, bijv. "Jaar > 1990 AND Genre = Jazz")  
  - track-zoek (tracktitel en tracknummer)  
  - Full-text search op alle velden.
- **Inzicht & ordening**:
  - overzichten per artiest/jaar/genre/type/locatie  
  - duplicatenrapport  
  - exporteerbare lijsten (CSV/PDF later)  
  - totale aantallen (totaal, p0er artiest, per genre, per jaar).
  - Financieel inzicht (optioneel: aankoopwaarde).
* **Volledig beeld:**
* Statistieken per artiest, genre, jaar en *tag*.
* Fysieke locatie registratie.
* **Mobile First:**
* De interface moet volledig bedienbaar zijn op een telefoon (grote targets, geen hover-states), aangezien dit het primaire device is bij de platenkast.

### 3.2 Gebruikersdoelen

* "Ik wil al mijn CD's met de tag 'Jeugdsentiment' zien."
* "Ik sta in de winkel en wil weten of ik deze specifieke editie al heb."
* "Ik wil weten in welke kast de CD 'The Mirror Pool' staat."
* "Ik zien of ik dubbele CD's in mijn bezit heb."
* "Ik wil op welke CD de track 'Swan' staat."
* "Ik wil een lijst van alle CD's met genre jazz uit de jaren 80."

---

## 4. Doelgroep & Persona’s

### 4.1 Doelgroep
Muziek-liefhebbers en verzamelaars met een thuisserver (HomeLab) en een vrij grote fysieke collectie van 100+ CD's en Blu-ray's.

### 4.2 Persona’s

* **Persona A – De Beheerder (Owner):**
  *  Wil snel schrijven en invoeren (scannen).
  *  Heeft behoefte aan back-ups en data-export.
  *  Zet metadata naar eigen hand (bijv. eigen genres indelen).
* **Persona B – De Verzamelaar:** 
  - Wil structuur en volledigheid, editions, covers, notities, duplicaatcontrole. Gebruikt tags om persingen en conditie ("Mint", "Krassen") aan te geven.
* **Persona C – De Luisteraar:** 
  - Gebruikt tags voor sfeer ("Rustig", "Zondagochtend") en wil snel iets vinden.
- **Persona D – De Zoeker**  
  - wil vooral “heb ik dit?” en “waar ligt het?” en “waar staat die track?”  
  - Zoekt op "Ik ben in de stemming voor..." (AI search?).   
  - Wil de cover zien voor de herkenning.
- **Persona E – e Opruimer**  
  - wil ordenen, lijstjes printen/exporteren, en makkelijker opruimen/labelen

---

## 5. Scope & Non-scope

### 5.1 In scope v1 (MVP)

* **Database & Modellen:**
* Standaard CD-data (Titel, Artiest, Tracks, Jaar, Covers).
* **Custom Tags:** Vrije invoer, kleur-codeerbaar (bijv. "Favoriet", "Nog luisteren").
* **Locatie:** Veld voor Kast/Plank.

**Data-objecten**
- **Release (CD/media-item)** met metadata:
  - Titel  
  - Artiest(en) (meerdere)  
  - Tracklist (tracknummer, titel; optioneel duur)  
  - Jaar (releasejaar)
  - Aankoopdatum  
  - Codes: UPC/EAN, catalogusnummer, SPARS  
  - Genre(s), te selecteren uit een default list  
  - Type: CD / Blu‑ray (uitbreidbaar)  
  - Notitie (vrij veld)  
  - Fysieke locatie (zie 5.1.3)
  - Tags  
  - Eigen rating  (1-5 sterren)   
  - Covers (min. front; opt. back/inside)

  **Covers:**
- Front cover (verplicht), Back/Inner (optioneel). Max resolutie 800x800px (server-side resize). Opslag als bestand in `/covers` map, niet in DB.
- JPG/PNG  
- Bestanden op disk (niet in DB), DB bewaart paden + checksum  
- Automatische thumbnail-generatie (voor performance)

* **Invoer:**
* Zoeken op Barcode/Titel via externe API (Discogs API).
  - Barcode scan op mobiel → lookup  
* Lookup-resultaten tonen als lijst → gebruiker kiest juiste match → import metadata + covers  
* Handmatige correctie en aanvulling (inclusief tags toevoegen tijdens import).
* Handmatig toevoegen (form) als niet online gevonden  
* Altijd mogelijkheid om data te corrigeren vóór opslaan  
* Duplicaatwaarschuwing (barcode/cataloguscode)

* **Zoeken:**
* Snelzoeken (1 veld) over titel, artiest, track, code, notitie  
  - Zoekbalk (global search).
* filters (jaar, type, genre, locatie, enzovoort)  
* Combinaties (Boolean operators: AND, OR, NOT).   
* “bevat” (LIKE) + exacte match
* AI-ondersteund zoeken ("Zoek albums die lijken op...").
* Sorteren en pagineren

**Fysieke locatie (vindbaarheid)**
* Locatiemodel (simpel maar krachtig):
  - Opslagtype: Kast / Box / Krat / Anders  
  - Locatienaam (bijv. “Kast woonkamer”)  
  - Sectie/Rij/Plank (vrij)  
  - Positie (nummer)  
* Rapportage om per locatie te sorteren en eventueel labels te maken (v2)

**Rapportage & inzichten**
- Overzichtsschermen:
  - totalen (aantal releases, aantal artiesten, per type)  
  - per artiest / per jaar / per genre / per locatie  
  - duplicaten (exact + “mogelijk”)  
- Export/back-up

**Export / back-up / restore**
- Eén “export bundle” (ZIP) met:
  - database dump (bijv. SQLite file of JSON + schema versie)  
  - covers + thumbnails  
  - manifest.json met versie, datum, checksums  
- Import/restore met validatie en migratiepad (schema versie)

* **Techniek:**
* Webinterface geoptimaliseerd voor mobiel (Mobile First).
* Docker container voor eenvoudige hosting.


### 5.2 Niet in scope v1

* Complex gebruikersbeheer (single user is de standaard).
* Offline-sync (applicatie gaat uit van verbinding met thuisserver).
* Audio rippen, afspelen of streaming.   
* Multi-user rollen/permissions uitgebreid (alleen basic auth in v1)  
* Automatische herkenning via audio fingerprinting  
* Geavanceerde label/print workflows (PDF labels)  
* Volledig editten van track-duren, credits, matrix/runout (kan later)
*   Sociale features (delen van lijsten met vrienden).
*   Geautomatiseerde waardebepaling (koppelen met marktplaatsen).

---

## 6. Belangrijkste Features & Prioritering

### 6.1 Feature-overzicht (MoSCoW)

**P0 – Must Have (De basis)**

* **CRUD Functionaliteit:** CD's aanmaken, lezen, updaten, verwijderen.
* **Snelle invoer** Barcode invoer + lookup + keuze match + import  
* **Covers** Covers uploaden en tonen.
* **Tagging Systeem:** Het kunnen aanmaken, toewijzen en verwijderen van tags bij albums.
* **Filteren op Tags:** "Toon alle CD's met tag X".
* **MusicBrainz Integratie:** Ophalen metadata.
* **Mobile Responsive Design:** Goed werkend op smartphone (iOS/Android browsers).
* **Locatie Beheer:** Veld om fysieke plek aan te duiden + sorteerbare lijsten.
* **Duplicaten** Duplicaatdetectie (exact)  
* **Snelzoeken** Snelzoeken + geavanceerd zoeken (EN/OF, bevat)  
* **Export** Export/restore bundle (ZIP)  
* **Responsive** Responsive mobile-first UI (werkt goed op telefoon/tablet)  
* **Deployment** Deployment: LAN-first + externe toegang via reverse proxy (Nginx)
* **Database** Database structuur (SQLModel/SQLite).


**P1 – Should Have**

* **AI Search:** "Natural language" queries via Gemini.
* **Batch Tagging:** Meerdere CD's selecteren en in één keer een tag geven.
* **Bulk** Bulk acties (meerdere items tegelijk locatie wijzigen)  
* **Thumbnails** Thumbnail/caching optimalisaties  
* **Export** CSV-export van lijst/rapport  
* **Audit** Audit log (wie/wat/wanneer) – ook nuttig voor “undo”
* **Statistics** Statistieken dashboard (Grafieken: Genre verdeling, Jaar van uitgave).

**P2 – Nice to Have**

* Export naar PDF/CSV.
* Dark Mode.
* Willekeurige album suggestie ("Shuffle").
* Labels/QR-codes printen voor dozen/kasten  
* Slimme “orde-advies” (bijv. alfabetisch per artiest, of per genre)  
* Edition management (meerdere versies van dezelfde release)  
* Integratie met externe bronnen (meerdere providers) + mapping UI  
* Voice search (mobiel)
* Authenticatie & accounts (Google OAuth als IDP) + basis autorisatie


---

## 7. User Stories (Aangevuld)

### 7.1 Beheer

* Als gebruiker wil ik tijdens het toevoegen van een CD direct de tag 'Nieuw gekocht' kunnen toevoegen.
* Als gebruiker wil ik een lijst van mijn eigen tags beheren (bijv. typfouten in tags corrigeren).
*  Als gebruiker wil ik een CD handmatig kunnen toevoegen   
   - AC: formulier valideert verplichte velden; opslaan toont detailpagina
*   Als gebruiker wil ik CD's toevoegen door middel van een barcode scan (camera of toetsenbord), zodat ik niet alles hoef over te typen.
   - AC: scan → resultatenlijst → keuze → conceptdetail → opslaan  
   - AC: bij bestaande barcode waarschuwing + optie “toch toevoegen”
*   Als gebruiker wil ik meerdere artiesten aan een album kunnen koppelen (bijv. "Various Artists" of samenwerkingen).
* Als gebruiker wil ik een export kunnen maken en later herstellen  
   - AC: export bundle bevat DB + covers; restore levert identieke collectie

### 7.2 Zoeken

* Als gebruiker wil ik snel kunnen zoeken op titel/artist/track/code.   
* Als gebruiker wil ik zoeken op alle CD's die de tag 'Instrumentaal' hebben EN uit het jaar '1995' komen.
* Als gebruiker wil ik geavanceerd kunnen filteren  
   - AC: filters combineren; EN/OF/NOT werkt zichtbaar en voorspelbaar

### 7.3 Organiseren

* Als gebruiker wil ik mijn CD verzameling kunnen organiseren op locatie, zodat ik weet wat er in 'Doos 3' zit.
* Als gebruiker wil ik een aangepast veld "Plank" invullen zodat ik weet waar de CD staat.
* Als gebruiker wil ik fysieke locaties kunnen beheren  
   - AC: locatielijst; items toewijzen; lijst per locatie sorteerbaar   
* Als gebruiker wil ik een rapportage kunnen genereren welke de CD's sorteert op "Fysieke Locatie" en vervolgens op Artiest, zodat ik mijn kast in één keer kan ordenen.   
* Als gebruiker wil ik een CD kunnen archiveren/verwijderen  
   - AC: item verdwijnt uit standaardlijst, blijft terugvindbaar in “Archief”


---

## 8. UX & UI Richtlijnen

### 8.1 Algemeen

#### Principes
* **Mobile-first** Mobile-first, snelle interactie (grote knoppen, korte formulieren)  
* **Progressive disclosure** “Progressive disclosure”: standaard simpel, advanced optioneel  
* **Fouten** Fouten voorkomen: suggesties, auto-complete, duplicaatwaarschuwingen  
* **Bewerken** Altijd “bewerken” vanaf detailpagina
* **Tags** Tags moeten duidelijk zichtbaar zijn als 'chips' of labels bij een album (bijv. gekleurde badgdes).
* **Performance:** Snelle laadtijden, trage animaties vermijden bij grote lijsten.
* **Cover Centric:** In lijstweergaven is de cover het belangrijkste herkenningspunt.

#### Kernschermen (v1)
- Dashboard (totalen + snelle acties)  
- Lijst (filter/sort/search)  
- Detail (cover, metadata, tracks, locatie)  
- Add flow (scan/handmatig)  
- Rapporten (duplicaten, per locatie, etc.)  
- Instellingen (lookup provider(s), export)
  - (v2) Inloggen/auth (Google OAuth)

### 8.2 Taal

* Nederlands.
* Duidelijke terminologie kort en duidelijk, geen vakjargon (Gebruik "Tag" of "Label", kies er één en wees consistent).
* Toegankelijkheid:
  - voldoende contrast  
  - grote tap-targets  
  - labels + foutmeldingen die uitleggen *wat* en *hoe op te lossen*
* WCAG 2.1 AA compliance (focus states, screenreader support).

---

## 9. Technische Requirements

### 9.1 Architectuur & stack

* **Server (Docker, Backend, thuisserver):**
* Python / FastAPI / SQLModel (SQLite).   
* `uv` voor dependency management, `.env` voor secrets.   
* SQLite FTS5 voor full-text search (sterk aanbevolen)  
* Migratie-tooling (Alembic of alternatief)  
* Bestandsopslag voor covers + thumbnails  
* AI: Pydantic-AI (v2) + Google Gemini (voor metadata verrijking of semantic search in latere fase).   
* (v2) Authenticatie via Google OAuth (IDP). In v1 alvast rekening houden met: gebruikers-/sessiemodel, auth-middleware, en scopes/roles (al is er maar 1 gebruiker).
* Python-Discogs-client (of MusicBrainz).

* **Frontend:**
* HTML/JS (Vue of React aanbevolen, *Suggestie: Vue.js is vaak lichter en makkelijker voor single-developer projecten.*).
* Framework: Tailwind CSS (voor eenvoudige mobile-first styling).
* Responsive.
* Camera/barcode: Web APIs (waar beschikbaar)


### 9.2 Data & modellen

* **Tabellen (Conceptueel, globaal):**
- Album(id, title, artists, year, genre, type, upc_ean, catalog_no, spars, notes, created_at, updated_at, archived_at, tag)  
- Artist(id, name, tag)  
- ReleaseArtist(release_id, artist_id, role/order)  
- Track(id, release_id, track_no, title, duration?)  
- Location(id, storage_type, name, section, shelf, position)  
- Cover(id, release_id, kind(front/back/inside), path, checksum, width, height, bytes)
* Tag (Naam, Kleur)
* AlbumTagLink (Koppeltabel voor Many-to-Many relatie tussen Album en Tag).
* Genre (id, name)

### 9.3 API (globaal)
- /releases (list, create)  
- /releases/{id} (read, update, archive/delete)  
- /search (quick)  
- /advanced-search (query builder payload)  
- /lookup (barcode → provider results)  
- /export (create bundle)  
- /import (restore bundle)  
- /locations (CRUD)  
- /stats (dashboards)

### 9.4 Security & Deployment

* Docker container.
* Intern toegankelijk binnen LAN  
* Extern toegang via Reverse Proxy (bijv. Traefik of Nginx Proxy Manager) op het thuisnetwerk.
* HTTPS via reverse proxy (bijv. Let’s Encrypt) aanbevolen  
* Back-ups lokaal; geen cloud afhankelijkheid  
* Logging met minimale privacy-impact (geen gevoelige data)
*   OAuth2 (Google) optioneel, anders een simpele username/password flow (HTTP Basic Auth of JWT). Omdat het thuis is, is basic auth over HTTPS vaak voldoende.
*   Data verlaat nooit de server (behalve voor Discogs API lookups, logs niet naar buiten).

---

## 10. Rapportage & Logging

### 10.1 Rapportage (v1)
* Loggen van import-acties.
* Foutmeldingen bij mislukte API calls (MusicBrainz).
* Duplicaten (exact + later fuzzy)  
* Per artiest / per jaar / per type / per locatie  
* Export CSV (P1) / PDF (P2)

### 10.2 Logging
* API errors, DB errors, lookup errors  
* Export/import acties (wie/wanneer + resultaat)  
* Optioneel audit log voor mutaties
* Logt API requests (als optioneel aanstaat i.v.m. privacy).
* Logt fouten bij Discogs API calls.
* Logt Backup acties.

---

## 11. Risico’s & Aannames

### 11.1 Risico’s
* Online lookup bronnen veranderen of limiteren (rate limits, API keys)  
  - Oplossing: Caching in SQLite en requests beperken in UI.
* Barcode scan werkt niet op alle devices/browsers even goed  
* Duplicaten zijn soms “bijna gelijk” (fuzzy matching vereist)  
* Cover-opslag kan veel ruimte innemen → thumbnails + limieten nodig
* Wildgroei aan tags. *Mitigatie: Autocomplete voorstellen bij het intypen van tags.*

### 11.2 Aannames
* De gebruiker zorgt zelf voor toegang tot de server van buitenaf (via VPN of Proxy) als dat gewenst is.
* Thuisserver is betrouwbaar en draait 24/7 of vaak genoeg  
* Gebruiker zit meestal op hetzelfde netwerk als server  
* Moderne browser beschikbaar op mobiel/tablet

### 11.3 Afhankelijkheden
* Browser support camera API’s  
* Eventuele externe data providers (optioneel)
*  Discogs API account (Client ID/Secret).
*  Python packages ecosystem.
*  Github/Docker voor updates.

---

## 12. Roadmap

### Fase 1 (MVP)

* Opzet Datamodel + CRUD + locaties.
* Snelzoeken + FTS  
* Handmatig toevoegen + basis UI (mobile-first)  
* Implementatie Tagging systeem (Backend + Frontend).
* Basis UI voor mobiel.
* Covers weergave en upload.
* Export/restore  
* Deployment: LAN-first + Nginx reverse proxy voor externe toegang

### Fase 2
* Barcode scanner integratie + lookup + import covers.
* Integratie Discogs API (Zoeken op Barcode/Artiest).
* Geavanceerd zoeken (Filters).
* Duplicaatdetectie  
* Rapporten (duplicaten, per locatie)  
* Performance tuning

### Fase 3 – v2 ideeën
- Authenticatie (Google OAuth als IDP) + basis autorisatie  
- Labels/QR print  
- Fuzzy duplicates + edition management  
- Bulk actions + CSV/PDF exports

### Fase 4
* Integratie Gemini AI voor "Vraag & Antwoord" over de collectie.
* AI functionaliteiten (Slim zoeken).
* Dashboard met grafieken.

---

