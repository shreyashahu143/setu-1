# Product Requirements Document (PRD)

## 1. Executive Summary & Problem Statement

Interstate migrants relocating to regional economic hubs like Nagpur face a steep, unwritten "outsider tax." Moving from states such as Telangana, Kerala, or Tamil Nadu into Maharashtra involves cultural estrangement, lack of linguistic fluency, and zero visibility into hyper-local market conventions. Generic LLMs fail to bridge this gap: they hallucinate bureaucratic rules, miss unindexed street-level shopping lanes, and lack ground-truth price benchmarks.

**Setu** is an autonomous, hyper-local multi-agent system designed to decode street navigation, specialized retail lanes, colloquial dialect nuances, and negotiation tactics for newcomers.

## 2. Target Persona

- **Primary Persona:** Interstate migrant students, IT engineers, and corporate transferees (originating outside Maharashtra, particularly South India).
- **Key Pain Points:**
  - Fear of being overcharged by local auto-rickshaws and street vendors.
  - Inability to locate specialized traditional market alleys (e.g., electronic repairs vs. saree lanes).
  - Linguistic insecurity and misinterpreting aggressive street tone or colloquial slang.

## 3. Scope & Boundaries

- **In-Scope (Pilot Phase):**
  - Hyper-local market scouting in Nagpur (Sitabuldi, Itwari, Chitaroli, Dharampeth, Sadar, Gandhibagh).
  - Dialect translation and conversational street scripts (Nagpuri Varhadi / Marathi-Hindi blend).
  - Cultural survival etiquette (festival conduct, food spice warnings, shop timings).
  - On-demand web harvesting to expand the knowledge base on cache misses.
- **Out-of-Scope (Deferred):**
  - Formal tenancy court disputes and civil litigation workflows.
  - Integration with live RTO payment APIs or digital police filing portals.
  - Support for cities outside Nagpur during the pilot MVP.

## 4. Functional Requirements

- **FR1: Intent Routing:** Real-time classification of incoming user queries into market scouting, dialect guidance, or hybrid tasks within 300ms.
- **FR2: Hyper-Local Retrieval (RAG):** Deterministic retrieval of verified lane and pricing metadata from an embedded vector store.
- **FR3: Dialect Bridging:** Generation of spoken street scripts with phonetic guides and tone instructions tailored to the user's native state.
- **FR4: Self-Learning Harvester:** Automated fallback that searches local city forums and community discussions on a cache miss, parses entities using structured schemas, and auto-indexes the result (subject to the verification gate in design.md).
- **FR5: Response Synthesis:** Consolidation of geographic guidance, street phrasing, and warnings into a single structured response card.

## 5. Non-Functional Requirements

- **Latency:** End-to-end response time under 2.5 seconds on cached queries; under 8 seconds on live harvested queries.
- **Cost Efficiency:** Entire MVP must run within free-tier quotas (Groq API, Google AI Studio, DuckDuckGo Search, local ChromaDB).
- **Reliability:** Zero hallucinated lane names presented as confirmed fact; strict fallback to the Harvester or graceful degradation when confidence is low; unverified data always disclosed as such (see design.md §2).
