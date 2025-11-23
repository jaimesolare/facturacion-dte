# Research & Decisions

**Feature**: Sistema de Emisión de DTE (El Salvador)

This document outlines the key technical research and decisions made for the project.

---

### 1. Backend Technology Stack

- **Decision**: Python 3.11+ with FastAPI.
- **Rationale**: Python is a mature language with excellent support for data manipulation, cryptography, and web services. FastAPI is a modern, high-performance web framework that is easy to learn and use. Its automatic data validation via Pydantic is ideal for ensuring the JSON structures strictly adhere to the Ministry of Finance's (MH) schemas. Its asynchronous capabilities are well-suited for handling I/O-bound operations like API calls to the MH.
- **Alternatives considered**: 
  - **Node.js with Express/Fastify**: A strong contender, especially for JSON-heavy applications. However, Python's data science and cryptographic libraries are slightly more mature and better suited for potential future requirements.
  - **Go**: Offers superior performance but has a steeper learning curve and less flexible data handling compared to Python for this specific use case.

---

### 2. Database and Data Archival

- **Decision**: PostgreSQL 15+.
- **Rationale**: The requirement to store DTEs for 15 years necessitates a robust, reliable, and scalable relational database. PostgreSQL is renowned for its data integrity, extensibility, and strong support for JSON data types (`JSONB`). This allows for efficient storage and indexing of the raw DTE JSON documents alongside structured relational data for querying and reporting.
- **Alternatives considered**: 
  - **MySQL**: A viable alternative, but PostgreSQL's `JSONB` support is generally considered more powerful for indexing and querying embedded JSON fields.
  - **NoSQL (e.g., MongoDB)**: While excellent for storing JSON documents, ensuring long-term relational integrity and handling complex queries across different document types could become more challenging compared to a hybrid SQL approach.

---

### 3. DTE Signing (JWS Standard)

- **Decision**: Use the `python-jose` library.
- **Rationale**: The MH requires DTEs to be signed using the JSON Web Signature (JWS) standard. The `python-jose` library is a well-maintained, full-featured implementation of the JOSE standards (JWS, JWE, JWK, JWA). It provides a straightforward API for creating compact, signed JWS objects, which is exactly what is needed to sign the DTE JSON payload with the private key.
- **Alternatives considered**: 
  - **Custom Implementation**: Building the JWS logic from scratch would be time-consuming and error-prone. Leveraging a standard, audited library is the secure and efficient choice.
  - **Wrapping the MH's `DTE-Firmador`**: While the MH provides a tool, integrating it as an external dependency (e.g., a local web service) adds operational complexity and a point of failure. A native Python library is more tightly integrated and easier to manage within the application.

---

### 4. API Client and Resilience

- **Decision**: Use the `httpx` library with custom resilience logic.
- **Rationale**: `httpx` is a modern, fully-featured HTTP client for Python that supports both sync and async requests, fitting perfectly with FastAPI. For the retry and contingency logic, a custom wrapper or decorator using `httpx` will be implemented. This provides full control over the retry timing, backoff strategy, and the conditions under which the system should enter contingency mode, as specified in the requirements.
- **Alternatives considered**: 
  - **`requests` library**: A classic and stable choice, but `httpx` offers a more modern API and native async support.
  - **Libraries with built-in retries (e.g., `requests.Session` with an adapter)**: These are good, but a custom implementation provides the necessary control to handle the specific logic of when to give up and trigger a contingency event, which is more complex than a simple retry.
