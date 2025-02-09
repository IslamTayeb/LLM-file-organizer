import click
import os
import PyPDF2
import PIL.Image
import io
import docx
import json
from typing import Dict, Any
from pathlib import Path

class ContentAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.extension = Path(file_path).suffix.lower()

    def analyze(self) -> Dict[str, Any]:
        """Analyze file content and return metadata."""
        if not os.path.exists(self.file_path):
            return {"error": "File not found"}

        metadata = {
            "filename": os.path.basename(self.file_path),
            "extension": self.extension,
            "size": os.path.getsize(self.file_path),
            "first_text": "",
            "preview": ""
        }

        try:
            if self.extension == '.pdf':
                metadata.update(self._analyze_pdf())
            elif self.extension in ['.png', '.jpg', '.jpeg']:
                metadata.update(self._analyze_image())
            elif self.extension == '.docx':
                metadata.update(self._analyze_docx())
            elif self.extension == '.txt':
                metadata.update(self._analyze_text())
        except Exception as e:
            metadata["error"] = str(e)

        return metadata

    def _analyze_pdf(self) -> Dict[str, str]:
        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) > 0:
                first_page = reader.pages[0].extract_text()
                return {
                    "first_text": first_page[:500],
                    "preview": first_page[:100]
                }
        return {"first_text": "", "preview": ""}

    def _analyze_image(self) -> Dict[str, str]:
        with PIL.Image.open(self.file_path) as img:
            # Create thumbnail
            img.thumbnail((100, 100))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=30)
            return {
                "preview": f"Image size: {img.size}",
                "compressed_size": len(buffer.getvalue())
            }

    def _analyze_docx(self) -> Dict[str, str]:
        doc = docx.Document(self.file_path)
        if doc.paragraphs:
            first_para = doc.paragraphs[0].text
            return {
                "first_text": first_para,
                "preview": first_para[:100]
            }
        return {"first_text": "", "preview": ""}

    def _analyze_text(self) -> Dict[str, str]:
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return {
                "first_text": content[:500],
                "preview": content[:100]
            }

class FileOrganizer:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.metadata_file = os.path.join(base_path, "content_index.json")
        self.content_index = self._load_index()

    def _load_index(self) -> Dict:
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.content_index, f, indent=2)

    def index_files(self, directory: str):
        """Index all files in the directory and save their metadata."""
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                analyzer = ContentAnalyzer(file_path)
                metadata = analyzer.analyze()
                self.content_index[file_path] = metadata
        self._save_index()

    def organize_by_query(self, query: str, target_dir: str):
        """Organize files based on the query into target directory."""
        os.makedirs(target_dir, exist_ok=True)

        # Simple keyword matching (can be enhanced with NLP/ML)
        query = query.lower()
        for file_path, metadata in self.content_index.items():
            matches = False
            for key in ['first_text', 'preview', 'filename']:
                if key in metadata and query in str(metadata[key]).lower():
                    matches = True
                    break

            if matches:
                dest = os.path.join(target_dir, os.path.basename(file_path))
                os.symlink(file_path, dest)

@click.group()
def cli():
    """Content-aware file organization tool."""
    pass

@cli.command()
@click.argument('directory')
def index(directory):
    """Index files in the specified directory."""
    organizer = FileOrganizer(directory)
    organizer.index_files(directory)
    click.echo(f"Indexed files in {directory}")

@cli.command()
@click.argument('query')
@click.argument('target_dir')
@click.option('--base-dir', default=".", help="Base directory containing the index")
def organize(query, target_dir, base_dir):
    """Organize files matching the query into target directory."""
    organizer = FileOrganizer(base_dir)
    organizer.organize_by_query(query, target_dir)
    click.echo(f"Organized matching files into {target_dir}")

if __name__ == '__main__':
    cli()
