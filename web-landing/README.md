# Sadece Futbol - Landing Page

Professional landing page for the Sadece Futbol live football match center platform.

## Overview

A modern, dark-themed premium sports-tech landing page showcasing the Sadece Futbol platform. Built with vanilla HTML, CSS, and JavaScript - no external dependencies or frameworks.

## Features Showcase

### Design Sections

1. **Navigation Bar**
   - Sticky navigation with smooth scrolling
   - Quick links to all major sections
   - Responsive design

2. **Hero Section**
   - Eye-catching headline and subtitle
   - Animated background elements
   - Call-to-action buttons (Live Demo, API Docs)
   - Split layout with visual elements

3. **Features Section**
   - 6 core platform features with icons:
     - Live Scores
     - Match Statistics
     - Events Timeline
     - Lineups
     - League Filters
     - Multi-language Support

4. **Architecture Section**
   - Technical stack overview:
     - Unity WebGL Frontend
     - FastAPI Backend
     - API-Football Provider
     - Cache-First System

5. **Demo Section**
   - Interactive component showcases:
     - Live Match Score Display
     - Match Statistics Visualization
     - Team Lineup Display
     - Events Timeline

6. **Roadmap Section**
   - Future features (5 items):
     - Mobile App
     - User Accounts
     - Notifications
     - AI Match Analysis
     - Custom Domain

7. **Footer**
   - Repository links
   - API documentation links
   - Quick navigation
   - Copyright information

## Design System

### Color Palette

- **Primary Background**: `#0f1419` (Dark Navy)
- **Secondary Background**: `#1a1f2e` (Slightly lighter navy)
- **Accent Color**: `#00d4ff` (Cyan)
- **Secondary Accent**: `#ffd700` (Gold)
- **Success Color**: `#10b981` (Green)
- **Text Primary**: `#e4e6eb` (Light Gray)
- **Text Muted**: `#b0b3b8` (Medium Gray)

### Typography

- Font Family: System fonts (Apple System, Segoe UI, Roboto, etc.)
- Multiple font sizes for hierarchy
- Font weights: 300 (light), 500 (medium), 600 (semibold), 700-800 (bold)

### Responsive Breakpoints

- Desktop: 1024px and above
- Tablet: 768px - 1023px
- Mobile: Below 768px
- Small Mobile: Below 480px

## Usage

### Opening Locally

1. **Method 1: Direct File Open**
   ```
   Open the web-landing folder
   Right-click on index.html
   Select "Open with" → Choose your browser
   ```

2. **Method 2: VS Code Live Server (Recommended)**
   - Install "Live Server" extension in VS Code
   - Right-click on `index.html`
   - Select "Open with Live Server"
   - Browser will open at `http://127.0.0.1:5500/index.html`

3. **Method 3: Terminal Command**
   ```bash
   cd web-landing
   python -m http.server 8080
   # Then visit http://localhost:8080
   ```

4. **Method 4: Using Node.js http-server**
   ```bash
   npm install -g http-server
   cd web-landing
   http-server
   ```

## File Structure

```
web-landing/
├── index.html      # Main HTML structure and content
├── styles.css      # Complete styling and responsive design
├── README.md       # This file
```

## Features

### Interactivity

- **Smooth Scrolling**: All navigation links use smooth scroll behavior
- **Hover Effects**: Cards and buttons have smooth hover transitions
- **Animations**: 
  - Fade-in animations on scroll for cards
  - Float animations on hero elements
  - Slide animations for hero content
- **Modal Alerts**: CTA buttons trigger placeholder alerts

### Responsive Design

- **Mobile-First Approach**: Base styles work on mobile, enhanced for larger screens
- **Flexible Grid Layouts**: Cards adapt from 3 columns to 1 column on mobile
- **Touch-Friendly**: Larger tap targets on mobile
- **Optimized Images/Content**: Text sizes adjust for readability

### Accessibility

- Semantic HTML structure
- Proper color contrast
- Keyboard navigation support
- Smooth scroll behavior

## Customization

### Updating Deployment URLs

Edit the `CONFIG` object at the top of the `<script>` section in `index.html`:

```javascript
const CONFIG = {
    BACKEND_API: 'https://your-backend-url.com',      // Your backend API
    DOCS_URL: 'https://your-docs-url.com/docs',       // Your API documentation
    WEBGL_URL: 'https://your-webgl-demo-url.com',     // Your Unity WebGL deployment
    GITHUB_URL: 'https://github.com/your-username/your-repo'
};
```

### Changing Colors

Edit the CSS variables in `styles.css`:

```css
:root {
    --color-accent: #00d4ff;        /* Main cyan color */
    --color-accent-gold: #ffd700;   /* Gold accent */
    --color-success: #10b981;       /* Green for roadmap */
    /* ... other variables */
}
```

### Adding Sections

1. Add HTML in `index.html`
2. Add corresponding CSS in `styles.css`
3. Add the element to the intersection observer for animations

### Updating Content

All content can be easily updated by editing the HTML file:
- Headlines in `<h1>`, `<h2>`, `<h3>` tags
- Descriptions in `<p>` tags
- Links in `<a>` tags

## JavaScript Features

The page includes vanilla JavaScript for:

1. **Configuration**
   - `CONFIG` object with deployment URLs
   - Easily update for different environments

2. **Event Handlers**
   - `handleLiveDemo()`: Redirects to WebGL demo URL
   - `handleApiDocs()`: Redirects to API documentation

3. **Smooth Scrolling**
   - Automatic smooth scroll for anchor links
   - Uses native `scrollIntoView()` API

