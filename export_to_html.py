#!/usr/bin/env python3
"""
Slack Export to HTML Converter

Converts a Slack standard export ZIP into readable HTML pages.
"""

import argparse
import json
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import jinja2
import mistune


class SlackMarkdownConverter:
    """Converts Slack mrkdwn formatting to HTML."""
    
    def __init__(self, users_map: Dict[str, str]):
        self.users_map = users_map
        self.markdown = mistune.create_markdown(
            plugins=['strikethrough', 'mark', 'insert', 'superscript', 'subscript']
        )
        
        # Common emoji mappings
        self.emoji_map = {
            ':slightly_smiling_face:': '🙂',
            ':smile:': '😊',
            ':laughing:': '😆',
            ':joy:': '😂',
            ':thumbsup:': '👍',
            ':thumbsdown:': '👎',
            ':heart:': '❤️',
            ':fire:': '🔥',
            ':tada:': '🎉',
            ':eyes:': '👀',
            ':thinking_face:': '🤔',
            ':wave:': '👋',
            ':clap:': '👏',
            ':100:': '💯',
            ':white_check_mark:': '✅',
            ':x:': '❌',
            ':warning:': '⚠️',
            ':information_source:': 'ℹ️',
        }
    
    def convert_user_mentions(self, text: str) -> str:
        """Convert <@U123> mentions to @displayname."""
        def replace_mention(match):
            user_id = match.group(1)
            display_name = self.users_map.get(user_id, f"@unknown-{user_id}")
            return f'<span class="user-mention">@{display_name}</span>'
        
        return re.sub(r'<@([A-Z0-9]+)>', replace_mention, text)
    
    def convert_links(self, text: str) -> str:
        """Convert <http://...|label> and <http://...> patterns."""
        # Handle <url|label> format
        text = re.sub(
            r'<(https?://[^|>]+)\|([^>]+)>',
            r'<a href="\1" target="_blank">\2</a>',
            text
        )
        
        # Handle <url> format
        text = re.sub(
            r'<(https?://[^>]+)>',
            r'<a href="\1" target="_blank">\1</a>',
            text
        )
        
        return text
    
    def convert_emoji(self, text: str) -> str:
        """Convert :emoji: to unicode emoji or leave as text."""
        def replace_emoji(match):
            emoji_name = match.group(0)
            return self.emoji_map.get(emoji_name, emoji_name)
        
        return re.sub(r':[a-z_]+:', replace_emoji, text)
    
    def convert_slack_formatting(self, text: str) -> str:
        """Convert Slack-specific formatting."""
        if not text:
            return ""
        
        # Convert user mentions
        text = self.convert_user_mentions(text)
        
        # Convert links
        text = self.convert_links(text)
        
        # Convert emoji
        text = self.convert_emoji(text)
        
        # Handle inline code (single backticks)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Handle basic Slack formatting
        text = re.sub(r'\*([^*]+)\*', r'<strong>\1</strong>', text)  # Bold
        text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)  # Italic
        text = re.sub(r'~([^~]+)~', r'<del>\1</del>', text)  # Strikethrough
        
        # Handle code blocks (triple backticks)
        text = re.sub(
            r'```([^`]*)```',
            r'<pre><code>\1</code></pre>',
            text,
            flags=re.DOTALL
        )
        
        # Handle blockquotes (lines starting with >)
        lines = text.split('\n')
        processed_lines = []
        in_blockquote = False
        
        for line in lines:
            if line.strip().startswith('>'):
                if not in_blockquote:
                    processed_lines.append('<blockquote>')
                    in_blockquote = True
                processed_lines.append(line.strip()[1:].strip())
            else:
                if in_blockquote:
                    processed_lines.append('</blockquote>')
                    in_blockquote = False
                processed_lines.append(line)
        
        if in_blockquote:
            processed_lines.append('</blockquote>')
        
        text = '\n'.join(processed_lines)
        
        # Convert newlines to <br> tags
        text = text.replace('\n', '<br>\n')
        
        return text


