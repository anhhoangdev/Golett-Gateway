# 🗿 Golett Gateway: Your BI Insights Portal

**Golett Gateway: Unearthing Insights with Your Autonomous BI Agent Crew!**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://example.com/build) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![crewAI](https://img.shields.io/badge/powered_by-crewAI-blue)](https://github.com/joaomdmoura/crewAI)

Welcome, Data Trainer! **Golett Gateway** is your access point to a powerful system of **Agentic Business Intelligence (BI) Agents**. Built on the `crewAI` framework, this system allows you to pose business questions in plain language and receive insightful answers, all orchestrated by a dedicated crew of AI agents.

Think of each 'Golett' in your crew as a specialized data assistant: one might be a **Query Golett** digging into databases, another a **Processor Golett** sifting through the findings, and a **Reporter Golett** presenting clear insights. The Gateway is where you issue your 'research quests' and receive their distilled wisdom.

---

## ✨ Features

* **Natural Language Querying:** Ask complex business questions in everyday language.
* **Automated Data Retrieval:** Agents autonomously generate and execute queries (e.g., SQL, API calls) against your configured data sources.
* **Intelligent Data Processing:** Agents can clean, transform, aggregate, and analyze retrieved data.
* **Insight Generation & Summarization:** AI crews collaborate to synthesize findings into understandable reports, visualizations, or direct answers.
* **`crewAI` Powered Collaboration:** Leverages `crewAI` for robust teamwork between specialized BI agents (e.g., Query Agent, Analysis Agent, Reporting Agent).
* **Data Source Connectivity:** Designed to be adaptable to various data sources (databases, APIs, CSV files, etc.).
* **Extensible Agent Skills:** Easily equip your Golett agents with new tools and capabilities for diverse BI tasks.

---

## 🧱 System Overview

Golett Gateway orchestrates a flow for answering your BI questions:

1.  **User Question:** The "Trainer" poses a business question through the Gateway.
2.  **Agent Crew Activation:** A specialized `crewAI` team is activated.
    * **Understanding Agent:** Interprets the natural language question.
    * **Query Planning Agent:** Determines what data is needed and how to get it.
    * **Data Retrieval Agent (Query Golett):** Connects to data sources and executes queries.
    * **Data Processing Agent (Processor Golett):** Cleans, analyzes, and aggregates the data.
    * **Insight Formulation Agent (Reporter Golett):** Synthesizes the information into a coherent answer.
3.  **Data Interaction:** Agents interact with configured databases, APIs, or files.
4.  **Answer Delivery:** The Gateway presents the processed information and insights back to the user.