4. **Intersection Observer**
   - Lazy animation triggers for cards
   - Triggers when elements enter viewport
   - Adds `animate-in` class for CSS animations

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Modern mobile browsers

## Deployment

This is a static site that can be deployed to any hosting platform. Three recommended options are provided below.

### Deployment Configuration

The deployment URLs are configured in `index.html` in a `CONFIG` object:

```javascript
const CONFIG = {
    BACKEND_API: 'https://football-match-center.onrender.com',
    DOCS_URL: 'https://football-match-center.onrender.com/docs',
    WEBGL_URL: 'https://YOUR_WEBGL_URL_HERE',
    GITHUB_URL: 'https://github.com/kunveli/football-match-center'
};
```

Update these URLs before deploying to match your actual endpoints.

### Option 1: Netlify (Recommended) ⭐

**Why Netlify?** Free tier, automatic deployments, built-in CDN, easy HTTPS, simple setup.

#### Method 1A: Using Netlify UI

1. Sign up at [netlify.com](https://netlify.com)
2. Click "Add new site" → "Deploy manually"
3. Drag and drop the `web-landing` folder
4. Site deploys immediately at `your-site-name.netlify.app`

#### Method 1B: Using Git Integration (Recommended for CI/CD)

1. Push your code to GitHub
2. Sign in to Netlify
3. Click "New site from Git"
4. Connect your GitHub repository
5. Set build settings:
   - Base directory: `web-landing/`
   - Build command: (leave empty - static site)
   - Publish directory: `web-landing/`
6. Deploy

#### Method 1C: Using Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
cd web-landing
netlify deploy --prod
```

#### Custom Domain on Netlify

1. Go to Site settings → Domain management
2. Click "Add custom domain"
3. Enter your domain name
4. Follow DNS configuration instructions

---

### Option 2: Vercel

**Why Vercel?** Next.js creators, fast edge deployments, great performance.

#### Method 2A: Using Vercel UI

1. Sign up at [vercel.com](https://vercel.com)
2. Click "Add new project"
3. Select your GitHub repository
4. Configure:
   - Root Directory: `web-landing`
   - Framework: "Other" or leave as default
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
5. Deploy

#### Method 2B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd web-landing
vercel --prod
```

#### Custom Domain on Vercel

1. Go to project settings → Domains
2. Click "Add" and enter your domain
3. Configure DNS according to Vercel's instructions

---

### Option 3: GitHub Pages

**Why GitHub Pages?** Free, integrated with GitHub, no third-party account needed.

#### Setup GitHub Pages

1. Push code to GitHub repository
2. Go to repository Settings → Pages
3. Select source: Deploy from a branch
4. Branch: `main` (or your default branch)
5. Folder: `/(root)` if repo is `web-landing`, or `/web-landing` if it's in a subdirectory
6. Click Save

**Note:** GitHub Pages uses `https://username.github.io/repository-name` format

#### Using GitHub Pages with Custom Domain

1. In GitHub Pages settings, add your custom domain
2. Configure your domain's DNS to point to GitHub Pages
3. Enable "Enforce HTTPS" in settings

---

### Environment Setup for Deployment

Before deploying, update these in `index.html`:

1. **Update WebGL URL** (Line ~10)
   ```javascript
   WEBGL_URL: 'https://your-webgl-deployment-url.com'
   ```

2. **Update Open Graph URL** (Line ~35)
   ```html
   <meta property="og:url" content="https://your-landing-page-url.com">
   ```

3. **Uncomment Favicon** (if you have one)
   ```html
   <link rel="icon" type="image/x-icon" href="/favicon.ico">
   ```

### Post-Deployment Checklist

- [ ] Test all links work (GitHub, API Docs, WebGL)
- [ ] Verify responsive design on mobile
- [ ] Check performance with Lighthouse (DevTools)
- [ ] Test smooth scrolling
- [ ] Verify animations work smoothly
- [ ] Check SEO meta tags with social media preview tools
- [ ] Set up custom domain (optional)
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Configure CDN caching headers (optional)
- [ ] Set up monitoring/analytics

### Analytics & Monitoring (Optional)

Add to `index.html` `<head>` for tracking:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Integration with Backend

The configuration object in `index.html` already points to:

- **Backend API**: `https://football-match-center.onrender.com`
- **API Docs**: `https://football-match-center.onrender.com/docs`
- **GitHub**: `https://github.com/kunveli/football-match-center`

These are referenced in the JavaScript functions:
- `handleLiveDemo()`: Redirects to WebGL demo
- `handleApiDocs()`: Redirects to API documentation

## Performance

- No external dependencies
- Minimal CSS (< 15KB)
- No JavaScript frameworks
- Fast page load times
- Optimized animations with GPU acceleration

## Future Enhancements

- ✅ Deployment configuration setup
- ✅ SEO meta tags and Open Graph
- Add actual demo integration / screenshots
- Implement dark/light theme toggle
- Add screenshot/video galleries
- Add testimonials section
- Form submissions (contact/newsletter)
- Integrate with GitHub API for stats display
- Add blog/news section
- Performance monitoring & analytics

## Notes

- This is a static landing page - no backend required for hosting
- All data shown in demo cards is mock/sample data
- Ready for deployment to Netlify, Vercel, or GitHub Pages
- Configuration URLs are in `index.html` CONFIG object
- Works offline (no external CDN dependencies)
- No secrets or API keys exposed in code

## License

Part of the Sadece Futbol project. All rights reserved.

---

**Created**: May 2026  
**Version**: 1.0  
**Status**: Production Ready
