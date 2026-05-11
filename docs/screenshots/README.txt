Screenshots Guide - Football Match Center v1.0.0
================================================

This directory should contain representative screenshots of the app for:
- GitHub README.md
- Portfolio presentations
- Release marketing
- Documentation

RECOMMENDED SCREENSHOTS
======================

1. MAIN_SCREEN.png (Bulletin View)
   ==================================
   - Shows: Match list with live scores
   - League: Premier League / La Liga (variety)
   - Include: 4-5 matches showing scores, teams, date/time
   - Purpose: Hero image for main README
   - Dimensions: 1920x1080 minimum
   - Key elements:
     * Match cards showing home/away teams
     * Live scores prominently displayed
     * League names visible
     * "Live" indicator showing data source
   - Tips: Show actual data, not test/demo teams


2. MATCH_DETAIL_HEADER.png (Score & Info)
   ======================================
   - Shows: Match detail screen header
   - Include: Large score display, team names, match date
   - Purpose: Show primary detail view
   - Dimensions: 1366x768 minimum
   - Key elements:
     * Home team name and score on left
     * Away team name and score on right
     * Match date/time/venue below
     * League name and match status
   - Tips: Choose a finished match for clear scores


3. STATS_TAB.png (Game Statistics)
   ============================
   - Shows: Stats tab with possession, shots, etc.
   - Include: Side-by-side team statistics
   - Purpose: Demonstrate data visualization
   - Dimensions: 1366x768 minimum
   - Key elements:
     * Possession percentage
     * Shots and shots on target
     * Corners and fouls
     * Yellow/red cards
     * Comparison bars or percentages
   - Tips: Include teams with significant stat differences


4. TIMELINE_TAB.png (Match Events)
   ==========================
   - Shows: Timeline/events tab with goal and card records
   - Include: At least 3-4 events (goals, cards)
   - Purpose: Show chronological event tracking
   - Dimensions: 1366x768 minimum
   - Key elements:
     * Event minute/timestamp
     * Event type (Goal, Card, Substitution)
     * Player name
     * Team identification
   - Tips: Choose match with multiple events for visual interest


5. LINEUPS_TAB.png (Team Formation)
   ============================
   - Shows: Lineups tab with formation and players
   - Include: Formation (4-3-3, 3-5-2, etc.) and player list
   - Purpose: Demonstrate comprehensive team data
   - Dimensions: 1366x768 minimum
   - Key elements:
     * Team formation display
     * Starting XI with positions
     * Player numbers
     * Player names
   - Tips: Choose different formations for visual variety


6. LANGUAGE_SWITCH.png (Turkish View)
   ==============================
   - Shows: Same app in Turkish (TR) instead of English
   - Include: All Turkish text, same match as main screen
   - Purpose: Demonstrate localization feature
   - Dimensions: 1920x1080 minimum
   - Key elements:
     * Turkish UI text
     * Tab names in Turkish (Bulten, Favori, Ayarlar)
     * Detail tab names (Genel, Sut ve Oyun, Olaylar, Kadro, H2H, Oranlar)
     * Same underlying data as English version
   - Tips: Shows same match as English version for direct comparison


7. RESPONSIVE_LAYOUT.png (Multiple Sizes)
   ====================================
   - Shows: App at different resolutions
   - Include: 1366x768, 1920x1080 side-by-side (or stacked)
   - Purpose: Demonstrate responsive design
   - Dimensions: 2560x1080+ (combining views)
   - Key elements:
     * UI properly scaled at both resolutions
     * No text cutoff or overflow
     * Readable font sizes
     * Touch targets are appropriate
   - Tips: Use DevTools device toolbar to capture different sizes


8. FAVORITES_TAB.png (User Favorites)
   =========================
   - Shows: Favorites tab with bookmarked matches
   - Include: 2-3 favorited matches
   - Purpose: Demonstrate user preference feature
   - Dimensions: 1366x768 minimum
   - Key elements:
     * Star icon showing favorited matches
     * Filtered list showing only favorites
     * Same match data as bulletin view
   - Tips: Click star on main view, then show Favorites tab


