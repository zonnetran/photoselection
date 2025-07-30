# Photo Selection Website

A locally hosted website for photographers to share galleries with clients for photo selection.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a gallery:**
   ```bash
   python setup_gallery.py client_name optional_password
   ```

3. **Upload photos:**
   - Copy your photos to `static/galleries/client_name/`

4. **Start the server:**
   ```bash
   python app.py
   ```

5. **Access galleries:**
   - Open http://localhost:5000 in your browser

## Features

✅ **Password-protected galleries**
✅ **Photo selection with counter**
✅ **Comments on individual photos**
✅ **Export selections to clipboard**
✅ **Responsive design**
✅ **Local hosting (no internet required)**
✅ **Neo-brutalist design system**
✅ **Multi-language support**

## File Structure

```
project/
├── app.py                 # Main Flask application
├── setup_gallery.py      # Gallery creation script
├── templates/             # HTML templates
│   ├── base.html         # Base template with styling
│   ├── index.html        # Gallery listing page
│   ├── gallery.html      # Photo selection interface
│   └── login.html        # Gallery password entry
├── static/
│   ├── css/
│   │   └── neo-brutalist.css  # Design system styles
│   └── galleries/        # Photo galleries
├── selections/           # Client selections (JSON files)
└── gallery_passwords.json # Gallery passwords
```

## Design System

The website uses a **Neo-Brutalist design system** with:

### Typography
- **Headers**: Bebas Neue font (bold, uppercase styling)
- **Body text**: Roboto Mono (monospace, technical feel)
- **CSS Variable**: `--bs-body-font-family: 'Roboto Mono', monospace`

### Visual Elements
- **Grid background**: Subtle dotted pattern
- **Bold borders**: 3-4px black borders on components
- **Drop shadows**: Offset box shadows for depth
- **High contrast**: Black/white with yellow accents

### Customization
To modify the design system:

1. **Change fonts** in `templates/base.html`:
   ```css
   :root {
       --bs-body-font-family: 'Your Font', monospace;
   }
   ```

2. **Modify grid background** in `static/css/neo-brutalist.css`:
   ```css
   body::before {
       background-size: 40px 40px; /* Grid spacing */
       opacity: 0.1; /* Grid visibility */
   }
   ```

3. **Update component styles**:
   ```css
   .neo-brutalist {
       border: 4px solid #000; /* Border thickness */
       box-shadow: 8px 8px 0 #000; /* Shadow offset */
   }
   ```

## Usage for Photographers

1. **Create gallery**: `python setup_gallery.py wedding_smith password123`
2. **Upload photos** to `static/galleries/wedding_smith/`
3. **Share URL** with client: `http://localhost:5000`
4. **Check selections** in `selections/` folder

## Client Workflow

1. Visit website
2. Select gallery
3. Enter password (if required)
4. Browse and select photos using heart checkboxes
5. Add comments (optional)
6. Submit selection
7. Receive confirmation

## Admin Features

- **Gallery management**: Create/delete galleries
- **Selection review**: View all client selections
- **Export options**: Download selections as JSON
- **Password protection**: Secure gallery access

## Technical Notes

- **Framework**: Flask (Python web framework)
- **Styling**: Bootstrap 5 + Custom Neo-Brutalist CSS
- **Fonts**: Google Fonts (Bebas Neue, Roboto Mono)
- **Translation**: Google Translate integration
- **Responsive**: Mobile-friendly design
- **Local hosting**: No internet required for core functionality

## Troubleshooting

**Grid background not showing:**
- Check `static/css/neo-brutalist.css` is loaded
- Verify `body::before` pseudo-element styles

**Fonts not loading:**
- Ensure Google Fonts CDN is accessible
- Check `--bs-body-font-family` CSS variable

**Gallery access issues:**
- Verify photos are in correct `static/galleries/` subfolder
- Check `gallery_passwords.json` for password entries
