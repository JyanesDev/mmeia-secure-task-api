# 🔐 Secure Task API

![Category](https://img.shields.io/badge/MMEIA-02_API-6f42c1)
![Python](https://img.shields.io/badge/Python-FastAPI-blue)
![Security](https://img.shields.io/badge/security-JWT%20%2B%20ownership-critical)
![Status](https://img.shields.io/badge/status-M0--M3%20complete-success)

A task-management API built as the **second MMEIA Reference Project**, focused on authentication, authorization and secure ownership rules rather than CRUD alone.

## 📍 Portfolio Position

| Field | Value |
|---|---|
| **Collection** | MMEIA Reference Projects |
| **Reference** | `02_API` |
| **Category** | Secure backend API |
| **Domain** | Users and tasks |
| **Engineering focus** | Authentication, authorization and security verification |

## 🎯 What This Project Demonstrates

- User registration and login
- JWT access tokens and refresh tokens
- Owner-based authorization for task operations
- Explicit `401`, `403` and `404` behaviour
- Expired access-token handling
- PostgreSQL constraints and soft delete
- API contracts before implementation
- Automated tests against real PostgreSQL
- Docker deployment and CI pipeline structure

The central security lesson is simple: **authentication proves who you are; authorization decides what you are allowed to do**.

## 🛠 Tech Stack

| Area | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2 |
| Validation | Pydantic |
| Authentication | PyJWT |
| Password hashing | bcrypt |
| Tests | Pytest + HTTPX |
| Deployment | Docker + Docker Compose |
| CI | GitHub Actions |

## 🧭 Engineering Approach

This project follows the MMEIA sequence:

```text
specification
   ↓
database design
   ↓
API contract
   ↓
JWT + ownership implementation
   ↓
automated verification
   ↓
Docker deployment
```

`spec.md`, `requirements.md` and `tasks.md` are treated as engineering inputs, not documentation written after the implementation.

## ✅ Current Status

| Milestone | State | Evidence |
|---|---|---|
| M0 — Scaffold | ✅ Complete | Spec, requirements and tasks versioned from the start |
| M1 — Database | ✅ Complete | PostgreSQL 16 constraint verification |
| M2 — Secure API | ✅ Complete | 36 Pytest tests + 12-scenario real-server smoke test |
| M3 — Deployment | ✅ Complete | Docker Compose + 5-point deployment verification |
| M4 — Formal freeze | ⏳ Pending | Final review, reference commit and `v1.0.0` |

## 📂 Repository Structure

```text
.
├── spec.md
├── requirements.md
├── tasks.md
├── disenio.md
├── despliegue.md
├── api/
├── db/
├── docs/
├── src/
├── tests/
├── docker/
├── .env.example
└── .github/workflows/
```

## 📚 Key Documentation

| Document | Purpose |
|---|---|
| [`spec.md`](spec.md) | Exact feature behaviour and scope |
| [`requirements.md`](requirements.md) | Functional and non-functional requirements |
| [`tasks.md`](tasks.md) | Milestones and verified progress |
| [`disenio.md`](disenio.md) | Database design |
| [`api/contrato.md`](api/contrato.md) | API contracts |
| [`api/VERIFICATION.md`](api/VERIFICATION.md) | API verification evidence |
| [`db/VERIFICATION.md`](db/VERIFICATION.md) | Database constraint evidence |
| [`docs/decisions.md`](docs/decisions.md) | Security and architecture decisions |
| [`docs/deployment.md`](docs/deployment.md) | Real deployment verification |

## 💡 How to Use This Repository

Use this project as a reference for the difference between a normal CRUD API and an API where **identity, ownership and failure semantics are part of the specification**.

## 🧭 MMEIA Reference Projects

| # | Category | Repository |
|---|---|---|
| 01 | 🗃️ CRUD | [mmeia-crud-product-management](https://github.com/JyanesDev/mmeia-crud-product-management) |
| 02 | 🔐 Secure API | **mmeia-secure-task-api** |
| 03 | 🏢 SaaS | [mmeia-multitenant-workspaces](https://github.com/JyanesDev/mmeia-multitenant-workspaces) |
| 04 | 🔌 MCP | [mmeia-notes-mcp-server](https://github.com/JyanesDev/mmeia-notes-mcp-server) |
| 05 | 🤖 RAG | [mmeia-support-rag](https://github.com/JyanesDev/mmeia-support-rag) |

## 👨‍💻 Author

**Jonay Yanes** — [GitHub profile](https://github.com/JyanesDev)
