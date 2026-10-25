# DukanIQ Backend

A complete Python/FastAPI backend for the **DukanIQ Shop Management System** — designed for small retailers, shopkeepers, and vendors.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | **FastAPI** (async REST API) |
| Database | **SQLite** (dev) / PostgreSQL (prod) |
| ORM | **SQLAlchemy** |
| Auth | **JWT** via `python-jose` + `passlib/bcrypt` |
| Validation | **Pydantic v2** |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # FastAPI app factory + startup
│   ├── core/
│   │   ├── config.py        # Settings (env vars)
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   └── security.py      # JWT auth + RBAC dependencies
│   ├── models/
│   │   └── __init__.py      # All SQLAlchemy ORM models (16 tables)
│   ├── schemas/
│   │   └── __init__.py      # All Pydantic request/response schemas
│   ├── services/
│   │   └── __init__.py      # Business logic (atomic transactions)
│   └── api/
│       ├── __init__.py      # Main API router
│       └── v1/
│           └── endpoints/
│               ├── auth.py           # Register, login, profile
│               ├── products.py       # Products + categories CRUD
│               ├── suppliers.py      # Suppliers + ledger + payments
│               ├── purchases.py      # Purchase entry (atomic posting)
│               ├── sales.py          # Sale completion (FEFO + receipts)
│               ├── inventory.py      # Stock snapshot, batches, movements, adjustments, expiry
│               ├── damaged_goods.py  # Damage recording + status tracking
│               └── reports.py        # Dashboard, sales/purchase/inventory/profit reports
├── main.py                  # Uvicorn server entry point
├── seed.py                  # Demo data seeder
├── requirements.txt
└── .env                     # Environment variables
```

## Quick Start

### 1. Install dependencies
```powershell
py -m pip install -r requirements.txt
```

### 2. Run the server
```powershell
cd backend
py main.py
```

### 3. Seed demo data (optional)
```powershell
py seed.py
```

### 4. Open API docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Demo Credentials (after seeding)

| Role | Email | Password |
|---|---|---|
| Owner | owner@dukaniq.com | admin123 |
| Manager | manager@dukaniq.com | manager123 |
| Cashier | cashier@dukaniq.com | cashier123 |

## Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register new shop + owner |
| `POST` | `/api/v1/auth/login` | Login → JWT token |
| `GET` | `/api/v1/dashboard` | Dashboard KPI cards |
| `GET/POST` | `/api/v1/products` | Product catalogue |
| `GET/POST` | `/api/v1/suppliers` | Supplier directory |
| `GET` | `/api/v1/suppliers/{id}/ledger` | Supplier balance ledger |
| `POST` | `/api/v1/purchases` | Create + post purchase (atomic) |
| `POST` | `/api/v1/sales` | Complete a sale (FEFO + receipts) |
| `GET` | `/api/v1/inventory` | Stock snapshot |
| `GET` | `/api/v1/inventory/expiry` | Expiry monitoring |
| `POST` | `/api/v1/inventory/adjustments` | Stock adjustment |
| `POST` | `/api/v1/damaged-goods` | Record damage (atomic) |
| `GET` | `/api/v1/reports/sales` | Sales report |
| `GET` | `/api/v1/reports/gross-profit` | Gross profit (COGS-based) |
| `GET` | `/api/v1/notifications` | In-app notifications |
| `GET` | `/api/v1/audit-logs` | Audit trail (owner only) |

## Business Rules Implemented

- ✅ **Atomic transactions** — purchase posting, sale completion, damage recording all use DB transactions
- ✅ **FEFO** — sales allocate from earliest-expiry batches first
- ✅ **Expired stock blocked** — expired batches cannot be sold by default
- ✅ **Negative stock prevention** — sales validate available stock
- ✅ **Role-based access** — Owner > Manager > Cashier > Inventory Staff
- ✅ **Audit logging** — all sensitive operations logged with actor + timestamp
- ✅ **Stock movements ledger** — every inventory change is traceable
- ✅ **Supplier ledger** — balances derived from posted invoices + payments
- ✅ **COGS-based gross profit** — uses unit_cost_snapshot at time of sale
- ✅ **Soft delete** — products deactivated, not deleted
- ✅ **Notifications** — low stock, expiry, damage alerts

## Production Notes

- Switch `DATABASE_URL` in `.env` to a PostgreSQL connection string
- Change `SECRET_KEY` to a secure random value
- Set `DEBUG=false`
- Use proper CORS origins instead of `"*"`
