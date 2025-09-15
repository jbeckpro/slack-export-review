# Slack Export to HTML Converter

A comprehensive tool that converts Slack standard export ZIP files into readable, chronologically ordered HTML pages that can be published as static websites.

## Features

- **Complete Message Preservation**: Displays all message content including timestamps, sender names, text, files, images, thumbnails, reactions, edits, thread metadata, bot names, and more
- **Slack Formatting Support**: Converts Slack markdown (*bold*, _italic_, ~strikethrough~, `code`, code blocks, lists, blockquotes)
- **User Mentions**: Resolves `<@U123>` mentions to display names using users.json mapping
- **Link Conversion**: Handles `<http://url|label>` and `<http://url>` patterns
- **Thread Support**: Groups thread replies under parent messages with visual indentation
- **File Handling**: Renders images with `<img>` tags and provides download links for other files
- **Search Functionality**: Client-side search to filter messages by text or username
- **Responsive Design**: Clean, accessible layout that works on desktop and mobile
- **Multiple Output Modes**: Generate separate HTML files per channel or a single combined file

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python export_to_html.py --zip path/to/slack-export.zip --out output_directory
```

### Combined Output (Single HTML File)

```bash
python export_to_html.py --zip path/to/slack-export.zip --out output_directory --combined
```

### Command Line Options

- `--zip`: Path to the Slack export ZIP file (required)
- `--out`: Output directory for HTML files (required)
- `--combined`: Generate a single combined HTML file instead of separate channel files

## Slack Export Structure

This tool expects a standard Slack export with the following structure:

```
slack-export.zip
├── channels.json (optional)
├── users.json
└── channel-name/
    ├── 2023-01-01.json
    ├── 2023-01-02.json
    └── ...
```

### Required Files

- **users.json**: Maps user IDs to display names
- **Channel directories**: Each channel has its own folder containing daily JSON files

### Optional Files

- **channels.json**: Contains channel metadata (names, topics, purposes)
- **Local files**: If the export contains local file copies, they will be copied to the `assets/` directory

## Output Structure

The converter generates the following files:

```
output_directory/
├── index.html (channel overview with links)
├── channel-name.html (individual channel pages)
├── combined.html (single file with all channels, if --combined used)
├── assets/ (copied files from export)
└── static/
    ├── style.css
    └── script.js
```

## Features in Detail

### Message Processing

- **Chronological ordering**: Messages sorted by timestamp across all days
- **Complete metadata**: Shows timestamps (human-readable + raw), user info, subtypes, edit status
- **Thread grouping**: Reply messages grouped under parent with reply counts
- **Reactions**: Displays emoji reactions with counts and user tooltips

### Text Formatting

- **Slack markdown**: `*bold*`, `_italic_`, `~strikethrough~`, `` `code` ``, code blocks
- **User mentions**: `<@U123>` converted to `@DisplayName`
- **Links**: `<http://example.com|Label>` and `<http://example.com>` patterns
- **Emoji**: Common emoji shortcodes converted to Unicode symbols
- **Blockquotes**: Lines starting with `>` rendered as blockquotes

### File Handling

- **Images**: Rendered as `<img>` tags with proper alt text
- **Other files**: Download links with file name, size, and type
- **Local files**: Automatically copied from export to `assets/` directory
- **External URLs**: Used directly when local copies unavailable

### Search and Navigation

- **Real-time search**: Filter messages by content or username
- **Keyboard shortcuts**: Ctrl/Cmd+F to focus search, Escape to clear
- **Permalink support**: Click timestamps to copy message permalinks
- **Smooth scrolling**: Navigation between channels in combined view

## Hosting

The generated HTML files are completely static and can be hosted anywhere:

- **Local viewing**: Open `index.html` in any web browser
- **Static hosting**: Upload to GitHub Pages, Netlify, Vercel, or any web host
- **Web servers**: Serve with Apache, Nginx, or any HTTP server

## Customization

### Styling

Edit `static/style.css` to customize:
- Colors and typography
- Layout and spacing
- Message appearance
- Responsive breakpoints

### Search Behavior

Modify `static/script.js` to adjust:
- Search sensitivity
- Highlight behavior
- Keyboard shortcuts
- Navigation features

### Templates

Customize `templates/*.j2` files to modify:
- HTML structure
- Metadata display
- Message layout
- Page organization

## Troubleshooting

### Common Issues

1. **Missing users.json**: Some user mentions may show as "User-ID" instead of display names
2. **Large exports**: Processing may take time for exports with many messages
3. **File permissions**: Ensure write permissions to output directory
4. **Memory usage**: Very large exports may require significant RAM

### Timezone Display

Timestamps are displayed in the system's local timezone. The raw Unix timestamp is preserved in the "Details" section of each message.

## Data Preservation

All original message data is preserved in the "Details" disclosure section of each message as pretty-printed JSON, ensuring no information is lost during conversion.

## Browser Compatibility

The generated HTML works in all modern browsers:
- Chrome/Chromium 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## License

This project is provided as-is for converting Slack exports to HTML format.