# FinFlow — Financial Services Data Platform

FinFlow is an end-to-end **financial services data engineering project** designed to simulate how customer, account, transaction, card, transfer, and loan data can be ingested, transformed, validated, secured, and modeled for analytics.

The project focuses on building a reliable analytical data platform using **PostgreSQL, Snowflake, dbt, Python, and SQL**, with particular attention to data quality, historical tracking, dimensional modeling, data governance, and security.

---

## Architecture

```text
                    ┌──────────────────────┐
                    │   Python Data        │
                    │   Generation         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    PostgreSQL        │
                    │  Operational Source  │
                    └──────────┬───────────┘
                               │
                         Data Ingestion
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Snowflake       │
                    │                      │
                    │    Bronze Layer      │
                    └──────────┬───────────┘
                               │
                       Streams + Tasks
                               │
                               ▼
                    ┌──────────────────────┐
                    │        dbt           │
                    │                      │
                    │   Silver Layer       │
                    │   Gold Layer         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Analytical Models  │
                    │                      │
                    │ Dimensions + Facts   │
                    └──────────────────────┘
```

The pipeline separates operational data from analytical transformations and provides distinct layers for ingestion, cleansing, validation, and analytics.

---

# Project Objectives

The main objectives of FinFlow were to build a financial data platform that demonstrates:

* End-to-end data generation and ingestion
* Relational operational data modeling
* Snowflake data warehousing
* Bronze, Silver, and Gold data layers
* Incremental data processing
* Change tracking using Snowflake Streams and Tasks
* Data cleansing and standardization
* Data quality testing
* Failed-record storage and quarantine
* Historical customer tracking with dbt snapshots
* Dimensional modeling
* Surrogate key generation
* Data documentation
* Data governance and security
* Sensitive-data protection using Snowflake Dynamic Data Masking

---

# Technology Stack

| Technology                         | Purpose                                                  |
| ---------------------------------- | -------------------------------------------------------- |
| **Python**                         | Data generation and ingestion                            |
| **PostgreSQL**                     | Operational/source database                              |
| **Snowflake**                      | Cloud data warehouse and data processing                 |
| **dbt**                            | SQL transformation, testing, documentation, and modeling |
| **SQL**                            | Data transformation and validation                       |
| **dbt-utils**                      | Surrogate key generation                                 |
| **Snowflake Streams**              | Change data tracking                                     |
| **Snowflake Tasks**                | Automated processing of changes                          |
| **Snowflake Dynamic Data Masking** | Protection of sensitive information                      |
| **Git/GitHub**                     | Version control and project management                   |

---

# Data Domain

FinFlow models a financial services environment containing the following core entities:

```text
Customers
   │
   ├── Accounts
   │      │
   │      ├── Transactions
   │      ├── Cards
   │      │      └── Card Transactions
   │      ├── Transfers
   │      └── Loans
   │             └── Loan Payments
   │
   └── Beneficiaries
```

The data model contains:

* Customers
* Accounts
* Beneficiaries
* Transactions
* Transfers
* Cards
* Card transactions
* Loans
* Loan payments

All financial data is modeled using **NGN (Nigerian Naira)**.

---

# Data Pipeline

## 1. Data Generation

I wrote the Python code responsible for generating the FinFlow operational data.

The generated data represents realistic financial entities and relationships rather than a single flat dataset.

The source system contains records for:

* Customers
* Accounts
* Beneficiaries
* Transactions
* Transfers
* Cards
* Card transactions
* Loans
* Loan payments

The generated data also includes intentionally introduced data-quality issues so that the pipeline can demonstrate real-world cleansing and validation scenarios.

---

## 2. Data Ingestion

I also wrote the ingestion code responsible for moving the generated operational data into the analytical platform.

The operational data originates in **PostgreSQL** and is ingested into Snowflake.

The ingestion architecture separates the source/operational environment from the analytical warehouse.

```text
PostgreSQL
     │
     │ Ingestion
     ▼
Snowflake Bronze
```

The Snowflake Bronze layer acts as the starting point for downstream transformations.

---

# Snowflake Bronze Layer

The Bronze layer contains the ingested source data from the operational system.

The main Bronze tables are:

```text
bronze_customers
bronze_accounts
bronze_beneficiaries
bronze_transactions
bronze_transfers
bronze_cards
bronze_card_transactions
bronze_loans
bronze_loan_payments
```

dbt sources are configured to reference these Snowflake Bronze tables:

```yaml
sources:
  - name: finflow_bronze_src
    database: FINFLOW_DB
    schema: FINFLOW_BRONZE
```

This allows the transformation layer to explicitly define its dependency on the Bronze source system.

---

# Incremental Processing with Snowflake Streams and Tasks

