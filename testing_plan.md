# AI Agent Application: Testing Plan

This document outlines the testing strategy for the AI Risk Assessment Agent. The goal is to ensure the application is robust, reliable, and meets the user's requirements for functionality and user experience.

## 1. Testing Objectives

*   Verify that all backend AI components (RAG pipeline, LLM interaction, risk scoring, advisory generation) function correctly.
*   Ensure the frontend conversational UI provides a smooth and intuitive user experience.
*   Validate that the integration between the frontend and backend is seamless, with correct data flow.
*   Confirm the accuracy of risk assessments and the relevance of recommendations based on sample inputs.
*   Ensure the application can be run locally as intended.

## 2. Testing Scope

### 2.1. Backend Testing

*   **Unit Tests:** Individual functions and modules within the backend (`api.py`, RAG pipeline components).
    *   Test PDF loading and chunking.
    *   Test embedding generation.
    *   Test vector store operations (storing, loading, similarity search).
    *   Test RAG chain construction and invocation.
    *   Test `generate_dynamic_questions_for_categories` function for correct question generation based on profile.
    *   Test `build_risk_table_from_answers` for accurate scoring and weighting based on sample answers.
    *   Test `retrieve_rag_context` for relevant context retrieval.
    *   Test `generate_llm_advice_async` for correct prompt construction and parsing of LLM JSON output.
    *   Test API endpoint logic for `/initialize-assessment` and `/submit-answers` (mocking external calls where necessary).
*   **Integration Tests (Backend):**
    *   Test the full RAG pipeline from document ingestion to context retrieval.
    *   Test the interaction between the API endpoints and the core risk assessment/advisory logic.

### 2.2. Frontend Testing

*   **Component Tests (Conceptual, as direct execution isn't possible here):**
    *   Verify rendering of chat messages (user and AI).
    *   Test input handling and submission.
    *   Test display of assessment results.
    *   Verify state management for the conversational flow.
*   **End-to-End (E2E) Flow Testing (Manual/Simulated):**
    *   Simulate the full conversational flow from initial greeting to displaying results.

### 2.3. Full-Stack Integration Testing

*   Test the complete workflow: user interacts with frontend, frontend calls backend APIs, backend processes data and returns results, frontend displays results.
*   Verify data consistency across the stack.
*   Test error handling (e.g., API errors, LLM failures).

## 3. Testing Environment & Tools

*   **Environment:** Local development setup (simulated).
*   **Backend:** FastAPI, Python (pytest for unit tests).
*   **Frontend:** Next.js, TypeScript (Jest/React Testing Library conceptually).
*   **Data:** Sample company profiles, sample user answers, and the user-provided PDF corpus for the RAG pipeline.

## 4. Test Cases (High-Level for UAT)

### 4.1. Scenario 1: Happy Path - Full Assessment

*   **Description:** User completes the entire assessment flow successfully.
*   **Steps:**
    1.  AI greets user and starts collecting company profile information.
    2.  User provides valid answers for all company profile questions.
    3.  AI successfully calls `/initialize-assessment` and receives risk questions.
    4.  AI presents risk questions one by one.
    5.  User provides valid answers for all risk questions.
    6.  AI successfully calls `/submit-answers`.
    7.  Backend processes answers, performs RAG, invokes LLM, and calculates scores.
    8.  Frontend receives and correctly displays the overall score, risk table, recommendations, and resources.
*   **Expected Outcome:** Assessment is accurate, recommendations are relevant, UI is smooth.

### 4.2. Scenario 2: Edge Case - Minimal/Vague User Input

*   **Description:** User provides very brief or vague answers.
*   **Steps:** Similar to Scenario 1, but with minimal user input.
*   **Expected Outcome:** The system should still attempt to provide an assessment. Scores might be lower, and recommendations more generic. The LLM should handle potentially ambiguous input gracefully. Check for robustness.

### 4.3. Scenario 3: Error Handling - Backend API Failure

*   **Description:** Simulate a failure in one of the backend API calls (e.g., LLM service unavailable, RAG DB error).
*   **Steps:** During the assessment flow, simulate an error response from `/initialize-assessment` or `/submit-answers`.
*   **Expected Outcome:** The frontend should display a user-friendly error message. The application should not crash. The user should understand that an error occurred.

### 4.4. Scenario 4: Error Handling - Invalid User Input (Conceptual)

*   **Description:** User provides unexpected input types (though current UI is text-based).
*   **Steps:** If applicable, test how the system handles unexpected formats.
*   **Expected Outcome:** Graceful error handling or input sanitization.

### 4.5. Scenario 5: RAG Pipeline Validation

*   **Description:** Verify the RAG pipeline is correctly ingesting PDFs and retrieving relevant context.
*   **Steps:**
    1.  Ensure PDFs are placed in the `data/` directory.
    2.  Observe backend logs during startup for RAG initialization messages.
    3.  During an assessment, check the `context` passed to the LLM (via logging or debug) to ensure it's relevant to the user's input and the PDF corpus.
*   **Expected Outcome:** RAG pipeline initializes correctly and provides relevant context to the LLM, leading to more informed recommendations.

## 5. Test Execution (Simulated)

*   **Backend Unit Tests:** (Would be run using `pytest`)
*   **Manual End-to-End Testing:** Simulate running the FastAPI backend and Next.js frontend locally. Open the browser and interact with the application, following the UAT scenarios.
    *   Start backend: `python -m uvicorn main:app --reload` (or similar, from within the `backend` directory, assuming `main.py` contains the app and RAG initialization is correctly handled on startup or via a script).
    *   Start frontend: `npm run dev` (from within the `frontend` directory).
    *   Access `http://localhost:3000` (or the Next.js port).

## 6. Reporting

*   Log any identified issues, errors, or areas for improvement.
*   Update the `development_todo.md` based on test findings.

This testing plan provides a structured approach. Given the current environment, the focus will be on outlining these tests and manually reviewing code against these principles rather than live execution.
