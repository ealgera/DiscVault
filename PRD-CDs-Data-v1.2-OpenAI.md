# Product Requirements Document – CD’s Database

**Projectnaam**: CD’s Database  
**Versie**: 1.2 (wijzigingen: geen PWA, geen API limits, auth later)  
**Datum**: 02-01-2026  
**Auteur**: Eric Algera (basis) + redactie/aanvulling (ChatGPT)  
**Status**: Concept – v1.2 (LAN + reverse proxy, single-user, auth later voorbereid)

---

## 1. Executive summary

**Wat is CD’s Database?**  
CD’s Database is een lokale (thuisserver) applicatie om een fysieke CD-/Blu‑ray-/DVD‑collectie te registreren, te beheren en terug te vinden. De backend draait op een thuisserver in een Docker-container. De frontend is een responsive webapp die goed werkt op mobiel/tablet/desktop. De server is altijd actief; clients verbinden intern via LAN en extern via een reverse proxy (bijv. Nginx).

**Wat kan een gebruiker ermee?**

- CD’s toevoegen, wijzigen, archiveren/verwijderen (met historie)  
- Metadata en kenmerken opslaan (titel, artiest(en), tracks, jaar, codes, notities, fysieke locatie, covers, etc.)  
- Snel en uitgebreid zoeken (incl. combinaties EN/OF, “bevat”/LIKE, en zoeken op track)  
- CD’s gemakkelijk invoeren via barcode/UPC/EAN (mobiel) + online lookup (optioneel)  
- Rapportages en lijsten genereren voor ordenen en inzicht (per artiest/jaar/genre/locatie, duplicaten, ontbrekende data)

**Voor wie?**  
Voor mensen met een (middel)grote tot grote fysieke collectie die overzicht willen, dubbelingen willen voorkomen en snel willen vinden waar iets staat.

**Waarom bouwen we dit?**  
Omdat “in je hoofd” of in losse lijstjes bijhouden niet schaalbaar is. De app geeft:
- inzicht (wat heb ik, hoeveel, duplicaten)  
- vindbaarheid (welke track staat waar, waar ligt de CD)  
- praktische hulp bij fysiek ordenen (op kast/box/rij/positie)  

---

## 2. Probleemstelling

**Huidige situatie**

- Onzekerheid over:
  - welke CD’s er zijn en welke versies (persing/edition)  
  - dubbelingen en (bijna-)dubbelingen  
  - fysieke vindplaats (kast/box/rij/positie)  
  - op welke CD een track staat  
- Handmatige invoer kost tijd; online data is versnipperd; covers zijn niet consistent.

**Kans / oplossing**

Een snelle, mobiele, lokale app die:
- invoer frictieloos maakt (barcode → voorstel → bevestigen)  
- zoekbaarheid maximaliseert (incl. tracks en combinaties)  
- fysieke vindbaarheid ondersteunt (locatievelden + rapporten)  
- data lokaal houdt (privacy, geen cloud-lock-in)  

---

## 3. Doelstellingen & succescriteria

### 3.1 Functionele doelen (v1)

- **Collectiebeheer**: CRUD + archief/historie  
- **Frictieloze invoer**: barcode/UPC/EAN + online lookup (optioneel) + handmatige correctie  
- **Zoekervaring**:
  - snel zoeken (1 zoekbalk)  
  - geavanceerd zoeken (EN/OF, filters, “bevat”)  
  - track-zoek (tracktitel en tracknummer)  
- **Inzicht & ordening**:
  - overzichten per artiest/jaar/genre/type/locatie  
  - duplicatenrapport  
  - exporteerbare lijsten (CSV/PDF later)  
- **Mobiel-first**: volledig kunnen lezen én schrijven op telefoon/tablet.

### 3.2 Succescriteria (meetbaar)

- 90% van toevoegacties kan binnen 60 sec (barcode → match → opslaan) bij beschikbare online data  
- Zoeken levert binnen 500 ms een resultaatset (bij ~5.000 items) op thuisnetwerk  
- Duplicatenrapport vindt ≥ 95% van exacte dubbelingen (zelfde barcode/cataloguscode)  
- Back-up/export + restore werkt zonder dataverlies in een testscenario

---

## 4. Doelgroep & persona’s

### 4.1 Doelgroep

- Particulieren met een grote fysieke media-collectie (CD’s, Blu‑ray audio, DVD, etc. – in v1 minimaal CD + Blu‑ray als type).

### 4.2 Persona’s

- **De Verzamelaar**  
  - wil volledigheid, editions, covers, notities, duplicaatcontrole  
- **De Zoeker**  
  - wil vooral “heb ik dit?” en “waar ligt het?” en “waar staat die track?”  
- **De Opruimer**  
  - wil ordenen, lijstjes printen/exporteren, en makkelijker opruimen/labelen

---

## 5. Scope & non-scope

### 5.1 In scope v1

