# Tasks: Sistema de Emisión de DTE

**Input**: Design documents from `/specs/001-sistema-emision-dte-sv/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md

**Tests**: Tasks for tests are included as per the TDD principle in the constitution.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

- Paths assume the single project structure defined in `plan.md` (`src/`, `tests/`).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [x] T001 Create project structure (`src`, `tests` directories) as defined in `plan.md`
- [x] T002 Initialize Python project with a virtual environment and create `requirements.txt`
- [x] T003 [P] Add initial dependencies to `requirements.txt`: `fastapi`, `uvicorn`, `psycopg2-binary`, `alembic`, `python-jose`, `httpx`, `pydantic`
- [x] T004 [P] Configure linting (`flake8` or `ruff`) and formatting (`black`) tools in `.vscode/settings.json` or `pyproject.toml`
- [x] T005 Configure Alembic for database migrations in `alembic.ini` and `src/core/db.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

- [x] T006 [P] Define SQLAlchemy base models for `Credenciales` and `DTE` in `src/models/db_models.py` based on `data-model.md`
- [x] T007 [P] Create Pydantic schemas for API data validation in `src/models/schemas.py`
- [x] T008 Create initial database migration for `Credenciales` and `DTE` tables using `alembic revision --autogenerate`
- [x] T009 Implement a service to manage encrypted credentials in `src/core/security.py`
- [x] T010 Implement the JWS signing service in `src/core/signing.py` using the `python-jose` library
- [x] T011 Implement the MH authentication service to get and cache JWTs in `src/services/auth_service.py`
- [x] T012 Implement a resilient API client with retry logic for MH communication in `src/core/client.py`
- [ ] T013 [P] Define SQLAlchemy model for `Catalogo` in `src/models/db_models.py`
- [ ] T014 [P] Implement repository functions for `Catalogo` in `src/repositories/catalogo_repository.py`
- [ ] T015 Implement service to load and update MH catalogs in `src/services/catalogo_service.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Emisión de una Factura Electrónica (Priority: P1) 🎯 MVP

**Goal**: Implement the end-to-end flow for issuing a standard electronic invoice.
**Independent Test**: Generate a single invoice, transmit it to the MH test environment, and verify a valid `Sello de Recepción` is received and stored.

### Tests for User Story 1 ⚠️

- [x] T016 [P] [US1] Write contract test for `POST /dte` endpoint in `tests/contract/test_api.py`
- [x] T017 [P] [US1] Write integration test for the DTE issuance service in `tests/integration/test_dte_service.py`
- [x] T018 [P] [US1] Write unit test for DTE JSON payload generation in `tests/unit/test_generation.py`

### Implementation for User Story 1

- [x] T019 [P] [US1] Implement the `POST /dte` and `GET /dte/{codigo_generacion}` endpoints in `src/api/dte_router.py`
- [x] T020 [US1] Implement the main DTE orchestration logic in `src/services/dte_service.py` (generate, sign, transmit)
- [x] T021 [US1] Implement the repository function to save a new DTE and update it with the seal in `src/repositories/dte_repository.py`
- [x] T022 [US1] Implement a service to generate the PDF representation (`Versión Legible`) with a QR code in `src/services/pdf_service.py`

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Operación en Modo de Contingencia (Priority: P2)

**Goal**: Allow the system to continue operating when MH services are down.
**Independent Test**: Simulate an MH API failure, generate DTEs in contingency mode, then restore the connection and verify the contingency event is sent and processed.

### Tests for User Story 2 ⚠️

- [x] T023 [P] [US2] Write integration test for the contingency workflow in `tests/integration/test_contingency.py`

### Implementation for User Story 2

- [x] T024 [P] [US2] Add the `Evento` SQLAlchemy model to `src/models/db_models.py` and create a new migration
- [x] T025 [US2] Update `dte_service.py` to include the logic for detecting failures and saving DTEs with `CONTINGENCIA` status
- [x] T026 [US2] Create a new service `src/services/contingency_service.py` to handle the generation and transmission of the `Evento de Contingencia`
- [x] T027 [US2] Create a background job or scheduled task to process pending contingency events and DTEs

**Checkpoint**: User Stories 1 and 2 are functional.

---

## Phase 5: User Story 3 - Invalidación de un DTE (Priority: P3)

**Goal**: Allow users to annul an already issued DTE.
**Independent Test**: Issue a DTE, then use the invalidation endpoint and verify the DTE's status is updated to `INVALIDADO`.

### Tests for User Story 3 ⚠️

- [x] T028 [P] [US3] Write contract test for `POST /dte/{codigo_generacion}/invalidate` in `tests/contract/test_api.py`

### Implementation for User Story 3

- [x] T029 [P] [US3] Implement the `POST /dte/{codigo_generacion}/invalidate` endpoint in `src/api/dte_router.py`
- [x] T030 [US3] Implement the invalidation logic in `src/services/dte_service.py` to generate and transmit the `Evento de Invalidación`
- [x] T031 [US3] Update the DTE repository in `src/repositories/dte_repository.py` to handle the status change to `INVALIDADO`

**Checkpoint**: All user stories are now independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation.

- [x] T032 [P] Add comprehensive logging to all services and API endpoints
- [x] T033 [P] Review and add detailed docstrings to all public functions and classes
- [x] T034 Create a `README.md` at the project root with final setup and deployment instructions
- [x] T035 Validate the full `quickstart.md` guide from a clean environment

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** must be completed first.
- **Phase 2 (Foundational)** depends on Phase 1 and blocks all user stories.
- **User Stories (Phase 3-5)** can be implemented after Phase 2. While they can be developed in parallel by different teams, the recommended order for a single developer is P1 -> P2 -> P3.
- **Phase 6 (Polish)** should be done last.

## Implementation Strategy

1.  **MVP First**: Complete Phases 1, 2, and 3 to deliver a functional MVP capable of issuing valid invoices.
2.  **Incremental Delivery**: Add Phase 4 (Contingency) and Phase 5 (Invalidation) as subsequent releases.
3.  **TDD Approach**: For each story, write the failing tests in the `tests/` directory first, then implement the code in `src/` to make them pass.