Snowflake Streams and Tasks are used to track and process changes in the Bronze layer.

The project includes change tracking for key entities such as:

* Customers
* Accounts

The Streams capture changes occurring in the source data, while Tasks provide automated processing of those changes.

This allows the warehouse to respond to newly ingested or modified records without requiring the entire dataset to be processed from scratch.

---

# dbt Transformation Layer

The transformation layer is implemented using **dbt**.

The dbt project separates transformations into:

```text
Bronze
   ↓
Silver
   ↓
Gold
```

The Bronze layer remains the source of the transformation pipeline, while the Silver and Gold layers are materialized as tables in separate Snowflake schemas.

---

# Silver Layer

The Silver layer is responsible for **cleansing, standardization, validation, and preparation of source data for analytical modeling**.

All Silver models are materialized as tables in the `silver_layer` schema.

```yaml
silver_layer:
  +materialized: table
  +schema: silver_layer
```

## Silver Models

### `silver_customers`

Performs operations such as:

* Text standardization
* Whitespace trimming
* Gender standardization
* Country standardization
* Address handling
* Date casting
* Duplicate email detection
* Duplicate phone-number detection
* Customer status validation

For example:

```sql
{{ clean_strings('first_name') }}
```

is used to standardize text values.

Customer records are also validated to ensure that email addresses and phone numbers are not duplicated.

---

### `silver_accounts`

Performs:

* Account type standardization
* Currency normalization
* Account status standardization
* Account validation
* Balance validation
* Account date validation

The project also validates relationships between accounts and customers.

---

### `silver_beneficiaries`

Standardizes beneficiary information and validates:

* Beneficiary identifiers
* Customer relationships
* Beneficiary accounts
* Bank names
* Beneficiary status

---

### `silver_transactions`

Handles transaction cleansing and validation including:

* Transaction type standardization
* Transaction status standardization
* Transaction direction standardization
* Currency normalization
* Transaction channel handling
* Missing descriptions
* Transaction amount validation
* Transaction reference validation
* Transaction timestamp validation

The model also identifies duplicate transaction references.

---

### `silver_transfers`

Transforms transfer records and standardizes transfer methods.

The model also links transfer records to their corresponding transaction records.

---

### `silver_cards`

Cleans and standardizes card information including:

* Card type
* Card status
* Card identifiers
* Account relationships
* Customer relationships
* Issue dates
* Expiration dates

---

### `silver_card_transactions`

Connects card transactions to:

* Cards
* Financial transactions

It also standardizes merchant categories and validates transaction relationships.

---

### `silver_loans`

Cleans and validates loan information including:

* Loan type
* Loan status
* Principal amount
* Interest rate
* Total repayable amount
* Outstanding balance
* Loan term
* Approval date
* Disbursement date
* Maturity date

---

### `silver_loan_payments`

Transforms loan payment records and validates their relationships with:

* Loans
* Transactions

It also validates payment amounts, payment status, and payment timestamps.

---

# Gold Layer

The Gold layer contains analytical models designed around **dimensions and facts**.

All Gold models are materialized as tables in a separate `gold_layer` schema.

```yaml
gold_layer:
  +materialized: table
  +schema: gold_layer
```

The Gold layer transforms the cleansed Silver data into an analytical model.

---

# Dimension Models

The project contains the following dimensions:

```text
dim_customers
dim_accounts
dim_beneficiaries
dim_cards
dim_loans
```

## Customer Surrogate Key

The customer dimension uses `dbt_utils.generate_surrogate_key()` to create a warehouse-specific surrogate key.

```sql
{{ dbt_utils.generate_surrogate_key(['customer_id']) }} 
    as customer_key
```

The original `customer_id` is retained alongside the surrogate key for source-system traceability.

The surrogate key is then used when connecting customer information to downstream analytical fact models.

---

# Fact Models

The Gold layer contains fact models for different financial activities:

```text
fact_transactions
fact_transfers
fact_card_transactions
fact_loan_payments
```

## `fact_transactions`

Contains transaction-level financial activity.

The model captures attributes such as:

* Transaction
* Account
* Transaction type
* Transaction status
* Transaction direction
* Amount
* Currency
* Channel
* Description
* Transaction timestamps

---

## `fact_transfers`

Models transfer activity and connects transfers to their underlying transaction records.

It captures:

* Transfer
* Transfer reference
* Sender transaction
* Receiver transaction
* Beneficiary
* Sender account
* Transfer amount
* Transaction timestamp

---

## `fact_card_transactions`

Models transactions performed using cards.

It connects:

```text
Card Transaction
      ↓
Card
      ↓
Account
      ↓
Customer
      ↓
Transaction
```

---

## `fact_loan_payments`

Models loan repayment activity by connecting:

