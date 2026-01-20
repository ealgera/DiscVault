# Design: Wishlist & Statistics

## 1. Doelstelling
Het toevoegen van functionaliteit om onderscheid te maken tussen albums in bezit en gewenste albums (Wishlist), en het bieden van visuele inzichten in de collectie via statistieken.

## 2. Wishlist (Verlanglijst)

### Datamodel
*   **Nieuw veld**: `status` op `Album` model.
    *   Type: `String` (Enum)
    *   Opties: `'collection'` (default), `'wishlist'`.
    *   *Toekomstbestendig*: Kan later uitgebreid worden met `'sold'`, `'loaned'`, etc.
*   **Validatie**: `location_id` mag `NULL` zijn voor items op de wishlist (fysiek nog niet aanwezig).

### Backend Changes
*   `Album` model update (`models.py`).
*   Migratie (alembic) of automatische schema update via SQLModel.
*   Update `GET /albums`: Ondersteuning voor filteren op `status`.
*   Update `POST /albums`: Mogelijkheid om status mee te geven (default `collection`).
*   Update `PUT /albums`: Status wijzigen (bijv. van Wishlist naar Collection).

### Frontend Changes

#### Collectie Overzicht (`CollectionView`)
*   **Tabs / Toggle**: Bovenaan switchen tussen "Mijn Collectie" en "Wishlist".
*   **Visueel**: Wishlist items krijgen een duidelijke markering (bijv. andere kaartstijl of badge).
*   **Acties**:
    *   Op de Wishlist: Knop "Toevoegen aan Collectie" -> opent modal/scherm om locatie en datum toe te voegen.

#### Scanner & Manual Entry (`ScanView`)
*   **Standaard Status**: Staat standaard op "Collectie" (want scannen = hebben).
*   **Keuze**: Radio buttons of toggle: "Aan Collectie toevoegen" vs "Op Wishlist zetten".
*   **Velden**: Bij keuze "Wishlist" wordt het veld `Locatie` verborgen.
*   **Nullability**: Voor Wishlist items mogen `Jaar`, `Catalogus #` en `Barcode` leeg blijven (worden niet verplicht).

#### Wishlist Matching & Conversie
*   **Scenario**: Gebruiker scant/voert album in voor Collectie dat al op Wishlist staat.
*   **Matching Logica**:
    *   Check of item op Wishlist staat op basis van **Titel** én **Artiest** (ongeacht barcode/jaar/cat#).
    *   Dit omdat de wishlist-versie vaak minder details heeft dan de fysieke versie die je later koopt.
*   **Actie**:
    *   Melding aan gebruiker: "Dit album stond op je Wishlist en is nu verplaatst naar je Collectie!".
    *   De *bestaande* wishlist entry wordt geüpdatet naar status `'collection'` (zodat datum en notities behouden blijven) OF de wishlist entry wordt verwijderd en de nieuwe scan wordt opgeslagen (schonere data).
    *   *Keuze*: Verwijder wishlist item en maak nieuwe aan (zodat barcode/jaar correct zijn van de scan).

## 3. Statistieken (Statistics)

### Backend Changes
*   Nieuw endpoint `GET /reports/distribution/{type}` (type: 'genre', 'tag').
    *   Geeft data terug: `[{ name: 'Rock', count: 45, percentage: 30 }, ...]`.
    *   Alleen tellen voor albums met status `'collection'`.

### Frontend Changes
*   **Nieuwe View**: `StatisticsView.vue` (route `/statistics`).
*   **Bereikbaarheid**: Via het "Rapporten" dashboard (extra tegel: "Bekijk Statistieken").
*   **Visualisatie**:
    *   Gebruik van eenvoudige, stijlvolle CSS-gebaseerde "Progress Bars" of "Donut Charts" (geen zware library nodig voor simpele distributies).
    *   **Genre Verdeling**: Top 10 genres met balken.
    *   **Tag Verdeling**: Top 10 tags.
    *   Responsive layout.

## 4. Implementatie Stappenplan
1.  **Backend**: Model aanpassen (`status` veld), DB migratie, endpoints updaten.
2.  **Frontend - Wishlist**:
    *   `CollectionView` filters en tabs.
    *   `AlbumDetail` aanpassen (status tonen/wijzigen).
    *   `ScanView` aanpassen (keuze wishlist/collectie).
3.  **Frontend - Statistieken**:
    *   Nieuwe `StatisticsView` bouwen.
    *   Koppelen aan Dashboard.

## 5. Vragen / Keuzes
*   **Locatie**: Voor wishlist items is locatie waarschijnlijk niet relevant. Zullen we dit veld verbergen bij het aanmaken van een wishlist item? (Ja, lijkt logisch).
*   **Datum**: `created_at` wordt de datum van op wishlist zetten. Willen we een `acquired_at` datum toevoegen voor het moment van in collectie komen? (Voor nu: *Nee*, `created_at` is datum van invoer systeem, dat is prima. Bij omzetten naar collectie blijft dit behouden of updaten we `updated_at`).

