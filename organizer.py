import os
from dotenv import load_dotenv
import argparse
import google.generativeai as genai
import json
import PyPDF2
from docx import Document
import markdown
from datetime import datetime
import shlex
import subprocess

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class DocumentAnalyzer:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in .env")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    def extract_content(self, file_path):
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        try:
            if ext == ".pdf":
                with open(file_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    # Get first 3 pages or all pages if less than 3
                    for page_num in range(min(3, len(reader.pages))):
                        text += f"\n=== Page {page_num + 1} ===\n"
                        text += reader.pages[page_num].extract_text()
                    return text
            elif ext == ".docx":
                doc = Document(file_path)
                return "\n".join(
                    [p.text for p in doc.paragraphs[:30]]
                )  # Increased from 10
            elif ext in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                    return file.read(10000)  # Increased from 2000
            return ""
        except Exception as e:
            print(f"Warning: Cannot read {file_path}: {str(e)}")
            return ""

    def get_files_metadata(self, source_dir, depth=1):
        files_metadata = []
        valid_extensions = {".pdf", ".docx", ".txt", ".md"}
        log_entries = []

        source_dir = os.path.expanduser(source_dir)
        for root, _, files in os.walk(source_dir):
            if root[len(source_dir) :].count(os.sep) > depth:
                continue

            for file in files:
                if os.path.splitext(file)[1].lower() not in valid_extensions:
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)

                try:
                    content = self.extract_content(file_path)
                    metadata = {
                        "filename": file,
                        "absolute_path": file_path,
                        "relative_path": rel_path,
                        "content": content,
                        "extension": os.path.splitext(file)[1].lower(),
                        "directory": os.path.dirname(rel_path),
                    }
                    files_metadata.append(metadata)

                    # Add to log
                    log_entries.append(
                        f"\n{'='*80}\nFile: {file_path}\nContent Preview:\n{content[:500]}...\n{'='*80}\n"
                    )
                except Exception as e:
                    log_entries.append(f"\nERROR processing {file_path}: {str(e)}\n")

        # Write log file
        log_path = os.path.join(source_dir, "file_analysis.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_entries))

        print(f"\nDetailed analysis log written to: {log_path}")
        return files_metadata, source_dir

    def generate_commands(self, source_dir, query, depth):
        files_metadata, abs_source = self.get_files_metadata(source_dir, depth)

        prompt = f"""Generate file organization commands based on these requirements:

SOURCE: {abs_source}
QUERY: {query}

FILES:
{json.dumps([{
    "name": m["filename"],
    "path": m["relative_path"],
    "content": m["content"] + "..." if m["content"] else ""
} for m in files_metadata], indent=2)}

REQUIREMENTS:
1. Return ONLY a JSON object without code fences or formatting
2. JSON must have this exact structure:
{{
    "explanation": "What the commands will do",
    "commands": [
        "mkdir -p folder_name",
        "cp \\"./file.pdf\\" \\"./folder_name/\\""
    ]
}}

RULES:
- Use only mkdir -p and cp commands
- Always quote file paths
- Use relative paths from source directory
- No wildcards or complex commands
- Target folder name should be simple (no spaces)
- Each cp command copies one file"""

        try:
            response = self.model.generate_content(prompt)
            # Clean up response text
            text = response.text.strip()
            if text.startswith("```"):
                text = text[text.find("{") : text.rfind("}") + 1]
            return json.loads(text)
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            print(f"Raw response:\n{response.text}")
            return {"explanation": "Failed to generate valid commands", "commands": []}


def safe_execute(source_dir, commands):
    source_dir = os.path.expanduser(source_dir)
    os.chdir(source_dir)

    for cmd in commands:
        try:
            parts = shlex.split(cmd)
            if not parts:
                continue

            # Only allow mkdir and cp
            if parts[0] not in ["mkdir", "cp"]:
                print(f"Skipping unauthorized command: {cmd}")
                continue

            subprocess.run(parts, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {cmd}")
            print(f"Error: {e}")
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description="File organizer")
    parser.add_argument("--source", required=True, help="Source directory")
    parser.add_argument("--query", required=True, help="Organization query")
    parser.add_argument("--depth", type=int, default=1, help="Directory depth")

    args = parser.parse_args()

    analyzer = DocumentAnalyzer()
    result = analyzer.generate_commands(args.source, args.query, args.depth)

    print("\nPlan:")
    print(result["explanation"])
    print("\nCommands:")
    for cmd in result["commands"]:
        print(cmd)

    if input("\nExecute? (y/N): ").lower() == "y":
        if safe_execute(args.source, result["commands"]):
            print("Complete!")
        else:
            print("Failed.")


if __name__ == "__main__":
    main()