```text
Loan Payment
      ↓
Loan
      ↓
Account
      ↓
Customer
      ↓
Transaction
```

This allows loan repayment activity to be analyzed alongside customer and account information.

---

# Data Quality

Data quality is treated as a core part of the pipeline rather than an afterthought.

The project uses **dbt data tests** to validate the transformed data.

Tests cover areas including:

* `not_null`
* `unique`
* `accepted_values`
* `relationships`
* Custom SQL tests
* Business-rule validation

For example, customer identifiers are tested for both:

```yaml
- not_null
- unique
```

Relationship tests are also used to ensure that foreign-key relationships are valid.

For example:

```text
silver_accounts.customer_id
        ↓
silver_customers.customer_id
```

---

# Custom Data Tests

In addition to standard dbt tests, custom SQL tests were created for business-specific rules.

Examples include:

### Invalid Account Closure Dates

Checks whether an account was closed before it was opened.

### Invalid Card Account Numbers

Checks card-number length.

### Invalid Fee Transactions

Checks that fee transactions contain the transaction they are associated with.

### Invalid Reversal Transactions

Checks that reversal transactions contain their original transaction reference.

### Invalid Transfers

Checks whether transfer records have corresponding transaction records.

### Invalid Loan Amounts

Checks whether:

```text
principal_amount > total_repayable_amount
```

and whether loan approval occurs after disbursement.

### Invalid Transaction Dates

Checks whether a transaction event occurs after the record was created.

---

# Failed Test Records

Failed dbt tests are stored instead of simply disappearing after the test run.

The project configures:

```yaml
data_tests:
  finflow_dbt:
    +store_failures: true
    +schema: test_failures
```

This creates a dedicated:

```text
test_failures
```

schema for failed test records.

This provides a persistent location for investigating data-quality failures.

---

# Data Quarantine

The project also contains a dedicated `quarantine` layer for records that violate important business rules.

Examples include:

```text
duplicate_transaction_reference
duplicated_emails_and_phone_numbers
negative_balance_and_data_issue
```

These models identify problematic records and provide a `data_quality_issue` field describing the detected problem.

This creates a separation between:

```text
Valid analytical data
        │
        └──► Gold

Problematic records
        │
        └──► Quarantine
```

---

# Historical Data Tracking with dbt Snapshots

The project uses a dbt snapshot to preserve changes to customer records.

```yaml
snapshots:
  - name: customer_snapshot
    relation: source('finflow_bronze_src', 'bronze_customers')
    config:
      unique_key: customer_id
      strategy: check
      check_cols:
        - last_name
        - email
        - phone_number
        - state
        - city
        - address
        - updated_at
      hard_deletes: invalidate
```

The snapshot tracks changes to selected customer attributes.

This means that when a customer's tracked information changes, the previous state can be preserved rather than simply overwritten.

The snapshot therefore provides a historical record of customer changes.

---

# Important Data Architecture Distinction

The project separates **change tracking** from **analytical transformation**.

Snowflake Streams and Tasks are responsible for processing changes in the warehouse ingestion layer.

The dbt snapshot is responsible for maintaining historical versions of tracked customer records.

The Silver and Gold models are then built from their configured sources and references.

This separation keeps ingestion, historical tracking, transformation, and analytical modeling as distinct responsibilities within the architecture.

---

# Reusable dbt Macros

The project contains custom dbt macros to reduce repetitive SQL logic.

## `clean_strings`

The `clean_strings` macro standardizes text values by:

* Trimming whitespace
* Replacing underscores with spaces
* Applying capitalization

Example:

```sql
{{ clean_strings('account_type') }}
```

This allows the same cleansing logic to be reused across multiple models.

---

## `generate_schema_name`

A custom `generate_schema_name` macro is used to control how dbt schemas are generated.

It allows explicitly configured schemas to be used instead of automatically appending the target schema.

---

# Documentation

The dbt project includes model and column documentation through YAML configuration and dbt documentation blocks.

For example:

```sql
{% docs created_at %}
    The date and time when each customer account was created.
{% enddocs %}
```

These documentation blocks are referenced from model metadata.

The source configuration also documents the Bronze tables and their columns.

This makes the transformation layer easier to understand and trace back to the source system.

---

# Data Governance & Security

Security and governance were incorporated directly into the warehouse design.

## Dynamic Data Masking

Snowflake **Dynamic Data Masking** was implemented to protect sensitive customer information.

Sensitive fields include information such as:

* Customer email
* Phone number
* Address
* Account number
* Card number

The masking policies prevent sensitive information from being unnecessarily exposed within the warehouse.

This demonstrates an important data-governance principle:

> Data should be accessible according to the sensitivity of the information and the user's required level of access.

---

# Environment Variable Security

Sensitive project configuration is not hard-coded into the dbt project.

