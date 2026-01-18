# Design Plan: YouTube Music & Lyrics Integration

**Date**: 2026-01-18
**Topic**: YouTube Music Smart Link & Lyrics Search

## Overview
Enhance the album detail view by providing quick links to external services for listening and discovery, following a "KISS" (Keep It Simple Stupid) approach.

## Proposed Changes

### Frontend: AlbumDetailView.vue

1.  **"Listen on YouTube Music" Button**:
    - **Logic**: A computed property that generates a YouTube Music search URL.
    - **Query Format**: `https://music.youtube.com/search?q=[Artist]+[Album Name]`
    - **Technology**: `encodeURIComponent()` to handle special characters.
    - **Styling**: A primary-style button (dark/red accent) with a 'play_circle' icon.

2.  **"Search Lyrics" Icon (Tracklist)**:
    - **Logic**: A link for each track in the tracklist.
    - **Query Format**: `https://www.google.com/search?q=[Artist]+[Track Name]+lyrics`
    - **Styling**: A subtle icon (e.g., 'lyrics' or 'description') next to the track title.
    - **Target**: Opens in a new tab.

## Implementation Details

```typescript
// Example Logic
const youtubeMusicUrl = computed(() => {
  if (!album.value) return '#';
  const artist = album.value.artists?.[0]?.name || '';
  const query = `${artist} ${album.value.title}`.trim();
  return `https://music.youtube.com/search?q=${encodeURIComponent(query)}`;
});
```

- **Target**: Both links will use `target="_blank"` to open in a new tab.
- **Responsive-ness**: On mobile, the YouTube Music link will trigger the app if installed.

## Success Criteria
- User can click a button and be taken to the correct search result on YouTube Music.
- User can quickly find lyrics via a Google Search link.
- No new backend fields or complex API integrations required.
