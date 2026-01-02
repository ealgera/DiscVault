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


* **Invoer:**
* Zoeken op Barcode/Titel via externe API (MusicBrainz).
* Handmatige correctie en aanvulling (inclusief tags toevoegen tijdens import).


* **Zoeken:**
* Filteren op Artiest, Jaar, **Tags** en Locatie.
* Combinaties (AND/OR).
* AI-ondersteund zoeken ("Zoek albums die lijken op...").


* **Techniek:**
* Webinterface geoptimaliseerd voor mobiel (Mobile First).
* Docker container voor eenvoudige hosting.



### 5.2 Niet in scope v1

* Complex gebruikersbeheer (single user is de standaard).
* Offline-sync (applicatie gaat uit van verbinding met thuisserver).
* Streaming van audio.

---

## 6. Belangrijkste Features & Prioritering

### 6.1 Feature-overzicht (MoSCoW)

**P0 – Must Have (De basis)**

* **CRUD Functionaliteit:** CD's aanmaken, lezen, updaten, verwijderen.
* **Tagging Systeem:** Het kunnen aanmaken, toewijzen en verwijderen van tags bij albums.
* **Filteren op Tags:** "Toon alle CD's met tag X".
* **MusicBrainz Integratie:** Ophalen metadata.
* **Mobile Responsive Design:** Goed werkend op smartphone (iOS/Android browsers).
* **Locatie Beheer:** Veld om fysieke plek aan te duiden.

**P1 – Should Have**

* **Barcode Scanner:** Via camera in de browser (html5-qrcode).
* **AI Search:** "Natural language" queries via Gemini.
* **Batch Tagging:** Meerdere CD's selecteren en in één keer een tag geven.

**P2 – Nice to Have**

* Export naar PDF/CSV.
* Dark Mode.
* Willekeurige album suggestie ("Shuffle").

---

## 7. User Stories (Aangevuld)

### 7.1 Beheer

* "Als gebruiker wil ik tijdens het toevoegen van een CD direct de tag 'Nieuw gekocht' kunnen toevoegen."
* "Als gebruiker wil ik een lijst van mijn eigen tags beheren (bijv. typfouten in tags corrigeren)."

### 7.2 Zoeken

* "Als gebruiker wil ik zoeken op alle CD's die de tag 'Instrumentaal' hebben EN uit het jaar '1995' komen."

### 7.3 Organiseren

* "Als gebruiker wil ik mijn CD verzameling kunnen organiseren op locatie, zodat ik weet wat er in 'Doos 3' zit."

---

## 8. UX & UI Richtlijnen

### 8.1 Algemeen

* **Mobile First:** Ontwerp begint bij het mobiele scherm. Desktop is een afgeleide.
* **Tag Visualisatie:** Tags moeten duidelijk zichtbaar zijn als 'chips' of labels bij een album (bijv. gekleurde badgdes).

### 8.2 Taal

* Nederlands.
* Duidelijke terminologie (Gebruik "Tag" of "Label", kies er één en wees consistent).

---

## 9. Technische Requirements

### 9.1 Architectuur & stack

* **Server (Backend):**
* Python / FastAPI / SQLModel (SQLite).
* AI: Pydantic-AI + Google Gemini.


* **Frontend:**
* HTML/JS (Vue of React aanbevolen).
* Framework: Tailwind CSS (voor eenvoudige mobile-first styling).
* Geen harde PWA-eis, maar wel responsive.



### 9.2 Data & modellen

* **Tabellen (Conceptueel):**
* `Album`
* `Artist`
* `Track`
* `Tag` (Naam, Kleur)
* `AlbumTagLink` (Koppeltabel voor Many-to-Many relatie tussen Album en Tag).



### 9.4 Security & Deployment

* Docker container.
* Toegang via Reverse Proxy (bijv. Traefik of Nginx Proxy Manager) op het thuisnetwerk.

---

## 10. Rapportage & Logging

* Loggen van import-acties.
* Foutmeldingen bij mislukte API calls (MusicBrainz).

---

## 11. Risico’s & Aannames

* **Aanname:** De gebruiker zorgt zelf voor toegang tot de server van buitenaf (via VPN of Proxy) als dat gewenst is.
* **Risico:** Wildgroei aan tags. *Mitigatie: Autocomplete voorstellen bij het intypen van tags.*

---

## 12. Roadmap

### Fase 1 (MVP)

* Opzet Database & Backend.
* Implementatie Tagging systeem (Backend + Frontend).
* Basis UI voor mobiel.
* Connectie MusicBrainz.

### Fase 2

* Barcode scanner integratie.
* AI functionaliteiten (Slim zoeken).

---

