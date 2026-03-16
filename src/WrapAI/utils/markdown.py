# utils/markdown.py

from pathlib import Path
import re
import logging

# Logger Configuration
logger = logging.getLogger(__name__)

class MarkdownToText:
    def __init__(self, resource_path):
        """Initialize with the MD path."""
        self.text_has_been_cleaned = False
        self.cleaned_text = ''

        self.md_path = Path(resource_path)
        if not self.md_path.exists():
            raise FileNotFoundError(f"File not found: {self.md_path}")

    # Extract methods
    def extract_raw_text(self):
        """Extracts raw text from the MD file."""
        try:
            with self.md_path.open('r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"An error occurred while extracting raw text: {e}")
            return None

    def extract_clean_text(self):
        """Extracts clean text from the MD file by removing Markdown syntax."""
        try:
            raw_text = self.extract_raw_text()
            if raw_text is None:
                return None
            self.cleaned_text = self._strip_markdown(raw_text)
            self.text_has_been_cleaned = True
            return self.cleaned_text
        except Exception as e:
            logger.error(f"An error occurred while extracting clean text: {e}")
            return None

    # Helper methods
    @staticmethod
    def _strip_markdown(md_text):
        """Converts Markdown text to plain text by removing common Markdown syntax."""
        # Remove code blocks
        text = re.sub(r'```.*?```', '', md_text, flags=re.DOTALL)
        # Remove inline code
        text = re.sub(r'`.*?`', '', text)
        # Remove images
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        # Remove links but keep the link text
        text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)
        # Remove emphasis and strong emphasis
        text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
        text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
        # Remove headings
        text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)
        # Remove horizontal rules
        text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
        # Remove blockquotes
        text = re.sub(r'^\s*>+\s*', '', text, flags=re.MULTILINE)
        # Remove unordered list markers
        text = re.sub(r'^\s*[-+*]\s+', '', text, flags=re.MULTILINE)
        # Remove ordered list numbers
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        # Remove extra spaces
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    # Save methods
    def save_clean_text(self, output_path):
        """Saves the cleaned text to a specified file path."""
        try:
            if not self.text_has_been_cleaned:
                return None

            output_path = Path(output_path)
            with output_path.open('w', encoding='utf-8') as file:
                file.write(self.cleaned_text)
            logger.info(f"Cleaned text saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"An error occurred while saving clean text: {e}")
            return None


class MarkdownToTextFromString:
    def __init__(self, resource):
        """Initialize with a Markdown file path or raw Markdown string."""
        self.text_has_been_cleaned = False
        self.plain_text = ''

        # Confirm resource is string
        if isinstance(resource, str):
            self.md_text = resource  # Direct Markdown text
        else:
            raise ValueError("Invalid input: Provide a valid file path or a Markdown string.")

    def extract_plain_text(self):
        """Extracts clean text by removing Markdown syntax."""
        raw_text = self.md_text
        if raw_text is None:
            return None

        self.plain_text = self._strip_markdown(raw_text)
        self.text_has_been_cleaned = True
        return self.plain_text

    @staticmethod
    def _strip_markdown(md_text):
        """Converts Markdown text to plain text by removing common Markdown syntax."""
        text = re.sub(r'```.*?```', '', md_text, flags=re.DOTALL)  # Remove code blocks
        text = re.sub(r'`.*?`', '', text)  # Remove inline code
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Remove images
        text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)  # Remove links but keep text
        text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # Remove bold
        text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)  # Remove italics
        text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)  # Remove headings
        text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)  # Remove horizontal rules
        text = re.sub(r'^\s*>+\s*', '', text, flags=re.MULTILINE)  # Remove blockquotes
        text = re.sub(r'^\s*[-+*]\s+', '', text, flags=re.MULTILINE)  # Remove unordered lists
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Remove ordered lists
        # text = re.sub(r'\s{2,}', ' ', text)  # Remove extra spaces
        text = re.sub(r'[ \t]{2,}', ' ', text)  # Collapse multiple spaces/tabs without affecting newlines
        text = re.sub(r' {2,}', ' ', text)



        return text.strip()

    def save_clean_text(self, output_path):
        """Saves the plain text to a specified file path."""
        if not self.text_has_been_cleaned:
            return None

        try:
            output_path = Path(output_path)
            with output_path.open('w', encoding='utf-8') as file:
                file.write(self.plain_text)
            logger.info(f"Plain text saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving plain text: {e}")
            return None

    def __call__(self):
        """Makes the class instance callable, returning plain text."""
        return self.extract_plain_text()
