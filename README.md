# AI Risk Assessment Agent - Proof of Concept

This project is a proof-of-concept AI agent designed to assess a company's risk posture concerning emerging technologies and provide advice on better incorporation strategies. It uses a local LLM and a curated corpus of PDF documents for its knowledge base.

## Project Structure

```
riskai_project/
├── backend/                  # FastAPI backend application
│   ├── api.py                # Main API logic, endpoints, RAG, LLM interaction
│   ├── main.py               # Uvicorn entry point (if separate from api.py, currently integrated)
│   ├── rag_pipeline/         # Modules for RAG (loader, embedder, store, retriever)
│   ├── data/                 # (Should be created by user) Directory for PDF corpus files
│   ├── vectordb/             # (Created by RAG) Persistent vector store
│   └── requirements.txt      # Python dependencies for backend
├── frontend/                 # Next.js frontend application
│   ├── pages/
│   │   └── index.tsx         # Main conversational UI page
│   ├── public/               # Static assets
│   ├── styles/
│   ├── lib/                  # Frontend utility functions (e.g., api.ts if used)
│   ├── package.json
│   └── ...                   # Other Next.js files
├── data/                     # (Create this at project root) For PDF documents (mounted into backend)
├── vectordb/                 # (Create this at project root) For persistent vector store (mounted into backend)
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── testing_plan.md
└── README.md                 # This file
```

## Features

*   **Conversational AI Interface:** Interacts with users through a chat-like UI to gather information.
*   **Dynamic Risk Questions:** Generates tailored questions based on the company profile.
*   **Weighted Risk Scoring:** Assesses risk across ~20 predefined categories with specific weights.
*   **RAG Pipeline:** Utilizes a Retrieval Augmented Generation (RAG) pipeline with a local vector store (Chroma) and PDF documents for context-aware responses.
*   **LLM Integration:** Leverages a small, free LLM (e.g., Falcon-RW-1B) for analysis and advice generation.
*   **Actionable Recommendations:** Provides tailored advice and links to resources.
*   **Dockerized Deployment:** Uses Docker and Docker Compose for easy local setup and execution.

## Prerequisites

