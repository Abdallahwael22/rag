# Mini RAG API

A FastAPI service for building small, project-scoped retrieval-augmented generation (RAG) applications. Upload PDF or text files, split them into chunks, index their embeddings in Qdrant, then search the documents or generate grounded answers with OpenAI or Cohere.

## What it does

- Accepts `.txt` and `.pdf` uploads per project.
- Stores file metadata and text chunks in PostgreSQL.
- Persists uploaded files and a local Qdrant vector store on disk.
- Supports OpenAI and Cohere for generation and embeddings.
- Retrieves semantically similar chunks and uses them as RAG context.
- Includes English and Arabic RAG prompt templates; the generated response is instructed to match the question language.

## Architecture

```text
PDF / TXT upload
      |
      v
Local file storage + PostgreSQL (assets and chunks)
      |
      v
Embedding provider (OpenAI or Cohere) --> local Qdrant collection per project
                                                   |
Question --> query embedding --> retrieval --> generation provider --> answer
```

Each project uses a Qdrant collection named `collection_<project_id>`. Uploaded files are stored under `src/assets/files/<project_id>/`, while the local Qdrant data directory is configured by `VECTOR_DB_PATH` under `src/assets/database/`.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (recommended for PostgreSQL)
- An OpenAI or Cohere API key

## Quick start

### 1. Start PostgreSQL

The included Compose file starts PostgreSQL with the `pgvector` image. MongoDB is also defined for legacy compatibility, but the current application uses PostgreSQL for its relational data.

```bash
cd docker
docker compose up -d pgvector
```

### 2. Create a virtual environment and install dependencies

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Configure the application

Copy the template environment file to create your runtime configuration:

```Bash
cp src/.env.example src/.env
```
Open src/.env and update the values to match your local setup (e.g., database credentials, provider API keys, and model selections).

## IMPORTANT
If you switch between OpenAI and Cohere, make sure to update both BACKEND variables and verify that EMBEDDING_MODEL_SIZE exactly matches your chosen embedding model's vector dimensions.

For Cohere, set both backends to `COHERE`, set `COHERE_API_KEY`, and use compatible generation and embedding model IDs. Ensure `EMBEDDING_MODEL_SIZE` matches the selected embedding model's vector dimension.

### 4. Run the database migration

```bash
cd src/models/db_schemes/minirag
cp alembic.ini.example alembic.ini
```

Edit `alembic.ini` and set `sqlalchemy.url` to your database, for example:

```ini
sqlalchemy.url = postgresql+psycopg2://postgres:your-postgres-password@localhost:5432/postgres
```

Then apply the migration:

```bash
alembic upgrade head
```

### 5. Start the API

From `src/`:

```bash
uvicorn main:app --reload
```

The service is available at `http://127.0.0.1:8000`. Interactive API documentation is at `/docs`.

## API workflow

Use the same numeric `project_id` through the workflow. A project record is created automatically when first referenced.

### 1. Check the service

```bash
curl http://127.0.0.1:8000/api/v1/
```

### 2. Upload a document

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/data/upload/1" \
  -F "file=@./example.pdf"
```

Save the returned `file_id` if you want to process only that file.

### 3. Split document(s) into chunks

Process every uploaded file in project `1`:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/data/process/1" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size": 1000, "overlap_size": 150, "do_reset": 1}'
```

To process a single file, include its returned identifier:

```json
{
  "file_id": "returned-file-id.pdf",
  "chunk_size": 1000,
  "overlap_size": 150,
  "do_reset": 0
}
```

`do_reset: 1` removes the project's existing PostgreSQL chunks before inserting the newly processed chunks.

### 4. Index chunks in Qdrant

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nlp/index/push/1" \
  -H "Content-Type: application/json" \
  -d '{"do_reset": 1}'
```

Use `do_reset: 1` when rebuilding the project's vector index; otherwise, indexing appends records to the existing collection.

### 5. Search the vector index

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nlp/index/search/1" \
  -H "Content-Type: application/json" \
  -d '{"text": "What does the document say about refunds?", "limit": 5}'
```

### 6. Ask a RAG question

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nlp/index/answer/1" \
  -H "Content-Type: application/json" \
  -d '{"text": "What does the document say about refunds?", "limit": 5}'
```

The response includes the generated `answer`, plus `full_prompt` and `chat_history` to help inspect the RAG request.

### Index details

```bash
curl http://127.0.0.1:8000/api/v1/nlp/index/info/1
```

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/` | Returns the configured app name and version. |
| `POST` | `/api/v1/data/upload/{project_id}` | Upload a PDF or TXT file. |
| `POST` | `/api/v1/data/process/{project_id}` | Extract and split one file or all project files. |
| `POST` | `/api/v1/nlp/index/push/{project_id}` | Create/reset and populate the project vector index. |
| `GET` | `/api/v1/nlp/index/info/{project_id}` | Return Qdrant collection metadata. |
| `POST` | `/api/v1/nlp/index/search/{project_id}` | Return the most similar document chunks. |
| `POST` | `/api/v1/nlp/index/answer/{project_id}` | Retrieve context and generate a grounded answer. |

## Project layout

```text
src/
├── main.py                         # FastAPI startup and shared clients
├── routes/                         # HTTP routes and request schemas
├── controllers/                    # Upload, chunking, project, and RAG logic
├── models/                         # SQLAlchemy models and data access layer
├── stores/
│   ├── llm/                        # OpenAI/Cohere provider adapters and prompts
│   └── vectordb/                   # Qdrant adapter
├── assets/
│   ├── files/                      # Runtime uploaded files
│   └── database/                   # Runtime local Qdrant data
└── models/db_schemes/minirag/      # Alembic migration configuration
docker/docker-compose.yml           # PostgreSQL and legacy MongoDB services
```

## Notes

- Keep `.env`, uploaded files, and the local Qdrant directory out of version control; they contain secrets or runtime data.
- The upload validator accepts MIME types `text/plain` and `application/pdf`. Set `FILE_MAX_SIZE` in MB.
- The API calls external embedding/generation providers while processing, indexing, searching, and answering; make sure the selected credentials and models are enabled for your account.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