For example, personal/profile information is supplied through environment variables rather than directly committing sensitive values to the repository.

The local environment contains the actual values while the project references the variable names.

This reduces the risk of accidentally exposing sensitive configuration through version control.

---

# Project Structure

A simplified structure of the project is:

```text
finflow/
│
├── models/
│   ├── silver_layer/
│   │   ├── silver_customers.sql
│   │   ├── silver_accounts.sql
│   │   ├── silver_beneficiaries.sql
│   │   ├── silver_transactions.sql
│   │   ├── silver_transfers.sql
│   │   ├── silver_cards.sql
│   │   ├── silver_card_transactions.sql
│   │   ├── silver_loans.sql
│   │   ├── silver_loan_payments.sql
│   │   └── silver_properties.yml
│   │
│   ├── gold_layer/
│   │   ├── dim_customers.sql
│   │   ├── dim_accounts.sql
│   │   ├── dim_beneficiaries.sql
│   │   ├── dim_cards.sql
│   │   ├── dim_loans.sql
│   │   ├── fact_transactions.sql
│   │   ├── fact_transfers.sql
│   │   ├── fact_card_transactions.sql
│   │   ├── fact_loan_payments.sql
│   │   └── gold_properties.yml
│   │
│   └── quarantine/
│       ├── duplicate_transaction_reference.sql
│       ├── duplicated_emails_and_phone_num.sql
│       └── negative_balance_and_data_issue.sql
│
├── snapshots/
│   └── snapshot.yml
│
├── macros/
│   ├── clean_strings.sql
│   └── generate_schema_name.sql
│
├── tests/
│   ├── invalid_closed_date.sql
│   ├── test_card_acct_num_length.sql
│   ├── test_for_fee_transaction_id_is_null.sql
│   ├── test_for_reversal_and_transaction_id_is_null.sql
│   ├── test_for_transfers_not_in_transactions.sql
│   ├── test_loan_amt_grtr_than_repayable_amt.sql
│   └── transaction_date_grtr_than_created_date.sql
│
├── models/
│   └── sources.yml
│
├── docs/
│   └── column_description.md
│
├── images/
│   ├── masking-policy
│   ├── customer-streams-and-tasks
│   ├── account-streams-and-tasks
│   └── data-lineage
│
└── dbt_project.yml
```

---

# Key Engineering Concepts Demonstrated

This project allowed me to work with several important Data Engineering concepts:

### Data Ingestion

Building the code responsible for moving operational data into the warehouse.

### Data Warehousing

Designing a layered Snowflake architecture with Bronze, Silver, and Gold schemas.

### ETL / ELT

Separating ingestion from warehouse-based transformations using dbt.

### Data Transformation

Cleaning and standardizing raw operational data using SQL and reusable dbt macros.

### Dimensional Modeling

Building analytical dimensions and fact tables.

### Surrogate Keys

Generating stable warehouse keys using `dbt_utils.generate_surrogate_key`.

### Incremental Change Processing

Using Snowflake Streams and Tasks to process warehouse changes.

### Historical Data

Using dbt snapshots to preserve changes to customer records.

### Data Quality

Combining standard dbt tests with custom SQL business-rule tests.

### Data Quarantine

Separating problematic records for investigation.

### Data Governance

Documenting data models, sources, columns, and data-quality rules.

### Data Security

Using Snowflake Dynamic Data Masking to protect sensitive information.

### Secret Management

Using environment variables rather than hard-coding sensitive configuration.

---

# What I Built

This project was built end-to-end rather than using a pre-existing dataset or pipeline.

I developed:

* The synthetic financial data generation process
* The operational data structure
* The data ingestion process
* Snowflake Bronze-layer architecture
* Snowflake Streams and Tasks
* dbt Silver transformations
* dbt Gold dimensional models
* dbt snapshots
* dbt macros
* dbt source definitions
* dbt data tests
* Custom SQL business-rule tests
* Data quarantine models
* Failed-test storage
* Surrogate-key generation
* Data documentation
* Snowflake masking policies
* Environment-variable-based configuration

The project therefore covers the flow from **source data generation through ingestion, transformation, validation, historical tracking, security, and analytical modeling**.

---

# Project Outcome

FinFlow demonstrates how a financial services data platform can be structured so that operational data is transformed into reliable analytical datasets while maintaining:

* Data quality
* Traceability
* Historical information
* Security
* Documentation
* Separation of responsibilities
* Analytical usability

The final architecture provides a clear path from operational financial records to trusted analytical dimensions and facts.

---

## Core Technologies

**Python · PostgreSQL · Snowflake · SQL · dbt · dbt-utils · Snowflake Streams · Snowflake Tasks · Dynamic Data Masking · Git**