**Data-objecten**
- **Release (CD/media-item)** met metadata:
  - Titel  
  - Artiest(en) (meerdere)  
  - Tracklist (tracknummer, titel; optioneel duur)  
  - Jaar (releasejaar; optioneel aankoopjaar)  
  - Codes: UPC/EAN, catalogusnummer, SPARS  
  - Genre(s) (optioneel v1 maar gewenst)  
  - Type: CD / Blu‑ray (uitbreidbaar)  
  - Notitie (vrij veld)  
  - Fysieke locatie (zie 5.1.3)  
  - Covers (min. front; opt. back/inside)

**5.1.1 Covers**
- JPG/PNG, met maximale resolutie en bestandsgrootte (config)  
- Bestanden op disk (niet in DB), DB bewaart paden + checksum  
- Automatische thumbnail-generatie (voor performance)

**5.1.2 Invoer (add)**
- Handmatig toevoegen (form)  
- Barcode scan op mobiel (PWA-camera) → lookup  
- Lookup-resultaten tonen als lijst → gebruiker kiest juiste match → import metadata + covers  
- Altijd mogelijkheid om data te corrigeren vóór opslaan  
- Duplicaatwaarschuwing (barcode/cataloguscode)

**5.1.3 Fysieke locatie (vindbaarheid)**
- Locatiemodel (simpel maar krachtig):
  - Opslagtype: Kast / Box / Krat / Anders  
  - Locatienaam (bijv. “Kast woonkamer”)  
  - Sectie/Rij/Plank (vrij)  
  - Positie (nummer)  
- Rapportage om per locatie te sorteren en eventueel labels te maken (v2)

**5.1.4 Zoeken**
- Snelzoeken (1 veld) over titel, artiest, track, code, notitie  
- Geavanceerd zoeken:
  - filters (jaar, type, genre, locatie)  
  - EN/OF logica  
  - “bevat” (LIKE) + exacte match  
- Sorteren en pagineren

**5.1.5 Rapportage & inzichten**
- Overzichtsschermen:
  - totalen (aantal releases, aantal artiesten, per type)  
  - per artiest / per jaar / per genre / per locatie  
  - duplicaten (exact + “mogelijk”)  
- Export/back-up (zie 5.1.6)

**5.1.6 Export / back-up / restore**
- Eén “export bundle” (ZIP) met:
  - database dump (bijv. SQLite file of JSON + schema versie)  
  - covers + thumbnails  
  - manifest.json met versie, datum, checksums  
- Import/restore met validatie en migratiepad (schema versie)

**5.1.7 PWA**
- Installable PWA, offline lezen mogelijk (cache)  
- Schrijven alleen binnen thuisnetwerk (v1)  
- “Snapshot sync”: periodiek een read-only snapshot naar device voor offline zoeken (optioneel)

### 5.2 Niet in scope v1 (kandidaat v2+)

- Audio rippen, afspelen of streaming  
- Multi-user rollen/permissions uitgebreid (alleen basic auth in v1)  
- Automatische herkenning via audio fingerprinting  
- Offline-first/PWA functionaliteit  
- Geavanceerde label/print workflows (PDF labels)  
- Volledig editten van track-duren, credits, matrix/runout (kan later)

---

## 6. Feature-set & prioritering

### P0 – Must Have (v1)
- CRUD releases + tracklist  
- Barcode invoer + lookup + keuze match + import  
- Duplicaatdetectie (exact)  
- Snelzoeken + geavanceerd zoeken (EN/OF, bevat)  
- Locatievelden + sorteerbare lijsten  
- Export/restore bundle (ZIP)  
- Responsive mobile-first UI (werkt goed op telefoon/tablet)  
- Deployment: LAN-first + externe toegang via reverse proxy (Nginx)

### P1 – Should Have (kort na v1)
- “Mogelijke duplicaten” (fuzzy op titel/artist/jaar)  
- Bulk acties (meerdere items tegelijk locatie wijzigen)  
- Thumbnail/caching optimalisaties  
- CSV-export van lijst/rapport  
- Audit log (wie/wat/wanneer) – ook nuttig voor “undo”

### P2 – Nice to Have / v2+
- Labels/QR-codes printen voor dozen/kasten  
- Slimme “orde-advies” (bijv. alfabetisch per artiest, of per genre)  
- Edition management (meerdere versies van dezelfde release)  
- Integratie met externe bronnen (meerdere providers) + mapping UI  
- Voice search (mobiel)
- Authenticatie & accounts (Google OAuth als IDP) + basis autorisatie

---

## 7. User stories (met acceptatiecriteria)

### 7.1 Beheer
1. **Als gebruiker wil ik een CD handmatig kunnen toevoegen**  
   - AC: formulier valideert verplichte velden; opslaan toont detailpagina

2. **Als gebruiker wil ik een CD via barcode kunnen toevoegen**  
   - AC: scan → resultatenlijst → keuze → conceptdetail → opslaan  
   - AC: bij bestaande barcode waarschuwing + optie “toch toevoegen”

3. **Als gebruiker wil ik een CD kunnen archiveren/verwijderen**  
   - AC: item verdwijnt uit standaardlijst, blijft terugvindbaar in “Archief”

### 7.2 Zoeken
4. **Als gebruiker wil ik snel kunnen zoeken op titel/artist/track/code**  
   - AC: resultaten binnen 500 ms (thuisnetwerk) bij 5.000 items