9. ERROR_STATE.png (Graceful Error Handling) - OPTIONAL
   ====================================================
   - Shows: "Stats not available" or similar friendly message
   - Purpose: Demonstrate error handling (not crashing)
   - Dimensions: 1366x768 minimum
   - Key elements:
     * Friendly error message (not raw HTTP error)
     * Other tabs still functional
     * App remains responsive
   - Tips: Show when stats/lineups truly unavailable (don't fake)


10. SETTINGS_TAB.png (Configuration) - OPTIONAL
    =========================================
    - Shows: Settings screen with language dropdown
    - Purpose: Demonstrate configuration options
    - Dimensions: 1366x768 minimum
    - Key elements:
      * Language selector (TR/EN)
      * Other settings if implemented
      * Clean settings UI
    - Tips: Highlight language dropdown


USAGE GUIDELINES
================

GitHub README:
- Use MAIN_SCREEN.png as hero image
- Include MATCH_DETAIL_HEADER.png
- Show STATS_TAB.png or TIMELINE_TAB.png
- Total: 2-3 screenshots in README

Portfolio/Presentation:
- MAIN_SCREEN.png - "Here's the app"
- MATCH_DETAIL_HEADER.png - "Detail view"
- STATS_TAB.png - "Complex data displayed clearly"
- LINEUPS_TAB.png - "Multiple tabs work independently"
- LANGUAGE_SWITCH.png - "Bilingual support"
- RESPONSIVE_LAYOUT.png - "Works at all sizes"
- Total: 6 images for comprehensive presentation

Marketing/Release Notes:
- MAIN_SCREEN.png - Main image
- MATCH_DETAIL_HEADER.png - Secondary image
- RESPONSIVE_LAYOUT.png - Show device compatibility

FILE NAMING CONVENTION
====================

Use descriptive names with version/date:

✓ MAIN_SCREEN.png
✓ MATCH_DETAIL_HEADER.png
✓ STATS_TAB.png
✓ TIMELINE_TAB.png
✓ LINEUPS_TAB.png
✓ LANGUAGE_SWITCH.png
✓ RESPONSIVE_LAYOUT.png
✓ FAVORITES_TAB.png
✓ ERROR_STATE.png
✓ SETTINGS_TAB.png

SCREENSHOT QUALITY REQUIREMENTS
==============================

Resolution:
- Minimum: 1366x768
- Recommended: 1920x1080
- Maximum: 4K (2560x1440+)
- Format: PNG (lossless) or high-quality JPG

Content:
- Real data (no test/fake data)
- Actual teams and matches
- No system notifications or UI chrome (remove taskbar, address bar)
- Focus on app content only

Editing:
- Optional: Add subtle borders/backgrounds
- Add descriptive captions below if needed
- Resize to consistent dimensions across set
- Consider watermarking for portfolio

CAPTURE TIPS
============

Windows:
- Press PrtScn, paste in Paint/Photoshop
- Or use Snip & Sketch (Win+Shift+S)
- Or use ShareX (free screenshot tool)

Mac:
- Cmd+Shift+4 for region capture
- Cmd+Shift+5 for screenshot tool
- Or use ScreenFlow

WebGL (Browser):
- DevTools F12 → Three dots → Capture screenshot
- Or Browser DevTools → Rendering → Emulation
- Browser "Print to PDF" then screenshot

Unity:
- File → Build Settings → Build for WebGL
- Run locally, then screenshot with browser DevTools

COMPRESSION & STORAGE
====================

Before uploading to GitHub:

PNG Compression:
- Use TinyPNG.com or ImageOptim
- Target: <2 MB per image
- Maintain quality

Git Storage:
- Commit to git: docs/screenshots/
- GitHub displays in README via relative path
- Use markdown: ![Alt text](path/to/image.png)

GitHub README Example:
```markdown
## Screenshots

### Main Screen - Live Match Bulletin
![Match list showing live scores](docs/screenshots/MAIN_SCREEN.png)

### Match Detail - Comprehensive Statistics
![Stats tab with team statistics](docs/screenshots/STATS_TAB.png)
```

CHECKLIST FOR RELEASE
====================

Before releasing v1.0.0:

- [ ] 10 recommended screenshots captured
- [ ] All images at 1920x1080 minimum
- [ ] Real data shown (no test teams)
- [ ] File names descriptive and consistent
- [ ] PNG format, compressed < 2MB each
- [ ] Added to GitHub repo
- [ ] README.md references images
- [ ] Release notes mention screenshots
- [ ] Portfolio presentation has 6+ images
- [ ] Demo script has screenshot references

FUTURE ENHANCEMENTS
===================

Possible additions for V1.1+:

- Animated GIFs showing language switching
- Video demo (YouTube embed)
- Before/after error handling comparison
- Performance metrics visualization
- Architecture diagram screenshots
- Deployment flow screenshots
- Mobile app screenshots (when available)

STORAGE LOCATION
===============

All screenshots should be in:
/backend-service/docs/screenshots/

This directory:
- Is in git repository
- Is displayed in GitHub UI
- Can be referenced from README.md
- Keeps project organization clean

SUPPORT
=======

For screenshot help:
1. See SHORT_DEMO_SCRIPT.md for app navigation
2. See FINAL_PRESENTATION.md for context
3. See README.md for example usage
4. Check architecture.md for technical context

Created: May 11, 2026
Version: 1.0.0
