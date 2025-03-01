# File Organizer
This Python script organizes files within a specified directory based on a user-provided query. It leverages Google Gemini's generative AI capabilities to generate file organization commands and then executes those commands.

## Features
* Organizes files based on user-defined criteria.
* Supports PDF, DOCX, TXT, and MD files.
* Uses Google Gemini to generate file organization commands.
* Provides a preview of the files and their contents.
* Generates a detailed log file of the analysis process.
* Allows for a review of the generated commands before execution.
* Handles errors gracefully, providing informative messages to the user.
* Supports specifying the directory depth to be processed.

## Usage
1.  **Install dependencies:**  `pip install -r requirements.txt`
2.  **Set up your environment:** Create a `.env` file in the same directory as `organizer.py` and add your Google Gemini API key:

    ```
    GEMINI_API_KEY=YOUR_API_KEY
    ```
3.  **Run the script:**

    ```bash
    python organizer.py --source /path/to/source/directory --query "Organize documents related to project X" --depth 1
    ```

    Replace `/path/to/source/directory` with the actual path and `"Organize documents related to project X"` with your organization query.  The `--depth` argument specifies how many subdirectories to traverse (default is 1).

## Installation
1. Clone the repository: `git clone <repository_url>`
2. Navigate to the project directory: `cd file-organizer`
3. Install the required packages: `pip install -r requirements.txt`

## Technologies Used
* **Python:** The primary programming language for the script.
* **Google Gemini:** Used for natural language processing to generate file organization commands.
* **`dotenv`:** Loads environment variables from a `.env` file.
* **`argparse`:** Parses command-line arguments.
* **`PyPDF2`:** Reads and extracts text from PDF files.
* **`python-docx`:** Reads and extracts text from DOCX files.
* **`markdown`:** Processes markdown files.
* **`shlex`:** Splits shell commands safely.
* **`subprocess`:** Executes shell commands.
* **`json`:** Handles JSON data.

## Configuration
The script requires a `.env` file containing your Google Gemini API key:

```
GEMINI_API_KEY=YOUR_API_KEY
```

## Dependencies
The project dependencies are listed in `requirements.txt`.  Install them using: `pip install -r requirements.txt`

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

*README.md was made with [Etchr](https://etchr.dev)*