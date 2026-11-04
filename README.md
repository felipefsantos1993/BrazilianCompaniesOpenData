# Brazilian Companies Open Data Platform

[![Project Status](https://img.shields.io/badge/Status-In%20Development-orange)]()
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)]()
[![Microsoft Azure](https://img.shields.io/badge/Microsoft%20Azure-Cloud-0078D4?logo=microsoftazure)]()
[![Databricks](https://img.shields.io/badge/Azure-Databricks-FF3621?logo=databricks)]()
[![Delta Lake](https://img.shields.io/badge/Delta-Lake-00ADD8?logo=delta)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

An end-to-end Data Engineering platform designed to ingest, process, validate, and transform Brazilian company registration data published by the Brazilian Federal Revenue Service (Receita Federal do Brasil).

Built on Microsoft Azure and Azure Databricks, this project demonstrates modern Data Engineering practices through a scalable and reproducible Lakehouse architecture.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Business Context](#business-context)
- [Project Scope](#project-scope)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Data Sources](#data-sources)
- [Data Engineering Workflow](#data-engineering-workflow)
- [Medallion Architecture](#medallion-architecture)
- [Data Quality](#data-quality)
- [Orchestration](#orchestration)
- [Infrastructure as Code](#infrastructure-as-code)
- [CI/CD](#cicd)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Security and Configuration](#security-and-configuration)
- [Cost Considerations](#cost-considerations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

The Brazilian Companies Open Data Platform is an open-source Data Engineering project focused on building an end-to-end data processing solution using publicly available Brazilian company registration datasets.

The platform implements automated data ingestion, distributed processing, data quality validation, and centralized workflow orchestration.

The main objectives are:

- Automate the ingestion of public datasets from the Brazilian Federal Revenue Service.
- Store source files in Azure Data Lake Storage Gen2 (ADLS Gen2).
- Process large-scale datasets using Azure Databricks and Apache Spark.
- Implement the Medallion Architecture (Bronze, Silver, and Gold).
- Apply data quality rules using Lakeflow Declarative Pipelines.
- Orchestrate data workflows using Azure Data Factory.
- Apply Infrastructure as Code (IaC) and CI/CD best practices.
- Provide a reproducible implementation that other engineers can deploy in their own Azure environments.

This repository is also intended to serve as a practical reference for modern Data Engineering architectures and development practices.

## Business Context

The Brazilian Federal Revenue Service provides public datasets containing information about companies registered in Brazil.

These datasets contain valuable information that can be used to analyze the Brazilian business ecosystem, including company registrations, economic activities, and geographic distribution.

By applying modern cloud data engineering technologies, this project aims to transform raw public datasets into reliable, structured, and analytics-ready information.

Potential analytical use cases include:

- Company distribution by state and municipality.
- Company registrations over time.
- Company distribution by economic activity (CNAE).
- Active versus inactive companies.
- Company size distribution.
- Business ecosystem analysis.

## Project Scope

The project will be developed incrementally, starting with the Companies dataset.

The architecture is designed to support additional data domains in future development phases.

| Data Domain | Description | Status |
|---|---|---|
| Companies | Brazilian company registration information | Initial scope |
| Establishments | Company establishment information | Planned |
| Partners | Company ownership and partner information | Planned |
| Reference Data | CNAEs, municipalities, and other reference datasets | Planned |

The initial implementation focuses on establishing the ingestion framework, Lakehouse architecture, data quality standards, and orchestration strategy using the Companies dataset.

Once the initial pipeline is stable, additional data domains will be incorporated using the same architectural principles.

## Architecture

The platform follows a Lakehouse architecture based on the Medallion Architecture pattern.

Azure Data Factory acts as the central orchestration layer, coordinating the execution of Databricks ingestion and processing jobs.

### High-Level Architecture

![Brazilian Companies Open Data Platform - Architecture](docs/images/architecture.png)

*Figure 1 — High-level solution architecture.*

### Architecture Components

| Component | Responsibility |
|---|---|
| Azure Data Factory | Centralized workflow orchestration and execution control |
| Azure Databricks | Data ingestion and distributed data processing |
| Python | Data extraction, validation, and ingestion |
| Azure Data Lake Storage Gen2 | Data lake storage |
| Lakeflow Declarative Pipelines | Data transformation and pipeline management |
| Delta Lake | Transactional data storage |
| Terraform | Infrastructure provisioning |
| GitHub Actions | CI/CD automation |
| Unity Catalog | Data governance and catalog management |

## Technology Stack

The following technologies are part of the planned solution:

| Category | Technology |
|---|---|
| Cloud Platform | Microsoft Azure |
| Orchestration | Azure Data Factory |
| Data Storage | Azure Data Lake Storage Gen2 |
| Data Processing | Azure Databricks |
| Processing Framework | Apache Spark / PySpark |
| Pipeline Framework | Lakeflow Declarative Pipelines |
| Storage Format | Delta Lake |
| Programming Language | Python |
| Query Language | SQL |
| Infrastructure as Code | Terraform |
| Version Control | Git / GitHub |
| CI/CD | GitHub Actions |
| Data Governance | Unity Catalog |

## Data Sources

The project uses publicly available datasets from the Brazilian Federal Revenue Service.

**Official data source:**

[Receita Federal — Public CNPJ Data](https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/cadastro-nacional-de-pessoas-juridicas-cnpj/dados-publicos-cnpj)

### Initial Dataset

| Dataset | Description |
|---|---|
| Companies | Brazilian company registration information |

### Future Datasets

| Dataset | Description |
|---|---|
| Establishments | Company establishment information |
| Partners | Company ownership and partner information |
| CNAEs | Economic activity classifications |
| Municipalities | Brazilian municipality reference data |

Source files are downloaded directly from the official data provider and are not stored in this GitHub repository.

## Data Engineering Workflow

The solution is divided into two main Databricks jobs, orchestrated by Azure Data Factory.

### 1. Data Ingestion

A Python-based Databricks Job is responsible for:

- Retrieving source files from the official data provider.
- Downloading compressed datasets.
- Validating downloaded files.
- Calculating SHA-256 checksums.
- Uploading source files to Azure Data Lake Storage Gen2.
- Recording ingestion metadata and execution status.

### 2. Data Processing

A Databricks Lakeflow Declarative Pipeline processes the ingested datasets.

The initial implementation focuses on the Companies domain.

The processing pipeline is responsible for:

- Reading source data from the ADLS landing zone.
- Creating Bronze Delta tables.
- Applying data cleansing and standardization.
- Enforcing data quality expectations.
- Creating Silver Delta tables.
- Applying business transformations.
- Creating Gold analytical tables.

## Medallion Architecture

The platform uses three logical data layers.

### Bronze Layer

Stores ingested source data in Delta format.

Main characteristics:

- Preserve source information.
- Maintain ingestion metadata.
- Track source files.
- Support data traceability and reprocessing.

### Silver Layer

Stores cleansed, standardized, and validated datasets.

Main characteristics:

- Data type standardization.
- Null value handling.
- Duplicate identification.
- Business rule validation.
- Data quality expectations.

### Gold Layer

Stores curated datasets designed for analytical consumption.

Potential data models include:

- Company dimension.
- Company registration status.
- Company size classification.
- Economic activity analysis.
- Geographic company distribution.

## Data Quality

Data quality is implemented primarily in the Silver layer using Lakeflow Declarative Pipelines expectations.

Initial validation rules may include:

- Mandatory field validation.
- Valid company registration identifiers.
- Valid date formats.
- Business rule validation.
- Duplicate record detection.

Expectations will be configured according to the severity of each validation rule.

The solution will also provide mechanisms to monitor data quality violations and investigate rejected records.

## Orchestration

Azure Data Factory acts as the central controller of the platform.

The main orchestration workflow follows these steps:

1. Start pipeline execution.
2. Trigger the Databricks ingestion job.
3. Wait for ingestion completion.
4. Validate ingestion results.
5. Trigger the Databricks processing pipeline.
6. Monitor processing execution.
7. Record execution status.
8. Handle failures and notifications.

The orchestration layer is responsible for execution dependencies, retries, timeouts, and operational monitoring.

Business transformations and data processing logic remain within Azure Databricks.

## Infrastructure as Code

Terraform is used to provision and manage the Azure infrastructure.

The infrastructure definition is designed to support reproducible deployments across different environments.

Planned infrastructure components include:

- Azure Resource Group.
- Azure Storage Account.
- Azure Data Lake Storage Gen2.
- Azure Data Factory.
- Azure Databricks Workspace.
- Required access permissions and integrations.

## CI/CD

GitHub Actions is used to automate validation and deployment workflows.

The CI/CD implementation is designed to include:

- Python code quality checks.
- Automated unit tests.
- Configuration validation.
- Infrastructure validation.
- Databricks resource deployment.
- Automated deployment workflows.

Environment-specific configuration and credentials must be managed securely and must never be committed to the repository.

## Repository Structure

The repository is organized to separate ingestion, processing, infrastructure, testing, and documentation.

```text
BrazilianCompaniesOpenData/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── docs/
│   ├── images/
│   │   └── architecture.png
│   ├── architecture/
│   ├── decisions/
│   ├── data-governance/
│   └── operations/
│
├── src/
│   ├── ingestion/
│   ├── pipelines/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   └── common/
│
├── infrastructure/
│   └── terraform/
│
├── databricks/
│   ├── jobs/
│   ├── pipelines/
│   └── databricks.yml
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── data_quality/
│
└── .github/
    └── workflows/
```

## Getting Started

This project is designed to be reproducible by other engineers using their own Azure subscriptions and Databricks environments.

### Prerequisites

Before deploying the solution, the following tools and resources will be required:

- An active Microsoft Azure subscription.
- Azure Databricks workspace.
- Azure Data Factory.
- Azure CLI.
- Terraform.
- Python.
- Databricks CLI.
- Git.

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/BrazilianCompaniesOpenData.git

cd BrazilianCompaniesOpenData
```

### Configuration

Create your environment-specific configuration using the provided example configuration files.

Configure your own:

- Azure subscription.
- Resource group.
- Storage account.
- Databricks workspace.
- Databricks catalog.
- Authentication settings.

### Deployment

Detailed deployment instructions will be provided as the infrastructure and application components are implemented.

The intended deployment workflow is:

1. Clone the repository.
2. Configure Azure authentication.
3. Configure environment-specific variables.
4. Provision Azure resources using Terraform.
5. Deploy Databricks resources.
6. Publish Azure Data Factory pipelines.
7. Execute the main