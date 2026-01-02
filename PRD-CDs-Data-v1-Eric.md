```markdown
# Product Requirements Document – CD's database

**Projectnaam**: CD's database  
**Versie**: 1.0 (concept)  
**Datum**: 03-01-2026  
**Auteur**: Eric Algera  
**Status**: Concept – v1 (Snapshot sync + PWA + Rationering)

---

## 1. Executive Summary

**Wat is CD's database?**  
Noodpakket is een intelligente applicatie voor het beheren van fysieke CD's, een CD management applicatie. De toepassing draait primair op een thuisserver in een Docker container.  

Gebruikers kunnen:

- CD's opvragen, toevoegen, wijzigen en verwijderen;  
- Karakteristieken of metagegevens van een CD opslaan bij de CD;
- CD's zoeken op basis van allerlei criteria zoals naam CD, Artiest, Track, datum, enzovoort. Ook op combinaties van criteria. Zowel met een EN als een OR functie;
- CD's gemakkelijk invoeren op basis van een code of iets dergelijks waarbij de CD-gegevens online worden gehaald en lokaal kunnen worden bewaard;
- Op basis van de gegevens CDS's rangschikken op Artiest en CD-naam of andere rangschikkingen;

**Voor wie?**  
Voor personen met een uitgebreide CD verzameling die orde in deze verzameling willen brengen en er beheer op kunnen uitvoeren.

**Waarom bouwen we dit?**  
We bouwen dit om inzicht te verschaffen in de verzameling, om:

- CD's te kunnen zoeken;
- CD's fysiek te kunnen rangschikken;

---

## 2. Probleemstelling

**Huidige situatie:**

- Op, dit moment weten we niet precies:
  - welke CD's we hebben,
  - of we dubbelingen hebben,
  - waar een CD precies staat (fysiek te vinden is),
  - welke versie we van een CD hebben,
  - op welke CD een bepaalde track staat.
  
**Kans:**

Een interactieve applicatie die:

- ...;

---

## 3. Doelstellingen & Goals

### 3.1 Functionele doelen

- CD's inbrengen en beheren:
  - gemakkelijke invoer van een CD, op basis van CD-code of iets dergelijks in combinatie met online zoek mogelijkheid,  
  - CD-gegevenn aanpasbaar, ook meta-gegevens,  
  - CD's te verwijderen naar een historie.
- Volledig beeld van alle CD's:
  - welke zijn er,
  - hoeveel zijn er,
  - hoeveel per gegeven, bijvoorbeeld hoeveel per Artiest of per Genre of per Jaar, enzovoort,
  - waar zijn ze fysiek opgeslagen,
- Uitgebreide zoekmogelijkheden. Op Titel, Artiest, Track, Jaar, enzovoort. Ook op combinaties daarvan en met EN of OF functies en een LIKE zoekmogelijkheid.
- Full capability op telefoon/tablet:
  - volledig en goed kunnen werken (lezen én schrijven) op kleinere apparaten dan een beeldscherm.

### 3.2 Gebruikersdoelen (voorbeelen)

- "Ik wil weten of ik de CD "The Mirror Pool" van "Lisa Gerrard" heb. 
- “Ik wil weten waar de CD "The Mirror Pool" van "Lisa Gerrard" staat, fysiek, waar ik die kan vinden.  
- “Ik wil weten welke CD's ik dubbel of meervoudig heb.”  
- “Ik wil weten op welke CD of CD's de track 'Swan' staat.”
- "Ik wil weten of ik een CD heb met 'Pool' in de naam van de titel."

---

## 4. Doelgroep & Persona’s

### 4.1 Doelgroep

- Een persoon met een grote hoeveelheid CD's.

### 4.2 Persona’s

- **Persona A – De CD eigenaar**  
  - Wil overzicht en gemakkelijke beheerfuncties.  

- **Persona B – De Gebruiker**  
  - Wil gemakkelijk kunnen zoeken naar CD's
  - wil een gezochte CD gemakkelijk kunnen vinden, fysiek.

---

## 5. Scope & Non-scope

### 5.1 In scope v1

- Eén database met alle CD's.  
- CD's worden opgeslagen met allerlei metadata zoals:
  - Covers
    - minimaal 1: front cover,
    - eventueel back cover en inner covers,
    - in JPG of PNG formaat,
    - gebonden aan een maximale grootte (--> uitzoeken)
    - covers worden apart bewaard, niet in de database
  - Titel,
  - Artiest(naam),
    - Ook meerdere Artiestname,
  - Tracknummer en Tracktitel,
  - Jaar,
  - CD code,
  - Opmerking, vrij invulbaar,
  - Aankoopdatum (als beschikbaar),
  - SPARS code,
  - overige metadata --> uitrzoeken
- Gemakkelijke invoer van CD's
  - door bijvoorbeeld gebruik te maken van het UPC/EAN nummer van de CD en online zoeken
  - van de online gevonden CD's moet er 1 uitgekozen kunnen worden
  - van de gekozen CD moeten covers en metadata worden ingelezen in de applicatie
- Uitgebreide zoekmogelijkheden
  - op alle metadata,
  - op combinaties van metadata,
    - zowel met EN- als een OR-functie.
  - met een LIKE zoekmogelijkheid
- Rapportage mogelijkheden
  - Lijsten van CD's,
    - diverse sorteringen
      - voorbeelden: per Artiest, per Jaar, per SPARSE-code, per fysieke plaats, enzovoort
- Blu-Ray is een specifiek type CD
  - Dit soort types moet kunnen worden:
    - bewaard bij de CD,
    - op gezocht kunnen worden
- Export en back-up mogelijkheden
  - De database en covers moeten gemakkelijk geexporteerd kunnen worden
  - in een formaat wat ook weer gemakkelijk kan worden ingelezen

### 5.2 Niet in scope v1 (mogelijk v2+)

- --> Uitzoeken

---

## 6. Belangrijkste Features & Prioritering

### 6.1 Feature-overzicht met prioriteit

**P0 – Must Have (v1)**

- Alle geschetste functionaliteit in sectie 5.1, Scope  

**P1 – Should Have (na v1, maar gewenst)**

- --> uitzoeken

**P2 – Nice to Have / v2+**

- --> uitzoeken
---

## 7. User Stories (kern)

### 7.1 Beheer

### 7.2 Zoeken

### 7.3 Organiseren
Als gebruiker wil ik mijn CD verzameling kunnen organiseren en zodanig fysiek neerzetten dat CD's gemakkelijk terug te vinden zijn. 

### 7.4 Backup en inlezen

---

## 8. UX & UI Richtlijnen

### 8.1 Algemene principes

### 8.2 Specifiek

### 8.3 Taal & toegankelijkheid

- Taal: Nederlands, kort en duidelijk, geen vakjargon.  
- Toegankelijkheid:
  - voldoende contrast,
  - grote tap-targets,
  - duidelijke labels.

---

## 9. Technische Requirements

### 9.1 Architectuur & stack

- **Server (thuisserver)**  
  - Taal: Python  
  - Environement: uv en .env
  - Framework: FastAPI  
  - Datamodellen: Pydantic  
  - Datamodellering: SQLModel   
  - AI en AI agents: Pydantic-AI   
  - AI model: Gemini   
  - Database: SQLite (bron van waarheid op server)

- **Frontend (web)**  
  - HTML/CSS/JavaScript  
  - Aanbevolen: modern framework (React of Vue)  

### 9.2 Data & modellen (globaal)

- --> uitzoeken

### 9.4 Security & Deployment

- Server:
  - in een Docker-container op thuisserver.  
  - Toegang alleen binnen thuisnetwerk, optioneel met OAuth-auth via Google.  
  - HTTPS aanbevolen (desnoods zelf-gesigned).

- Privacy:
  - Geen gevoelige persoonsgegevens;.  
  - Geen cloud-dependency; alles lokaal.

---

## 10. Rapportage & Logging

### 10.1 Rapportage

- --> uitzoeken

### 10.2 Logging

- Server:
  - logt fouten in API/database,
  - logt snapshot-export/import-acties.  

---

## 11. Risico’s, Aannames & Afhankelijkheden

### 11.1 Risico’s

- --> uitzoeken

### 11.2 Aannames

- --> uitzoeken

### 11.3 Afhankelijkheden

- Beschikbaarheid van een moderne browser op mobiel/tablet.  
- Beschikbaarheid van Python/FastAPI/SQLModel/AI-omgeving op thuisserver.

---

## 12. Roadmap & Fasering

### Fase 1 

- --> uitzoeken

### Fase 2 
- --> uitzoeken

.   
.   
.   

### Fase N 
- --> uitzoeken

