# IronStore Assistant

A simple chat assistant that answers questions about IronStore's internal documents. It searches the PDFs for relevant passages, then uses an AI model to write an answer with citations.

## How it works

1. **Ingest** (`ingest.py`): Reads every PDF in `documents/`, splits the text into chunks, converts each chunk into an embedding (a list of numbers that represents its meaning), and saves them in a local database in `chroma_db/`.
2. **Search** (`chat.py`): When you ask a question, the question is converted into an embedding too. The database returns the chunks with the most similar meaning.
3. **Answer** (`chat.py`): The best chunks are passed to the AI model, which writes an answer and cites the document title and page number. If no chunk is similar enough, the assistant says it doesn't know.
4. **Chat screen** (`app.py`): A simple web page where you type questions and read the answers as they stream in.

## Project structure

```
ironstore-assistant/
├── documents/        # IronStore PDF files
├── chroma_db/        # created by ingest.py (vector database)
├── .env              # your OpenAI API key
├── requirements.txt  # Python packages
├── ingest.py         # builds the database from the PDFs
├── chat.py           # search and answer logic, plus a terminal chat
└── app.py            # Streamlit chat screen
```

## Setup

1. Make sure Python 3.10 or newer is installed.

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS / Linux
   ```

3. Install the packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a file called `.env` in the project folder with your OpenAI key:

   ```
   OPENAI_API_KEY=your-key-here
   ```

5. Build the database:

   ```bash
   python ingest.py
   ```

## Running the assistant

**Chat screen (recommended):**

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

**Terminal chat:**

```bash
python chat.py
```

Type `quit` to exit.

## Changing the settings

- **Abstain threshold (`MIN_SCORE` in `chat.py`):** If the assistant refuses questions it should answer, lower this value (for example, 0.30 to 0.25). If it answers unrelated questions, raise it.
- **Number of chunks (`k` in `chat.py`):** How many passages are sent to the model. Increase it if answers miss relevant information.
- **Chunk size (`chunk_size` in `ingest.py`):** Controls how much text goes into each chunk. After changing it, run `python ingest.py` again.

## Updating the documents

Whenever you add, remove, or change a PDF, run `python ingest.py` again. It deletes the old database and rebuilds it from scratch.

## Limitations

- The chat history is kept only while the browser page is open. Refreshing the page clears it.
- The assistant answers only from the indexed documents. It is not a replacement for HR, Finance, or other department contacts.
- The model can still paraphrase incorrectly. Check important answers against the cited page.