class SlackExportConverter:
    """Main converter class for Slack exports."""
    
    def __init__(self, zip_path: str, output_dir: str, combined: bool = False):
        self.zip_path = Path(zip_path)
        self.output_dir = Path(output_dir)
        self.combined = combined
        self.temp_dir: Optional[Path] = None
        self.users_map = {}
        self.channels_map = {}
        self.markdown_converter: Optional[SlackMarkdownConverter] = None
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'assets').mkdir(exist_ok=True)
        
        # Set up Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def extract_zip(self) -> Path:
        """Extract the Slack export ZIP to a temporary directory."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        
        return self.temp_dir
    
    def load_users(self) -> None:
        """Load users.json and create user ID to display name mapping."""
        if not self.temp_dir:
            return
        users_file = self.temp_dir / 'users.json'
        
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                
            for user in users_data:
                user_id = user.get('id')
                display_name = (
                    user.get('profile', {}).get('display_name') or
                    user.get('profile', {}).get('real_name') or
                    user.get('name') or
                    f"User-{user_id}"
                )
                if user_id:
                    self.users_map[user_id] = display_name
    
    def load_channels(self) -> None:
        """Load channels.json if available."""
        if not self.temp_dir:
            return
        channels_file = self.temp_dir / 'channels.json'
        
        if channels_file.exists():
            with open(channels_file, 'r', encoding='utf-8') as f:
                channels_data = json.load(f)
                
            for channel in channels_data:
                channel_id = channel.get('id')
                if channel_id:
                    self.channels_map[channel_id] = {
                        'name': channel.get('name', channel_id),
                        'topic': channel.get('topic', {}).get('value', ''),
                        'purpose': channel.get('purpose', {}).get('value', '')
                    }
    
    def get_channel_messages(self, channel_dir: Path) -> List[Dict[str, Any]]:
        """Get all messages from a channel directory, sorted by timestamp."""
        messages = []
        
        # Process all JSON files in the channel directory
        for json_file in sorted(channel_dir.glob('*.json')):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    day_messages = json.load(f)
                    messages.extend(day_messages)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Warning: Could not read {json_file}: {e}")
        
        # Sort messages by timestamp
        messages.sort(key=lambda msg: float(msg.get('ts', 0)))
        
        return messages
    
    def process_message_text(self, message: Dict[str, Any]) -> str:
        """Process message text with Slack formatting."""
        text = message.get('text', '')
        
        # Handle blocks format (newer Slack messages)
        if not text and 'blocks' in message:
            text_parts = []
            for block in message['blocks']:
                if block.get('type') == 'rich_text':
                    for element in block.get('elements', []):
                        if element.get('type') == 'rich_text_section':
                            for text_element in element.get('elements', []):
                                if text_element.get('type') == 'text':
                                    text_parts.append(text_element.get('text', ''))
                                elif text_element.get('type') == 'user':
                                    user_id = text_element.get('user_id')
                                    user_name = self.users_map.get(user_id, f"@{user_id}")
                                    text_parts.append(f"<@{user_id}>")
            text = ''.join(text_parts)
        
        return self.markdown_converter.convert_slack_formatting(text) if text and self.markdown_converter else ""
    
    def format_timestamp(self, ts: str) -> Tuple[str, str]:
        """Format timestamp to human-readable form."""
        try:
            timestamp = float(ts)
            dt = datetime.fromtimestamp(timestamp)
            human_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            return human_time, ts
        except (ValueError, TypeError):
            return ts, ts
    
    def process_reactions(self, reactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process message reactions."""
        processed_reactions = []
        
        for reaction in reactions:
            emoji = reaction.get('name', '')
            count = reaction.get('count', 0)
            users = reaction.get('users', [])
            
            # Convert emoji names to unicode if possible
            emoji_display = f':{emoji}:'
            if self.markdown_converter:
                emoji_display = self.markdown_converter.emoji_map.get(f':{emoji}:', f':{emoji}:')
            
            # Get user names for tooltip
            user_names = [self.users_map.get(user_id, f"User-{user_id}") for user_id in users]
            
            processed_reactions.append({
                'emoji': emoji_display,
                'count': count,
                'users': user_names
            })
        
        return processed_reactions
    
    def process_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process file attachments."""
        processed_files = []
        
        for file_info in files:
            file_data = {
                'name': file_info.get('name', 'Unknown file'),
                'size': file_info.get('size', 0),
                'mimetype': file_info.get('mimetype', ''),
                'url': file_info.get('url_private', file_info.get('permalink', '')),
                'is_image': False,
                'local_path': None
            }
            
            # Check if it's an image
            if file_data['mimetype'].startswith('image/'):
                file_data['is_image'] = True
            
            # Look for local file copies in the export
            file_id = file_info.get('id')
            if file_id and self.temp_dir:
                # Common patterns for local files in Slack exports
                potential_paths = [
                    self.temp_dir / file_data['name'],
                    self.temp_dir / f"{file_id}_{file_data['name']}",
                    self.temp_dir / file_id,
                ]
                
                for potential_path in potential_paths:
                    if potential_path.exists():
                        # Copy to assets directory
                        assets_dir = self.output_dir / 'assets'
                        local_filename = f"{file_id}_{file_data['name']}" if file_id else file_data['name']
                        local_path = assets_dir / local_filename
                        
                        try:
                            shutil.copy2(potential_path, local_path)
                            file_data['url'] = f"assets/{local_filename}"
                            file_data['local_path'] = str(local_path)
                            break
                        except (OSError, IOError) as e:
                            print(f"Warning: Could not copy file {potential_path}: {e}")
            
            processed_files.append(file_data)
        
        return processed_files
    
    def group_threads(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group thread replies under parent messages."""
        threads = {}
        main_messages = []
        
        for message in messages:
            thread_ts = message.get('thread_ts')
            
            if thread_ts and thread_ts != message.get('ts'):
                # This is a reply
                if thread_ts not in threads:
                    threads[thread_ts] = []
                threads[thread_ts].append(message)
            else:
                # This is a main message (or thread parent)
                main_messages.append(message)
        
        # Attach replies to parent messages
        for message in main_messages:
            ts = message.get('ts')
            if ts in threads:
                message['replies'] = threads[ts]
                message['reply_count'] = len(threads[ts])
            else:
                message['replies'] = []
                message['reply_count'] = 0
        
        return main_messages
    
    def process_channel(self, channel_name: str, channel_dir: Path) -> Dict[str, Any]:
        """Process a single channel and return processed data."""
        messages = self.get_channel_messages(channel_dir)
        
        # Process each message
        processed_messages = []
        for message in messages:
            # Get user info
            user_id = message.get('user')
            bot_id = message.get('bot_id')
            username = message.get('username')
            
            if user_id:
                display_name = self.users_map.get(user_id, f"User-{user_id}")
            elif bot_id:
                display_name = message.get('bot_profile', {}).get('name', f"Bot-{bot_id}")
            elif username:
                display_name = username
            else:
                display_name = "Unknown User"
            
            # Process message
            processed_message = {
                'ts': message.get('ts', ''),
                'human_time': self.format_timestamp(message.get('ts', ''))[0],
                'raw_ts': message.get('ts', ''),
                'user_id': user_id,
                'display_name': display_name,
                'text': self.process_message_text(message),
                'subtype': message.get('subtype'),
                'edited': 'edited' in message,
                'reactions': self.process_reactions(message.get('reactions', [])),
                'files': self.process_files(message.get('files', [])),
                'thread_ts': message.get('thread_ts'),
                'permalink': message.get('permalink', ''),
                'raw_message': message  # For the details disclosure
            }
            
            processed_messages.append(processed_message)
        
        # Group threads
        grouped_messages = self.group_threads(processed_messages)
        
        # Get channel info
        channel_info = self.channels_map.get(channel_name, {})
        
        return {
            'name': channel_name,
            'display_name': channel_info.get('name', channel_name),
            'topic': channel_info.get('topic', ''),
            'purpose': channel_info.get('purpose', ''),
            'messages': grouped_messages,
            'message_count': len(messages),
            'date_range': self.get_date_range(messages)
        }
    
    def get_date_range(self, messages: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Get the date range for messages."""
        if not messages:
            return "", ""
        
        timestamps = [float(msg.get('ts', 0)) for msg in messages if msg.get('ts')]
        if not timestamps:
            return "", ""
        
        first_date = datetime.fromtimestamp(min(timestamps)).strftime("%Y-%m-%d")
        last_date = datetime.fromtimestamp(max(timestamps)).strftime("%Y-%m-%d")
        
        return first_date, last_date
    
    def generate_html(self, channels_data: List[Dict[str, Any]]) -> None:
        """Generate HTML files from processed channel data."""
        # Copy static files
        self.copy_static_files()
        
        # Generate index page
        self.generate_index_page(channels_data)
        
        # Generate channel pages
        if self.combined:
            self.generate_combined_page(channels_data)
        else:
            for channel_data in channels_data:
                self.generate_channel_page(channel_data)
    
    def copy_static_files(self) -> None:
        """Copy CSS and JS files to output directory."""
        static_dir = self.output_dir / 'static'
        static_dir.mkdir(exist_ok=True)
        
        # Copy CSS and JS files from the static directory
        source_static = Path('static')
        if source_static.exists():
            for file_path in source_static.glob('*'):
                if file_path.is_file():
                    shutil.copy2(file_path, static_dir / file_path.name)
    
    def generate_index_page(self, channels_data: List[Dict[str, Any]]) -> None:
        """Generate the index.html page."""
        template = self.jinja_env.get_template('index.html.j2')
        
        html_content = template.render(
            channels=channels_data,
            combined=self.combined,
            generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        with open(self.output_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_channel_page(self, channel_data: Dict[str, Any]) -> None:
        """Generate HTML page for a single channel."""
        template = self.jinja_env.get_template('channel.html.j2')
        
        html_content = template.render(
            channel=channel_data,
            generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        filename = f"{channel_data['name']}.html"
        with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_combined_page(self, channels_data: List[Dict[str, Any]]) -> None:
        """Generate a single combined HTML page for all channels."""
        template = self.jinja_env.get_template('combined.html.j2')
        
        html_content = template.render(
            channels=channels_data,
            generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        with open(self.output_dir / 'combined.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def convert(self) -> None:
        """Main conversion method."""
        print(f"Extracting {self.zip_path}...")
        extract_dir = self.extract_zip()
        
        print("Loading users and channels...")
        self.load_users()
        self.load_channels()
        
        # Initialize markdown converter with users map
        self.markdown_converter = SlackMarkdownConverter(self.users_map)
        
        print("Processing channels...")
        channels_data = []
        
        # Find all channel directories
        for item in extract_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Skip if it doesn't contain JSON files
                if not list(item.glob('*.json')):
                    continue
                
                print(f"Processing channel: {item.name}")
                channel_data = self.process_channel(item.name, item)
                channels_data.append(channel_data)
        
        print("Generating HTML...")
        self.generate_html(channels_data)
        
        print(f"Conversion complete! Output saved to: {self.output_dir}")
        
        # Cleanup
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Slack export ZIP to HTML"
    )
    parser.add_argument(
        '--zip',
        required=True,
        help='Path to Slack export ZIP file'
    )
    parser.add_argument(
        '--out',
        required=True,
        help='Output directory for HTML files'
    )
    parser.add_argument(
        '--combined',
        action='store_true',
        help='Generate a single combined HTML file instead of separate channel files'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not Path(args.zip).exists():
        print(f"Error: ZIP file not found: {args.zip}")
        return 1
    
    try:
        converter = SlackExportConverter(args.zip, args.out, args.combined)
        converter.convert()
        return 0
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1


if __name__ == '__main__':
    exit(main())