# Design Plan: Reporting & Cleanup Dashboard

**Date**: 2026-01-19
**Topic**: Data Quality & Insights Reporting

## Overview
Implement a "Rapporten" (Reporting) feature to give users insight into their collection's data quality and provide tools for cleanup and maintenance. 

**Changes from previous version:**
- Feature moved to its own view (linked from the existing "Rapporten" button on the Dashboard).
- Added "Missing Media" and "Missing Catalog #" to incomplete albums.
- Maintaining "Recent Toegevoegd" on the Dashboard without extra clutter.

## Features

### 1. Dashboard (`ReportsView`)
A grid of summary cards, accessible from the Home screen. Each card shows a statistic and links to a detailed list.

**Categories:**
*   **Metadata Cleanup**
    *   **Unused Genres**: Genres with 0 albums.
    *   **Unused Tags**: Tags with 0 albums.
    *   **Low Usage Genres**: Genres used on ≤ 2 albums.
    *   **Low Usage Tags**: Tags used on ≤ 2 albums.
    *   **Unused Artists**: Artists not linked to any album (Main/Guest).
*   **Incomplete Albums**
    *   **Missing Cover**: Albums without cover art.
    *   **Missing Tracks**: Albums with 0 tracks.
    *   **Missing Year**: Albums with year = 0 or null.
    *   **Missing Location**: Albums not assigned to a location.
    *   **Missing Media**: Albums without media type.
    *   **Missing Catalog #**: Albums without catalog number.

### 2. Detailed Views (`ReportDetailView`)
A dynamic list view depending on the report type selected.

**For Metadata (Genres, Tags, Artists):**
*   **Columns**: Name, Usage Count.
*   **Actions**:
    *   **Delete**: (Trash icon) Permanently remove the item. *Confirmation required.*
    *   **Edit**: (Pencil) Rename/Edit (e.g. to merge typos).

**For Albums:**
*   **Columns**: Title, Artist, Status (e.g. "No Cover").
*   **Actions**:
    *   **View**: Link to `AlbumDetailView` to fix the issue manually.

## Technical Architecture

### Backend
New endpoints in `main.py` (or refactored router):

*   `GET /reports/stats`: Returns counts for all dashboard cards.
    *   `{ "unused_genres": 5, "missing_covers": 12, ... }`
*   `GET /reports/unused_genres`: Returns list of genres with count=0.
*   `GET /reports/low_usage_genres`: Returns list of genres with count between 1 and 2.
*   (Similar patterns for Tags/Artists)
*   `GET /reports/albums_no_cover`: Returns list of albums.
*   (Similar patterns for other album issues)

### Frontend
*   New: `views/ReportsView.vue` (Dashboard Grid)
*   New: `views/ReportDetailView.vue` (Dynamic list for cleanup)
*   Modify: `DashboardView.vue` - Link the "Rapporten" button to `/reports`.
*   Fix: `AlbumDetailView.vue` - Tighten vertical spacing in track list (lyrics icon refinement).

## Mockup Flow
1. User clicks "Rapportage" on Home.
2. user sees dashboard:
   [ 🗑️ 5 Ongebruikte Genres ] [ ⚠️ 12 Albums zonder Cover ] ...
3. User clicks "Ongebruikte Genres".
4. User sees list:
   - "Rock & Rll" (0) [🗑️]
   - "Test Genre" (0) [🗑️]
5. User clicks Trash icon -> Confirm -> Genre deleted -> List refreshes.
