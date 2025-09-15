# Overview

This is a Slack Export to HTML Converter that transforms Slack standard export ZIP files into readable, chronologically ordered HTML pages. The tool processes Slack workspace exports containing JSON message data and converts them into clean, navigable websites that preserve all message content including text, formatting, reactions, threads, files, and user interactions. The output can be generated as separate HTML files per channel or as a single combined file for easy sharing and archival.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Processing Pipeline
The application follows a file-based processing approach where it extracts ZIP archives to temporary directories, parses JSON data structures, and generates static HTML outputs using template rendering.

**Problem addressed**: Converting Slack's JSON export format into human-readable HTML while preserving all message metadata and formatting.

**Solution**: Multi-stage processing pipeline that parses user mappings, channel metadata, and message data, then renders everything through Jinja2 templates with custom Slack markdown conversion.

## Data Processing Layer
Uses Python's built-in JSON parsing to handle Slack export structure with dedicated classes for markdown conversion and message formatting.

**Key components**:
- SlackMarkdownConverter class handles Slack's mrkdwn format conversion to HTML
- Message aggregation across multiple daily JSON files per channel
- User ID to display name mapping using users.json
- Chronological sorting of messages by timestamp

## Template Rendering System
Employs Jinja2 templating engine to generate static HTML pages with responsive CSS and JavaScript for search functionality.

**Architecture decision**: Static site generation over dynamic rendering for portability and ease of deployment.

**Benefits**: 
- No server requirements
- Easy to host and share
- Fast loading times
- Works offline

## File Organization Strategy
Outputs follow a structured directory layout with separate HTML files per channel plus an index overview page, or optionally a single combined file.

**Structure**:
- index.html (channel overview and navigation)
- Individual channel HTML files (e.g., general.html)
- static/ directory containing CSS and JavaScript assets
- Optional combined.html for single-file output

## Message Processing Engine
Handles complex Slack message structures including threads, reactions, file attachments, user mentions, and emoji conversion.

**Features**:
- Thread grouping with visual indentation
- User mention resolution (@username display)
- Emoji shortcode to Unicode conversion
- File and image rendering with proper HTML tags
- Slack formatting preservation (bold, italic, code blocks, lists)

# External Dependencies

## Core Libraries
- **Jinja2** (3.1.0+): Template engine for HTML generation and rendering
- **mistune** (3.0.0+): Markdown parser used for processing Slack's mrkdwn formatting

## Python Standard Library Dependencies
- **zipfile**: ZIP archive extraction and handling
- **json**: Slack export JSON data parsing
- **argparse**: Command-line interface and argument processing
- **datetime**: Timestamp conversion and formatting
- **pathlib**: File system path manipulation
- **tempfile**: Temporary directory management for ZIP extraction
- **shutil**: File operations and directory copying
- **html**: HTML entity escaping for safe output
- **re**: Regular expression pattern matching for text processing

## Frontend Assets
- **CSS**: Custom stylesheet with responsive design and Slack-like visual styling
- **JavaScript**: Client-side search functionality for filtering messages and channels

## Input Data Format
- **Slack Standard Export**: ZIP files containing channel directories with daily JSON files, users.json for user mapping, and optional channels.json for metadata
- **JSON Structure**: Slack's native message format with support for all message types, threads, reactions, and file attachments