5. **Als gebruiker wil ik geavanceerd kunnen filteren**  
   - AC: filters combineren; EN/OF werkt zichtbaar en voorspelbaar

### 7.3 Organiseren
6. **Als gebruiker wil ik fysieke locaties beheren**  
   - AC: locatielijst; items toewijzen; lijst per locatie sorteerbaar

### 7.4 Back-up en inlezen
7. **Als gebruiker wil ik een export kunnen maken en later herstellen**  
   - AC: export bundle bevat DB + covers; restore levert identieke collectie

---

## 8. UX & UI richtlijnen

### 8.1 Principes
- Mobile-first, snelle interactie (grote knoppen, korte formulieren)  
- “Progressive disclosure”: standaard simpel, advanced optioneel  
- Fouten voorkomen: suggesties, auto-complete, duplicaatwaarschuwingen  
- Altijd “bewerken” vanaf detailpagina

### 8.2 Kernschermen (v1)
- Dashboard (totalen + snelle acties)  
- Lijst (filter/sort/search)  
- Detail (cover, metadata, tracks, locatie)  
- Add flow (scan/handmatig)  
- Rapporten (duplicaten, per locatie, etc.)  
- Instellingen (lookup provider(s), export)
  - (v2) Inloggen/auth (Google OAuth)

### 8.3 Taal & toegankelijkheid
- Nederlands, kort en duidelijk, geen vakjargon  
- Toegankelijkheid:
  - voldoende contrast  
  - grote tap-targets  
  - labels + foutmeldingen die uitleggen *wat* en *hoe op te lossen*

---

## 9. Technische requirements

### 9.1 Architectuur & stack (voorgesteld)
- **Server (thuisserver)**
  - Python + uv + .env  
  - FastAPI  
  - SQLModel (SQLite)  
  - Migratie-tooling (Alembic of alternatief)  
  - **SQLite FTS5** voor full-text search (sterk aanbevolen)  
  - Bestandsopslag voor covers + thumbnails  
    - (v2) Authenticatie via Google OAuth (IDP). In v1 alvast rekening houden met: gebruikers-/sessiemodel, auth-middleware, en scopes/roles (al is er maar 1 gebruiker).

- **Frontend (web/PWA)**
  - Modern framework: React of Vue  
  - PWA: service worker + offline cache  
  - Camera/barcode: Web APIs (waar beschikbaar)

### 9.2 Datamodel (globaal)
- Release(id, title, year, type, upc_ean, catalog_no, spars, notes, created_at, updated_at, archived_at)  
- Artist(id, name)  
- ReleaseArtist(release_id, artist_id, role/order)  
- Track(id, release_id, track_no, title, duration?)  
- Location(id, storage_type, name, section, shelf, position)  
- Cover(id, release_id, kind(front/back/inside), path, checksum, width, height, bytes)

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

### 9.4 Security & deployment
- Docker-container op thuisserver  
- Intern toegankelijk binnen LAN  
- Extern toegankelijk via reverse proxy (Nginx)  
- HTTPS via reverse proxy (bijv. Let’s Encrypt) aanbevolen  
- Back-ups lokaal; geen cloud afhankelijkheid  
- Logging met minimale privacy-impact (geen gevoelige data)

---

## 10. Rapportage, logging & observability

### 10.1 Rapportage (v1)
- Duplicaten (exact + later fuzzy)  
- Per artiest / per jaar / per type / per locatie  
- Export CSV (P1) / PDF (P2)

### 10.2 Logging
- API errors, DB errors, lookup errors  
- Export/import acties (wie/wanneer + resultaat)  
- Optioneel audit log voor mutaties

---

## 11. Risico’s, aannames & afhankelijkheden

### 11.1 Risico’s
- Online lookup bronnen veranderen of limiteren (rate limits, API keys)  
- Barcode scan werkt niet op alle devices/browsers even goed  
- Duplicaten zijn soms “bijna gelijk” (fuzzy matching vereist)  
- Cover-opslag kan veel ruimte innemen → thumbnails + limieten nodig

### 11.2 Aannames
- Thuisserver is betrouwbaar en draait 24/7 of vaak genoeg  
- Gebruiker zit meestal op hetzelfde netwerk als server  
- Moderne browser beschikbaar op mobiel/tablet

### 11.3 Afhankelijkheden
- Browser support voor PWA + camera API’s  
- Eventuele externe data providers (optioneel)

---

## 12. Roadmap & fasering (suggestie)

### Fase 1 – Basis (v1)
- Datamodel + CRUD + locaties  
- Snelzoeken + FTS  
- Handmatig toevoegen + basis UI (mobile-first)  
- Export/restore  
- Deployment: LAN-first + Nginx reverse proxy voor externe toegang

### Fase 2 – Invoer versnellen
- Barcode scan + lookup + import covers  
- Duplicaatdetectie  
- Rapporten (duplicaten, per locatie)  
- Performance tuning

### Fase 3 – v2 ideeën
- Authenticatie (Google OAuth als IDP) + basis autorisatie  
- Labels/QR print  
- Fuzzy duplicates + edition management  
- Bulk actions + CSV/PDF exports
