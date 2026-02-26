# 📀 DiscVault

[English](#english) | [Nederlands](#nederlands)

---

<a name="english"></a>
## 🌍 English

**DiscVault** is a modern, high-performance web application designed for CD collectors and music enthusiasts. It allows you to digitize your collection by scanning barcodes, manual entry, or bulk importing for tracks. With a focus on speed, aesthetics, and data ownership, DiscVault is the perfect companion for managing your physical media.

### ✨ Key Features
- **Barcode Scanner**: Quickly add albums using your mobile camera.
- **MusicBrainz Integration**: Automatic fetching of titles, artists, genres, and durations.
- **Bulk Track Import (v2.0.0)**: Paste tracklists in CSV format (`nr, title, duration`) for instant mapping.
- **Mobile-First Design**: A premium, responsive UI that feels like a native app.
- **Backup & Restore**: Easily export your entire collection (including cover art) as a ZIP file.
- **Duplicate Detection**: Smart warnings when adding albums you already own.
- **Multi-Artist & Multi-Disc Support**: Full management of complex releases.

### 🛠️ Tech Stack
- **Backend**: Python (FastAPI, SQLModel, SQLite).
- **Frontend**: Vue.js 3, Vite, Tailwind CSS.
- **Containerization**: Docker & Docker Compose.
- **Database**: SQLite (local and persistent).

### 🚀 Quick Start
You can run DiscVault in two different environments: **Acceptance (Docker)** or **Development (Local)**.

#### Acceptance Environment (Docker)
This is the recommended way to run the application in an environment similar to production. Ensure you have Docker and Docker Compose installed.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/[your-repo]/discvault.git
    cd discvault
    ```

2.  **Start the services**:
    ```bash
    docker-compose up -d
    ```

3.  **Access the app**:
    Open `http://localhost:5173` (Frontend) or `http://localhost:8000/docs` (API Docs).

#### Development Environment (Local)
For local development, you need Node.js and a Python environment managed by `uv`.

1.  **Start the Backend**:
    From the root directory, run the backend using `uv` with hot-reload enabled. We use `--host 0.0.0.0` so it is accessible from your network IP:
    ```bash
    uv run uvicorn backend.app.main:app --host 0.0.0.0 --reload
    ```

2.  **Start the Frontend**:
    Open a new terminal, navigate to the `frontend` directory, install dependencies, and start the development server:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3.  **Access the app**:
    Open `http://localhost:5173` (Frontend) or `http://localhost:8000/docs` (API Docs).

### 📦 Persistent Data
All data is stored in the `./data` directory:
- `discvault.db`: The SQLite database.
- `covers/`: All uploaded or fetched cover art images.

---

<a name="nederlands"></a>
## 🇳🇱 Nederlands

**DiscVault** is een moderne, krachtige webapplicatie ontworpen voor CD-verzamelaars en muziekliefhebbers. Het stelt je in staat om je collectie te digitaliseren via barcodescanning, handmatige invoer of bulk-import van tracks. Met de focus op snelheid, esthetiek en eigenaarschap van data, is DiscVault de perfecte metgezel voor het beheren van je fysieke media.

### ✨ Belangrijkste Functies
- **Barcode Scanner**: Voeg snel albums toe via de camera van je mobiel.
- **MusicBrainz Integratie**: Automatisch ophalen van titels, artiesten, genres en tijdsduur.
- **Bulk Track Import (v2.0.0)**: Plak tracklijsten in CSV-formaat (`nr, titel, duur`) voor directe verwerking.
- **Mobile-First Design**: Een premium, responsieve interface die aanvoelt als een native app.
- **Back-up & Herstel**: Exporteer eenvoudig je volledige collectie (inclusief hoezen) naar een ZIP-bestand.
- **Dubbele Check**: Slimme waarschuwingen bij het toevoegen van albums die je al bezit.
- **Multi-Artist & Multi-Disc Ondersteuning**: Volledig beheer van complexe releases.

### 🛠️ Technologie
- **Backend**: Python (FastAPI, SQLModel, SQLite).
- **Frontend**: Vue.js 3, Vite, Tailwind CSS.
- **Containerisatie**: Docker & Docker Compose.
- **Database**: SQLite (lokaal en persistent).

### 🚀 Snel Starten
Je kunt DiscVault draaien in twee verschillende omgevingen: **Acceptatie (Docker)** of **Ontwikkeling (Lokaal)**.

#### Acceptatieomgeving (Docker)
Dit is de aanbevolen manier om de applicatie te draaien in een productie-achtige omgeving. Zorg dat je Docker en Docker Compose hebt geïnstalleerd.

1.  **Clone de repository**:
    ```bash
    git clone https://github.com/[your-repo]/discvault.git
    cd discvault
    ```

2.  **Start de diensten**:
    ```bash
    docker-compose up -d
    ```

3.  **App openen**:
    Open `http://localhost:5173` (Frontend) of `http://localhost:8000/docs` (API Documentatie).

#### Ontwikkelomgeving (Lokaal)
Voor lokale ontwikkeling heb je Node.js en een Python-omgeving beheerd door `uv` nodig.

1.  **Start de Backend**:
    Vanuit de hoofdmap start je de backend met `uv` met hot-reload ingeschakeld. We gebruiken `--host 0.0.0.0` zodat het API bereikbaar is via je netwerk IP:
    ```bash
    uv run uvicorn backend.app.main:app --host 0.0.0.0 --reload
    ```

2.  **Start de Frontend**:
    Open een nieuwe terminal, ga naar de `frontend`-map, installeer de afhankelijkheden en start de ontwikkelserver:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3.  **App openen**:
    Open `http://localhost:5173` (Frontend) of `http://localhost:8000/docs` (API Documentatie).

### 📦 Permanente Data
Alle data wordt opgeslagen in de `./data` map:
- `discvault.db`: De SQLite database.
- `covers/`: Alle geüploade of opgehaalde albumhoezen.

---

**Developed with ❤️ by the DiscVault Team.**
