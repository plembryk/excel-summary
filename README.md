# Excel Summary API

**Excel Summary API** is a Django-based service that allows processing Excel (`.xlsx`) files and generating column summaries of numeric data. The project uses Docker and Poetry for dependency and environment management.

---

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Setup](#setup)
- [API](#api)
- [Tests](#tests)
- [Assumptions](#assumptions)

---

## Features

- Process Excel `.xlsx` files.
- Extract data from specified columns.
- Generate column summaries: sum and average for numeric data.
- Error handling for invalid files or missing columns.
- Fully covered unit tests using `pytest`.
- Fully typed, passes `mypy` checks

---

## Technologies

- **Python 3.12**
- **Django 5.2.6**
- **Django REST Framework 3.16.1**
- **OpenPyXL 3.1.5** (Excel processing)
- **Poetry 1.8.4** (dependency management)
- **Docker & Docker Compose** (containerization)
- **Ruff, MyPy, pytest** (linting, type checking, testing)

---

## Setup

### Requirements

- Docker 27.3.1
- Docker Compose 2.29.7

### Run the service

1. Clone the repository:

```bash
git clone https://github.com/plembryk/excel-summary
cd excel-summary
```

2. Build and start the Docker container:

```bash
docker-compose up --build
```

3. The Django server will be available at:

```
http://localhost:8000/
```

---

## API
This project provides automatically generated API documentation using **drf-spectacular**.

### Available Endpoints

- **Schema (OpenAPI 3.0):**
  - `GET /api/schema/`
  - Returns the OpenAPI schema in JSON format.

- **Interactive Swagger UI:**
  - `GET /api/docs/`
  - Provides an interactive documentation interface where you can explore and test all available endpoints.

### Notes
- The schema is generated automatically from DRF views and serializers.
- The Swagger UI can be used to quickly verify request/response formats and test the API without external tools.

### Endpoint: `POST /api/v1/excel-summary/`

Accepts an Excel file and a list of column names to generate a summary.

#### Request

| Field         | Type         | Description                  |
|---------------|-------------|------------------------------|
| `file`        | File        | Excel `.xlsx` file           |
| `column_names`| List[str]   | List of column names         |

Example (multipart/form-data):

```json
{
  "file": "<file.xlsx>",
  "column_names": ["Column1", "Column2"]
}
```

Example (curl)

```
curl -X POST http://127.0.0.1:8000/api/v1/excel-summary/ \
  -F "file=@{path_to_file}" \
  -F 'column_names={column_name_1}' \
  -F 'column_names={column_name_2}' \
  -H "Content-Type: multipart/form-data"

```

#### Response (200 OK)

```json
{
  "file": "file.xlsx",
  "summary": [
    {"column": "Column1", "sum": "123", "avg": "41"},
    {"column": "Column2", "sum": "456", "avg": "152"}
  ]
}
```

#### Errors

- **400 Bad Request** – missing required column or invalid file.  
- **500 Internal Server Error** – unexpected processing error.

---

## Tests

The project uses `pytest`.

Run tests using:

```bash
poetry install
pytest
```

Tests include:

- Processing a single data row.
- Processing multiple data rows.
- Handling missing or unprocessable values.
- Validation errors (e.g., column not found).

---


## Assumptions
- To ensure correct functionality, each column name and its corresponding values should be located in the same column in the Excel file.
- If a column name appears in merged cell, the program may not work correctly.
- To ensure a row is processed correctly, each processed column in that row must contain a value that can be processed.
- If no row is processed, the value "N/A" will be returned for both sum and average.
If at least one value cannot be converted to a `Decimal`, the entire row will not be processed.
**Example:** The row `[1, None, 2]` will not be processed because `None` cannot be converted to a `Decimal`.


