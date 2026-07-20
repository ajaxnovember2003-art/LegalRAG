# LegalRAG Development Log

## Project Title

Temporally-Aware Multi-Hop Retrieval-Augmented Generation Framework with Citation Verification for Indian Legal Question Answering


# Week 1


## Day 1 - Project Planning

Date:

Objectives:
- Finalize project idea and research direction.
- Identify limitations in existing Indian legal RAG systems.
- Define the three major research contributions.

Completed:
- Studied existing legal AI systems.
- Identified research gaps:
  1. Temporal validity checking of legal provisions.
  2. Multi-hop retrieval across statutes, judgments, and amendments.
  3. Citation verification for generated responses.


---

## Day 2 - Environment and Project Setup

Objectives:
- Prepare development environment.
- Create initial project architecture.

Completed:
- Created LegalRAG project structure.
- Created Python virtual environment.
- Installed required backend dependencies.
- Planned modules for:
  - Retrieval system
  - Temporal validation
  - Citation verification
  - Evaluation


---

## Day 3 - Backend and Frontend Prototype

Objectives:
- Build the initial working application.

Completed:
- Implemented FastAPI backend.
- Created API health endpoint.
- Implemented Streamlit frontend.
- Connected frontend with backend.
- Tested communication between UI and API.
- Initialized Git repository.
- Added version control.

Current Architecture:

User
 |
Streamlit Frontend
 |
FastAPI Backend
 |
API Response


---

## Day 4 - System Design and API Planning

Objectives:
- Convert project idea into a structured software system.
- Design future API architecture.

Completed:
- Defined functional requirements.
- Defined non-functional requirements.
- Designed API structure.

Planned API:

GET /
- Checks backend availability.

POST /ask
- Accepts legal questions.
- Retrieves relevant legal information.
- Generates verified responses.


Planned Processing Pipeline:

User Query

↓

Query Processing

↓

Legal Document Retrieval

↓

Multi-Hop Reasoning

↓

Temporal Validation

↓

Citation Verification

↓

Final Response


---

# Future Development Notes

Upcoming modules:

1. Document Processing Module
2. Embedding Generation Module
3. Vector Database Integration
4. Retrieval Pipeline
5. LLM Response Generation
6. Temporal Validation Engine
7. Citation Verification Engine
8. Evaluation Framework