*   **Docker:** Ensure Docker Desktop or Docker Engine is installed and running. (https://www.docker.com/get-started)
*   **Git:** For cloning the repository (if applicable).
*   **PDF Corpus:** You need to provide your own curated PDF documents related to governance and risk for emerging technologies.

## Setup and Running the Application Locally

1.  **Clone the Repository (if you haven't already):**
    ```bash
    # git clone <repository_url>
    # cd riskai_project
    ```

2.  **Prepare PDF Corpus:**
    *   Create a directory named `data` in the root of the `riskai_project` directory (i.e., `riskai_project/data/`).
    *   Place all your curated PDF documents into this `riskai_project/data/` directory.
    *   The backend will automatically process these PDFs on its first startup to build the vector database.

3.  **Create Vector Database Directory:**
    *   Create an empty directory named `vectordb` in the root of the `riskai_project` directory (i.e., `riskai_project/vectordb/`). This directory will be used to persist the embeddings database.

4.  **Build and Run with Docker Compose:**
    *   Open a terminal in the root of the `riskai_project` directory (where `docker-compose.yml` is located).
    *   Run the following command:
        ```bash
        docker-compose up --build
        ```
    *   This command will:
        *   Build the Docker images for both the backend and frontend if they don't exist or if Dockerfiles have changed.
        *   Start the containers for the backend and frontend services.
    *   The first time the backend starts, it will process the PDFs in the `data` directory to build the vector store in `vectordb`. This might take some time depending on the number and size of your PDFs and your machine's performance.
    *   Subsequent startups will be faster as they will load the existing vector store from `vectordb`.

5.  **Access the Application:**
    *   Once the containers are running (you'll see logs in your terminal), open your web browser and navigate to:
        `http://localhost:3000`

## Usage

1.  The AI will greet you and start asking questions to build a company profile.
2.  Answer the questions as prompted in the chat interface.
3.  After gathering the company profile, the AI will ask a series of more detailed risk questions related to the 20 defined categories.
4.  Once all questions are answered, the AI will submit them for analysis.
5.  The backend will process your answers, use the RAG pipeline and LLM to generate a risk assessment, including:
    *   An overall weighted risk score.
    *   A detailed breakdown of scores for each risk category.
    *   Actionable recommendations.
    *   Links to relevant resources.
6.  The results will be displayed in the chat interface.

## Development Notes & Customization

*   **Backend (FastAPI - `backend/api.py`):**
    *   **Risk Categories:** Defined in `RISK_CATEGORIES_DEFINITION`. You can modify categories, definitions, scoring focus, and weights here.
    *   **Scoring Logic:** The current scoring in `build_risk_table_from_answers` is a placeholder based on answer length and keywords. **This is a critical area for future improvement and should ideally involve more sophisticated NLP or LLM-based assessment of the textual answers against the category definitions and scoring focus.**
    *   **LLM Prompts:** The prompts used for `generate_llm_advice_async` can be further refined for better outputs.
    *   **RAG Pipeline:** Components are in `backend/rag_pipeline/`. Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings and `tiiuae/falcon-rw-1b` as the LLM (via HuggingFace `pipeline`). Ensure these models are accessible or adjust as needed. Model downloads may occur on first run if not cached by HuggingFace Transformers.
    *   **PDF Data Directory:** Hardcoded to `/app/data` inside the container, mapped from `./data` in `docker-compose.yml`.
    *   **Vector DB Directory:** Hardcoded to `/app/vectordb` inside the container, mapped from `./vectordb` in `docker-compose.yml`.
*   **Frontend (Next.js - `frontend/pages/index.tsx`):**
    *   **API Calls:** Uses `fetch` to `http://localhost:8000`. If you change backend port or deploy differently, update these.
    *   **Styling:** Uses Tailwind CSS.
*   **LLM Model:** The current setup relies on HuggingFace Transformers downloading and running the LLM locally. This requires sufficient RAM and CPU. For very large models or resource-constrained environments, consider using a dedicated LLM inference server or API.

## Managing the PDF Corpus

*   **Adding new PDFs:** Simply add new PDF files to the `riskai_project/data/` directory on your host machine.
*   **Updating the Vector Store:**
    1.  Stop the Docker containers: `docker-compose down`
    2.  Delete the contents of the `riskai_project/vectordb/` directory (or the entire directory and recreate it empty).
    3.  Restart the application: `docker-compose up --build` (the `--build` might not be strictly necessary if only data changed, but it's safe).
    *   The backend will detect an empty/missing vector store and rebuild it from all PDFs currently in the `data` directory.

## Stopping the Application

*   Press `Ctrl+C` in the terminal where `docker-compose up` is running.
*   To remove the containers (but not the images or volumes like `vectordb`), you can run: `docker-compose down`

## Troubleshooting

*   **Backend not starting / RAG errors:**
    *   Check Docker logs for the backend service: `docker-compose logs backend`
    *   Ensure the `data` directory exists at the project root and contains your PDFs.
    *   Ensure the `vectordb` directory exists at the project root.
    *   Ensure you have enough disk space and memory for the LLM and embedding models to download and run.
*   **Frontend not connecting to backend:**
    *   Check Docker logs for both services.
    *   Ensure the backend is running and accessible on port 8000 from the host.
    *   Check browser console for network errors.
*   **Slow performance:** LLM inference and RAG pipeline operations can be resource-intensive. Performance will depend on your machine specs and the size of the LLM/PDFs.

## Future Enhancements (Ideas)

*   More sophisticated, LLM-driven scoring of user answers against risk categories.
*   User authentication and session management.
*   Ability for users to upload PDFs directly through the UI.
*   More granular control over RAG parameters (chunk size, k-value for retrieval).
*   Integration with external GRC tools or knowledge bases.
*   More advanced prompt engineering for nuanced advice.
*   Streaming responses from the LLM for a more interactive feel.

