# UI Design Specificaties - DiscVault

**Versie:** 1.0
**Datum:** 03-01-2026
**Doel:** Blauwdruk voor de frontend implementatie in Vue.js + Tailwind CSS.

---

## 1. Design System & Stijl

### 1.1 Kleurenpalet (Tailwind Classes)
We gebruiken een schoon, modern en rustig palet zodat de album covers de aandacht krijgen.

*   **Achtergrond:** `bg-gray-50` (lichtgrijs, prettiger dan hard wit)
*   **Surface (Cards/Nav):** `bg-white`
*   **Tekst Primair:** `text-slate-900`
*   **Tekst Secundair:** `text-slate-500`
*   **Primair (Acties):** `bg-indigo-600` (Indigo)
*   **Accenten (Tags):** Divers (Amber, Emerald, Rose, Blue, etc.)
*   **Status:**
    *   Succes: `text-green-600`
    *   Error: `text-red-600`

### 1.2 Typografie
*   Standaard sans-serif (Tailwind default: Inter/System fonts).
*   **Koppen:** Bold / Semi-bold.
*   **Body:** Regular.

### 1.3 Componenten
*   **Card:** `bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden`
*   **Button (Primary):** `bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium active:bg-indigo-700`
*   **Button (Secondary):** `bg-white text-slate-700 border border-gray-300 px-4 py-2 rounded-lg`
*   **Input:** `w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500`

---

## 2. Navigatie Structuur (App Shell)

Omdat het mobile-first is, gebruiken we een **Bottom Navigation Bar** voor de belangrijkste navigatie.

### 2.1 Layout
```
+-----------------------------------+
|  [Header: Page Title / Actions]   |  <-- Sticky Top
+-----------------------------------+
|                                   |
|            CONTENT                |
|           (Scrollable)            |
|                                   |
+-----------------------------------+
|  [Home] [Collectie] [Scan] [Loc]  |  <-- Fixed Bottom
+-----------------------------------+
```

### 2.2 Navigatie Items
1.  **Home (Dashboard):** Overzicht, recente toevoegingen.
2.  **Collectie:** De volledige lijst met zoek/filter functionaliteit.
3.  **Scan (+):** De centrale actieknop. Opvallender vormgegeven (bijv. ronde knop in het midden of highlight).
4.  **Locaties:** Beheer van kasten en dozen.
5.  **Instellingen:** (Optioneel, misschien via icoon in header).

---

## 3. Scherm Specificaties

### 3.1 Dashboard (Home)
**Doel:** Snel toegang tot recente items en statistieken.

*   **Header:** "Welkom, Eric"
*   **Sectie 1: Statistieken (Cards)**
    *   3 kleine blokken naast elkaar: "Totaal Albums", "Totaal Artiesten", "Deze Maand".
*   **Sectie 2: Recent Toegevoegd**
    *   Horizontaal scrollbare lijst (carousel) van de laatste 5 albums (alleen cover + titel).
*   **Sectie 3: Willekeurige Suggestie**
    *   "Weet je nog?" - Eén album uitgelicht om te herontdekken.

### 3.2 Collectie (Lijstweergave)
**Doel:** Vinden van een album.

*   **Header:**
    *   Zoekbalk (`input type="search"`) - "Zoek op titel, artiest, track..."
    *   Filter Icoon (opent een 'drawer' of modal met: Genre, Jaar, Tag filter).
*   **Content:**
    *   **Grid Weergave (Default):** 2 kolommen op mobiel, meerdere op desktop.
        *   *Card:* Cover art (groot), Titel (truncate), Artiest (kleiner), Jaar (badge rechtsboven).
    *   **Lijst Weergave (Toggle optie):** Compacte rijen.
        *   *Row:* Kleine thumbnail, Titel/Artiest tekst, Locatie icoon.
*   **Interactie:** Klik op kaart -> Ga naar Detail Pagina.

### 3.3 Album Detail
**Doel:** Alle info van een album inzien en beheren.

*   **Header:** Terug-knop (<), Bewerk-knop (Potlood), Menu-knop (...) voor verwijderen.
*   **Hero Sectie:**
    *   Achtergrond: Geblurde versie van de cover.
    *   Voorgrond: De cover art scherp in het midden.
*   **Info Sectie:**
    *   **Titel:** Groot (H1).
    *   **Artiest:** Linkbaar (H2).
    *   **Badges:** Jaar, Genre, Type (CD/Vinyl).
    *   **Tags:** Gekleurde 'chips' (bijv. "Favoriet", "Luisteren").
*   **Locatie Blok (Prominent):**
    *   Icoon (Kast/Doos).
    *   Tekst: "Kast Woonkamer - Plank 2".
    *   *Actie:* "Verplaatsen" knop.
*   **Tracklist:**
    *   Genummerde lijst.
    *   Tracktitel en duur.
*   **Notes:**
    *   Tekstblok met eventuele notities.

### 3.4 Toevoegen / Bewerken (Add Flow)
**Doel:** Snel albums invoeren.

*   **Tabbladen bovenin:** [Scan Barcode] | [Handmatig]
*   **Tab 1: Scan**
    *   Camera view (indien technisch mogelijk) of "Upload Foto Barcode".
    *   Input veld voor handmatige barcode invoer (fallback).
    *   Knop: "Zoek Online".
*   **Tab 2: Handmatig (Formulier)**
    *   *Sectie 1: Metadata:* Titel, Artiest, Jaar.
    *   *Sectie 2: Cover:* Upload veld / Drag & Drop.
    *   *Sectie 3: Locatie:* Dropdown (Kies Kast) + Veld (Plank/Positie).
    *   *Sectie 4: Tags:* Multi-select input.

### 3.5 Locatie Beheer
**Doel:** Fysieke opslagplekken beheren.

*   **Lijst:** Lijst van locaties.
    *   Item: Naam (bijv. "Zolderdoos 1"), Type (Doos), Aantal items (badge).
*   **FAB (Floating Action Button):** "+" om nieuwe locatie toe te voegen.

---

## 4. Interactie Flows

### Flow: Een CD toevoegen
1.  Gebruiker klikt op "+" in de navigatiebalk.
2.  Scherm opent op tabblad "Scan".
3.  Gebruiker scant barcode.
4.  Systeem zoekt (via Discogs API - backend).
5.  Systeem toont resultaat: Cover + Titel + Artiest.
6.  Gebruiker bevestigt ("Ja, dit is hem").
7.  Gebruiker komt in het "Edit" scherm om locatie en tags toe te voegen.
8.  Gebruiker klikt "Opslaan".
9.  Terug naar Dashboard / Laatst toegevoegd.

### Flow: Een CD zoeken
1.  Gebruiker klikt op "Collectie".
2.  Gebruiker typt "Dead Can Dance".
3.  Lijst filtert realtime.
4.  Gebruiker klikt op "The Serpent's Egg".
5.  Detailpagina opent.
6.  Gebruiker ziet: "Locatie: Kast Woonkamer".
