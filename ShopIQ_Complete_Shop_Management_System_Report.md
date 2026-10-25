# ShopIQ — Shop Management System
## Complete Functional & Technical Report

**Document version:** 1.0  
**Date:** 25 October 2026  
**Purpose:** Product and development blueprint

> This report describes the proposed ShopIQ system. It is a specification, not a claim that the software has already been implemented or deployed.

---

## Document Overview

| Item | Description |
|---|---|
| Product | ShopIQ — Shop Management System |
| Primary users | Small shopkeepers, local retailers, vendors, owners, managers, cashiers, and inventory staff |
| Primary objective | Centralize daily shop operations and maintain accurate, traceable business records |
| Delivery model | Responsive web application designed for future multi-shop support |
| Core areas | Dashboard, products, inventory, purchases, sales, suppliers, expiry, damaged goods, reports, and settings |

## Contents

1. Executive Summary
2. Problem Statement and Objectives
3. Scope and User Roles
4. Application Navigation and Dashboard
5. Functional Modules
6. End-to-End Workflows
7. Business Rules and Calculations
8. Data Model and Relationships
9. Technical Architecture
10. Security, Reliability, and Auditability
11. Reports and Notifications
12. User Interface Guidelines
13. Non-Functional Requirements
14. Implementation Roadmap
15. Acceptance Criteria
16. Risks and Mitigations
17. Future Enhancements
18. Conclusion

---

## 1. Executive Summary

ShopIQ is a web-based shop management system intended to help small retailers replace fragmented paper registers and spreadsheets with one organized application. A main dashboard provides access to each business function and highlights daily indicators such as sales, purchases, current stock value, low-stock products, expiring batches, expired products, damaged goods, and supplier balances.

The system is designed around traceable transactions. A confirmed purchase increases the appropriate inventory batches; a completed sale reduces stock; damage and expiry write-offs reduce saleable stock; and every movement is recorded in a stock ledger. This helps the shopkeeper investigate discrepancies and understand how stock changed over time.

The initial release should prioritize dependable product, supplier, purchase, inventory, sales, expiry, damage, and reporting workflows. Barcode scanning, offline mode, multi-location transfers, and automated reordering can be added after the core transaction flows are stable.

## 2. Problem Statement and Objectives

### 2.1 Problem Statement

Small shopkeepers often maintain product quantities, supplier purchases, daily sales, expiry dates, damaged items, and payment records in separate registers or informal spreadsheets. This can lead to stock mismatches, missed expiry dates, delayed replenishment, difficulty tracing purchase history, and limited visibility into sales and gross profit. ShopIQ aims to centralize these activities and make the current state of the shop easier to understand.

### 2.2 Objectives

- Maintain a searchable master catalogue of products and categories.
- Track available quantities by product and, where applicable, by batch and expiry date.
- Record purchases, supplier invoices, payments, sales, returns, damage, expiry write-offs, and adjustments.
- Automatically update inventory through controlled, auditable transactions.
- Notify users about low stock, upcoming expiry, expired stock, and pending supplier payments.
- Provide reports that support daily operations and business decisions.
- Use role-based access and shop-level data separation to protect business records.
- Provide a responsive interface usable on desktop, tablet, and mobile devices.

## 3. Scope and User Roles

### 3.1 In Scope for the Core Release

- Authentication and shop profile setup.
- Product and category management.
- Supplier directory and supplier ledger.
- Purchase entry, purchase history, and payment status.
- Batch-based stock tracking and stock movement history.
- Sales entry, cart totals, receipts, and sales history.
- Expiry monitoring and damaged-goods records.
- Low-stock alerts and operational notifications.
- Sales, purchases, inventory, expiry, damage, and supplier reports.
- Audit trail for sensitive actions and corrections.

### 3.2 Roles and Permissions

| Role | Typical permissions |
|---|---|
| Owner / Admin | Full access to shop settings, users, products, inventory, purchases, sales, reports, and corrections. |
| Manager | Manage products, suppliers, purchases, stock, sales, and reports; restricted access to owner/security settings. |
| Cashier | Create sales, print receipts, and process permitted returns; cannot edit purchase costs or manage users unless granted. |
| Inventory Staff | Receive stock, view batches, record damage, and perform authorized stock counts. |

Permissions must be enforced by the backend on every protected API, not only by hiding buttons in the user interface.

## 4. Application Navigation and Dashboard

### 4.1 Main Navigation

| Section | Pages / actions |
|---|---|
| Dashboard | Business summary, charts, alerts, quick actions |
| Products | All products, add/edit product, categories, product history |
| Inventory | Current stock, batches, stock movements, low stock, stock adjustments |
| Sales | New sale, sales history, receipts, returns, cancellations/reversals |
| Purchases | New purchase, purchase history, invoices, supplier returns |
| Suppliers | Supplier directory, add/edit supplier, supplier ledger, payment history |
| Expiry Management | Expiring soon, urgent batches, expired stock, expiry reports |
| Damaged Goods | Record damage, damage history, supplier claim/replacement status |
| Reports & Analytics | Sales, purchases, inventory, supplier balances, expiry, damage, gross profit |
| Settings | Shop profile, users, roles, units, alert thresholds, preferences |

### 4.2 Dashboard Cards

| Card | Definition / behavior |
|---|---|
| Total Products | Count of active product records; show inactive products separately. |
| Current Stock Value | Estimated inventory cost value using the configured costing method. |
| Today's Sales | Net sales for the current shop-local business date, with returns handled consistently. |
| Today's Purchases | Confirmed purchase value for the current shop-local business date. |
| Low Stock | Count of products at or below their configured reorder threshold. |
| Expiring Soon | Count of batches inside the configured expiry warning window. |
| Expired Stock | Count and value of batches past expiry that still have quantity. |
| Damaged Stock | Quantity and estimated cost value recorded as damaged. |
| Supplier Outstanding | Unpaid balances calculated from posted invoices and recorded payments. |

### 4.3 Dashboard Charts and Shortcuts

- Sales trend by day, week, and month.
- Purchase trend and supplier-wise purchase totals.
- Inventory by category and stock movement summary.
- Top-selling products and slow-moving products, where reliable sales history exists.
- Quick actions: **Add Product**, **New Sale**, **New Purchase**, **Add Supplier**, **Record Damage**, and **View Expiry**.

The dashboard is an overview; detailed operations take place in their dedicated modules.

## 5. Functional Modules

### 5.1 Product Management

**Purpose:** Maintain one authoritative product record for each sellable item.

Features:
- Create, view, edit, search, filter, and deactivate products.
- Store SKU/product code, barcode, name, category, unit, description, and optional image.
- Store default purchase cost, selling price, tax settings if needed, and minimum stock threshold.
- Associate suppliers through purchase history or an explicit supplier-product relationship.
- Display current stock, batch list, recent purchases, recent sales, and stock movement history.
- Prevent accidental deletion when a product is referenced by historical transactions; use deactivation instead.

Example product fields:

| Field | Example |
|---|---|
| Product ID | PRD001 |
| Product Name | Parle-G Biscuits |
| Category | Packaged Food |
| Purchase Price | ₹8 |
| Selling Price | ₹10 |
| Current Stock | 100 packets |
| Minimum Stock | 20 packets |
| Unit | Packet |
| Expiry Tracking | Enabled |

Product details and stock quantities should be managed separately. One product can have multiple batches with different purchase costs and expiry dates.

### 5.2 Inventory and Batch Management

Features:
- Display total saleable stock and batch-level quantities.
- Record receipts, sales, customer returns, supplier returns, damage, expiry write-offs, and approved adjustments.
- Maintain batch/lot number, received date, expiry date when relevant, unit cost, and available quantity.
- Support stock counts and adjustments with a reason, user, timestamp, and approval policy where required.
- Provide movement history with opening balance, quantity change, closing balance, reference transaction, and actor.
- For expiry-sensitive goods, select batches using **FEFO (First Expired, First Out)** where appropriate.

Example stock movement:

| Activity | Quantity change | Remaining stock |
|---|---:|---:|
| Opening stock | — | 100 |
| New purchase | +50 | 150 |
| Sales | -30 | 120 |
| Damaged goods | -5 | 115 |
| Approved adjustment | -2 | 113 |

### 5.3 Purchase Management and Entry Records

A purchase is a supplier transaction with a header and one or more purchase-item lines.

Features:
- Create a draft purchase and select a supplier, purchase date, supplier invoice number, and payment terms.
- Add multiple products with quantity, unit cost, batch number, expiry date, discount, tax, and additional charges as applicable.
- Calculate line totals, subtotal, discounts, tax, charges, final invoice amount, amount paid, and outstanding balance.
- Confirm/post the purchase to create the purchase record, purchase lines, batches or batch receipts, stock movements, and payment record if money was paid.
- Show purchase history with search by date, supplier, product, invoice number, status, and purchase reference.
- Allow draft edits; use a reversal/correction workflow for posted purchases so stock and supplier balances remain consistent.
- Support full, partial, and unpaid invoice statuses, with due dates and payment history.

**Purchase entry form**

**Purchase details**
- Purchase ID (automatically generated)
- Supplier
- Supplier invoice number
- Purchase date
- Payment due date
- Payment status: Paid, Partial, or Unpaid

**Product lines**
- Product name
- Batch number
- Quantity purchased
- Purchase price
- Expiry date, if applicable
- Discount
- Tax, where applicable
- Line total

**Summary**
- Subtotal
- Discount
- Tax
- Additional charges
- Final purchase amount
- Amount paid
- Outstanding balance

Example:

| Product | Quantity | Unit cost | Total |
|---|---:|---:|---:|
| Biscuits | 100 | ₹8 | ₹800 |
| Chips | 50 | ₹10 | ₹500 |
| Soft Drinks | 30 | ₹20 | ₹600 |
| **Total** | | | **₹1,900** |

When the purchase is confirmed:
1. The purchase record is saved.
2. Relevant product batches are created or updated.
3. Inventory quantities increase.
4. Supplier purchase history is updated.
5. The outstanding supplier balance is updated according to the payment recorded.
6. Dashboard statistics refresh.

Purchase posting must be transactional: if saving the purchase fails, inventory must not be partially updated.

### 5.4 Sales Management

Features:
- Search for products and add them to a sale cart.
- Enter quantities and authorized discounts; calculate totals on the server before finalizing.
- Record payment method (cash, UPI, card, or other), payment reference if useful, and amount received.
- On completion, create the sale and sale-item records, allocate stock from appropriate batches, create stock movements, and generate a receipt.
- Show sales history, receipt reprints, item-level detail, cashier, time, and payment status.
- Handle returns and cancellations through controlled reversal transactions; preserve the original sale for audit.
- Block sales of expired or unavailable stock unless an explicitly permitted business rule applies.

Example:

| Product | Quantity | Selling price | Total |
|---|---:|---:|---:|
| Biscuits | 2 | ₹10 | ₹20 |
| Chips | 3 | ₹20 | ₹60 |
| Cold Drink | 1 | ₹40 | ₹40 |
| **Total** | | | **₹120** |

On successful completion, stock, payment records, receipt, and dashboard totals update consistently.

### 5.5 Supplier Management

Features:
- Store supplier name, contact person, phone, email, address, optional tax registration number, notes, and status.
- Show products supplied and purchase history for each supplier.
- Maintain a supplier ledger with opening balance, posted purchases, payments, supplier returns/credit notes, and closing outstanding balance.
- Record payment amount, date, method, reference, and invoices to which the payment applies.
- Flag upcoming and overdue payments without treating a reminder as a payment.

| Field | Example |
|---|---|
| Supplier ID | SUP001 |
| Business Name | ABC Distributors |
| Contact Person | Rahul Sharma |
| Phone | Supplier contact number |
| Address | Indore, Madhya Pradesh |
| GSTIN | If applicable |
| Products Supplied | Biscuits, Chips, Snacks |
| Outstanding Balance | ₹5,000 |

### 5.6 Expiry Management

Features:
- Capture expiry dates at batch receipt when relevant.
- Provide configurable warning windows, such as 30 days, 7 days, and expired.
- List batch, product, remaining quantity, expiry date, days remaining, and estimated cost value.
- Allow filtering by category, supplier, expiry window, and quantity.
- Record expiry write-offs with reason, quantity, user, timestamp, and linked stock movement.
- Support eligible supplier returns or claims as separate transactions.
- Prevent expired stock from being sold by default; keep expired quantities distinguishable from saleable stock.

Suggested default statuses:

| Status | Default rule (configurable) |
|---|---|
| Safe | More than 30 days remaining |
| Expiring Soon | 8–30 days remaining |
| Urgent | 1–7 days remaining |
| Expired | Expiry date is before the shop-local current date |

These are suggested defaults, not universal regulatory thresholds. Shops can configure suitable warnings by product type. Expiry tracking must happen at the **batch level**, since the same product can arrive in shipments with different expiry dates.

### 5.7 Damaged Goods Management

Features:
- Record product, batch, quantity, date, damage reason, notes, optional photo, and reporter.
- Calculate estimated cost value using batch cost or configured valuation method.
- Reduce saleable inventory and create a linked stock movement in the same transaction.
- Track disposition: written off, pending supplier claim, replacement requested, replacement received, or resolved.
- Generate reports by period, product, category, supplier, reason, and estimated cost.

Example damage record:

| Field | Value |
|---|---|
| Product | Cold Drink |
| Batch | BATCH004 |
| Quantity damaged | 5 |
| Unit cost | ₹20 |
| Estimated cost value | ₹100 |
| Reason | Broken bottles |
| Status | Recorded |

The ₹100 is the estimated cost value of the damaged stock, not necessarily the final accounting loss.

### 5.8 Stock Alerts and Notifications

- **Low-stock alert:** products at or below their configured minimum quantity.
- **Expiry alert:** batches approaching expiry and expired stock requiring attention.
- **Damaged-stock alert:** new damage records or unresolved claims.
- **Purchase alert:** draft or unverified purchase entries, if the workflow uses verification.
- **Supplier payment alert:** upcoming due dates and overdue invoices.
- In-app notifications are sufficient for the first release; email, SMS, or WhatsApp can be added later.

Alerts should be based on current business records. Marking an alert as read must not alter stock or payment data.

### 5.9 Reports and Analytics

| Report | Key information |
|---|---|
| Daily / Monthly Sales | Gross sales, discounts, returns, net sales, payment-method totals, transaction count |
| Purchase Report | Supplier, invoice, date, product lines, invoice value, paid amount, balance |
| Inventory Snapshot | Product, category, quantity, batch quantities, cost value, stock status |
| Stock Movement | Opening quantity, movements, closing quantity, movement type, reference, user, timestamp |
| Low Stock | Current quantity, threshold, usage if available, suggested reorder quantity |
| Expiry | Product, batch, expiry date, quantity, days remaining, estimated value |
| Damaged Goods | Product, batch, reason, quantity, estimated cost, disposition status |
| Supplier Ledger | Opening balance, invoices, payments, credits/returns, outstanding balance |
| Gross Profit Estimate | Net sales revenue less cost of goods sold for the selected period |

Reports should support date ranges and relevant filters, pagination, and CSV/Excel export. Financial definitions must be consistent. Gross profit must not be calculated by subtracting all purchases in a month from sales revenue because some purchased goods may remain unsold.

### 5.10 Settings, Users, and Audit Logs

- Set shop name, address, currency, timezone, receipt details, and default preferences.
- Create/deactivate staff accounts and assign roles.
- Configure units, expiry warning windows, low-stock thresholds, and optional tax settings.
- Record important actions: posted purchases, completed sales, returns, stock adjustments, damage write-offs, payment edits, and permission changes.
- Include actor, timestamp, action, entity type, reference ID, and relevant before/after values where appropriate.

## 6. End-to-End Workflows

### 6.1 Purchase-to-Stock Workflow

1. Open **Purchases** and select **New Purchase**.
2. Select a supplier and enter invoice details.
3. Add products, quantities, unit costs, batch numbers, and expiry dates where applicable.
4. Review totals, discounts, taxes, and payment details.
5. Save as draft or confirm/post the purchase.
6. On posting, atomically create purchase records, batch receipts, stock movements, and any recorded payment.
7. Refresh stock, supplier ledger, alerts, and dashboard totals.
8. Display the transaction in purchase history.

### 6.2 Sale Workflow

1. Open **New Sale** and search or scan products.
2. Add quantities and permitted discounts.
3. Validate stock availability and select eligible batches, prioritizing FEFO where appropriate.
4. Review the total and record payment details.
5. Complete the sale.
6. Atomically create sale records, allocate batch quantities, create stock movements, and record payment.
7. Display/print the receipt and refresh dashboard metrics.

### 6.3 Damaged Goods Workflow

1. Open **Damaged Goods** and choose the affected product and batch.
2. Enter quantity, reason, date, notes, and optional evidence.
3. Validate that the quantity does not exceed available stock in that batch.
4. Confirm the damage record.
5. Reduce saleable batch quantity and create a stock movement in one database transaction.
6. Show the record in damage history and update inventory value and alerts.

### 6.4 Expiry Workflow

1. Capture batch expiry dates during purchase receiving.
2. A scheduled backend job or query calculates upcoming and overdue batches.
3. Dashboard cards and expiry lists show affected products and quantities.
4. Staff inspect the goods and choose an appropriate action: isolate, return to supplier, or write off.
5. Record stock removal through a linked return or expiry write-off transaction.

### 6.5 Correction and Reversal Workflow

If a posted transaction is wrong, an authorized user should create a reversal or correction referencing the original transaction. The system should restore or adjust inventory and balances consistently, retain both records, and log the reason and user. Historical transactions should not be silently deleted.

## 7. Business Rules and Calculations

| Rule / calculation | Definition |
|---|---|
| Closing stock | Opening stock + receipts + customer-return receipts − sales − supplier returns − damage/expiry write-offs ± approved adjustments |
| Purchase line total | Quantity × unit cost, adjusted for applicable line discounts and taxes according to configured calculation order |
| Purchase outstanding | Posted invoice amount − allocated payments − applicable credits/returns |
| Net sales | Sales revenue after discounts and returns, using a consistent tax-inclusive or tax-exclusive reporting basis |
| Gross profit | Net sales revenue − cost of goods sold, using the configured inventory costing method |
| Damage value | Damaged quantity × relevant inventory cost; estimate until accounting treatment is finalized |
| Low-stock status | Saleable available quantity ≤ configured minimum threshold |
| Expiry status | Derived from batch expiry date and configurable warning windows |

### 7.1 Transaction Integrity

- Posting a purchase or completing a sale must be atomic: either all related records are saved or none are.
- The backend recalculates prices, totals, discounts, permissions, and stock availability rather than trusting client values.
- Prevent negative stock by default and validate concurrent sales to avoid overselling.
- Use unique transaction references and idempotency protection where requests might be retried.
- Use a consistent shop-local timezone for business dates while storing timestamps in a standard timezone format.
- Define how customer returns re-enter inventory and how supplier returns reduce stock and supplier balances.

## 8. Data Model and Relationships

| Entity / table | Purpose and key fields |
|---|---|
| `shops` | Shop ID, name, contact/address, timezone, currency, settings |
| `users` | User ID, shop ID, name, login identifier, password hash or identity-provider ID, role, status |
| `categories` | Category ID, shop ID, name, description, active status |
| `products` | Product ID, shop ID, SKU, barcode, name, category ID, unit, prices, minimum stock, active status |
| `suppliers` | Supplier ID, shop ID, business name, contact details, address, tax ID if applicable, status |
| `product_batches` | Batch ID, product ID, supplier reference if available, batch number, received date, expiry date, unit cost, on-hand quantity |
| `purchases` | Purchase ID, shop ID, supplier ID, invoice number, date, status, subtotal, discount, tax, total, paid, balance |
| `purchase_items` | Purchase line ID, purchase ID, product ID, batch ID, quantity, unit cost, discount, tax, line total |
| `sales` | Sale ID, shop ID, receipt number, date, cashier ID, status, subtotal, discount, tax, total, payment status |
| `sale_items` | Sale line ID, sale ID, product ID, batch allocation(s), quantity, unit price, unit cost snapshot, discount, line total |
| `stock_movements` | Movement ID, shop ID, product ID, batch ID, type, signed quantity, reference type/ID, actor, timestamp, reason |
| `damaged_goods` | Damage ID, product ID, batch ID, quantity, reason, estimated value, status, evidence reference, actor, timestamp |
| `supplier_payments` | Payment ID, supplier ID, date, amount, method, reference, invoice allocations |
| `returns` | Return ID, original transaction, return type, reason, lines, quantities, amounts, stock/balance effects |
| `notifications` | Notification ID, shop ID, type, message, related entity, created/read timestamps |
| `audit_logs` | Audit ID, shop ID, actor, action, entity type/ID, timestamp, reason, before/after metadata |

### 8.1 Relationship Summary

- A shop has users, products, categories, suppliers, purchases, sales, notifications, and audit records.
- A product belongs to a category and can have many batches and stock movements.
- A purchase belongs to one supplier and contains multiple purchase-item lines.
- A sale contains multiple sale-item lines; a sale line can consume stock from one or more batches.
- A damage or expiry write-off references the affected product and batch and creates a stock movement.
- Payments can be allocated to one or more supplier invoices; balances should be derived from posted invoices, allocations, and credits.

## 9. Technical Architecture

### 9.1 Recommended Technology Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React + Vite | Pages, forms, navigation, dashboard, client-side interactions |
| UI styling | Tailwind CSS + shadcn/ui | Responsive layout and reusable interface components |
| Charts | Recharts | Sales, purchase, and inventory visualizations |
| Backend | Node.js + Express | Authentication, validation, business rules, REST APIs, transactions |
| Database | PostgreSQL | Relational records, constraints, transactional consistency |
| Data access | Prisma ORM | Schema migrations and typed database access |
| Validation | Zod or equivalent | Validate request payloads and form schemas |
| Deployment | Vercel frontend + suitable Node/PostgreSQL hosting | Hosting, environment configuration, database connectivity, backups |

### 9.2 Logical Architecture

```text
SHOPKEEPER / STAFF
        |
        v
REACT + VITE WEB APP
        |
        | HTTPS / REST API
        v
NODE.JS + EXPRESS BACKEND
        |
        +-- Authentication and authorization
        +-- Product and category service
        +-- Supplier and purchase service
        +-- Sales and returns service
        +-- Inventory, batch, and stock movement service
        +-- Expiry and damage service
        +-- Reports, notifications, and audit service
        |
        v
PRISMA ORM / DATABASE TRANSACTIONS
        |
        v
POSTGRESQL DATABASE
        |
        v
REPORTS • ALERTS • AUDIT HISTORY
```

### 9.3 Suggested API Route Examples

| Area | Example endpoints |
|---|---|
| Products | `GET /api/products`, `POST /api/products`, `PATCH /api/products/:id` |
| Suppliers | `GET /api/suppliers`, `POST /api/suppliers`, `GET /api/suppliers/:id/ledger` |
| Purchases | `POST /api/purchases`, `POST /api/purchases/:id/post`, `GET /api/purchases` |
| Sales | `POST /api/sales`, `POST /api/sales/:id/complete`, `GET /api/sales` |
| Inventory | `GET /api/inventory`, `GET /api/stock-movements`, `POST /api/stock-adjustments` |
| Expiry / Damage | `GET /api/expiry`, `POST /api/damaged-goods`, `POST /api/expiry/write-offs` |
| Reports | `GET /api/reports/sales`, `GET /api/reports/inventory`, `GET /api/reports/purchases` |

These are proposed examples; final routes should follow one consistent naming and authorization convention.

## 10. Security, Reliability, and Auditability

- Use secure authentication, strong password hashing, session protection, and secure cookies where session-based authentication is used.
- Require HTTPS in production and store secrets in environment variables or a secret manager.
- Enforce role permissions and shop-level tenant isolation in backend queries.
- Validate and normalize all inputs; use parameterized queries/ORM protections and rate limits for sensitive endpoints.
- Protect against cross-site scripting, cross-site request forgery where applicable, injection, and unauthorized object access.
- Use database transactions for stock, payment, purchase, sale, damage, and return operations.
- Keep audit records for sensitive operations; restrict who can reverse transactions or change historical financial data.
- Schedule database backups and test restoration, not just backup creation.
- Log application errors without exposing passwords, session tokens, or unnecessary personal information.
- Provide a clear failure message when a transaction fails and ensure no partial stock changes remain.

## 11. Reports and Notifications

### 11.1 Filters and Exports

- Provide start/end date filters and appropriate filters for supplier, product, category, status, and transaction type.
- Show totals and clear units/currency, and distinguish gross, net, paid, outstanding, and estimated values.
- Support paginated tables and CSV/Excel export for authorized users.
- Use the same calculation definitions in dashboard cards and downloadable reports.

### 11.2 Alert Behavior

Alerts should be generated from current business records, not maintained as an independent source of stock truth. A low-stock alert should resolve when saleable quantity rises above its threshold. Expiry and due-payment checks can run on demand and/or through scheduled background jobs.

## 12. User Interface Guidelines

- Use a persistent desktop sidebar with clear icons and labels; collapse it into a mobile menu on narrow screens.
- Keep global search, notification entry point, and current-user menu in the header.
- Use consistent status labels: Draft, Posted, Paid, Partial, Unpaid, Expiring Soon, Expired, Damaged, Reversed.
- Use tables with sorting, filters, pagination, empty states, loading states, and error messages.
- Use confirmation dialogs for irreversible or financially significant actions.
- Use accessible labels, keyboard navigation, readable contrast, and form validation messages.
- Keep common tasks short: new sale, new purchase, receive stock, record damage, and check expiry.
- Make currency and date formats configurable for the shop's locale.

## 13. Non-Functional Requirements

| Requirement | Expected behavior |
|---|---|
| Usability | Routine operations should require minimal training. |
| Responsiveness | Core screens and forms work on desktop, tablet, and mobile. |
| Consistency | Stock and financial balances remain consistent after successful transactions. |
| Performance | Common lists and dashboard summaries load promptly; use pagination and indexes. |
| Availability | Production hosting and database have a defined monitoring and recovery plan. |
| Security | Access is authenticated, authorized, encrypted in transit, and tenant-isolated. |
| Maintainability | Use modular services, reusable UI components, migrations, tests, and documented configuration. |
| Traceability | Every inventory change links to a transaction, reason, user, and timestamp. |
| Recoverability | Backups can be restored and critical records recovered after a failure. |
| Extensibility | Architecture permits future barcode, multiple locations, integrations, and additional reports. |

## 14. Implementation Roadmap

| Phase | Deliverables | Completion signal |
|---|---|---|
| 1. Foundation | Repository, app layout, authentication, shop profile, database setup, roles | Users can log in and see only their shop's workspace |
| 2. Product Catalogue | Products, categories, search, validation, active/inactive state | Product records can be created, edited, and searched |
| 3. Suppliers and Purchases | Supplier directory, purchase form, purchase history, payment status | Posting a purchase records its lines and supplier balance |
| 4. Inventory Foundation | Batches, stock movement ledger, stock snapshot, adjustments | All stock changes have a traceable movement record |
| 5. Sales | Cart, sale completion, batch allocation, payment record, receipt | A completed sale decreases stock exactly once |
| 6. Expiry and Damage | Expiry dashboard, batch warnings, damage entry, write-off workflow | Expiry and damage actions update stock and history consistently |
| 7. Reports and Alerts | Sales, purchase, stock, expiry, damage, supplier reports; notifications | Reports reconcile with transaction records |
| 8. Hardening | Permissions, audit logs, tests, backup/restore, monitoring, deployment | Critical workflows pass tests and recovery/security checks |
| 9. Enhancements | Barcode scanning, reorder suggestions, offline mode, multi-location support | Optional features are added without breaking core transactions |

### 14.1 Recommended Testing

- Unit tests for stock calculations, totals, expiry statuses, and supplier balances.
- Integration tests for purchase posting, sale completion, returns, damage, and expiry write-offs.
- Concurrency tests to ensure two simultaneous sales cannot oversell the same stock.
- Authorization tests proving users cannot access another shop's records.
- End-to-end tests for product creation through purchase, sale, and reporting.
- Backup restoration test and deployment smoke test before release.

## 15. Acceptance Criteria

- A shop owner can sign in and access the main dashboard.
- A product can be created with SKU/barcode, category, prices, unit, and minimum stock level.
- A supplier can be created and linked to purchase records.
- A purchase can be entered with multiple products and posted without partial updates.
- Posting a purchase increases the correct batch quantities and records stock movements.
- A sale can be completed only when eligible stock is available, and the receipt is retrievable.
- Sales, returns, damage, expiry write-offs, and approved adjustments create traceable stock movements.
- Batch expiry dates appear in the correct warning categories.
- Expired stock is blocked from sale by default.
- Supplier balances reconcile to invoices, payments, and applicable credits.
- Dashboard totals and reports use consistent calculation definitions.
- Authorized users can export appropriate reports.
- A user cannot access another shop's records or perform actions outside their role.
- Posted records are corrected through traceable reversals/corrections rather than silent deletion.
- Critical operations have automated tests and the deployed system has a tested backup/recovery process.

## 16. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Incorrect stock totals | Use one stock movement service, database transactions, constraints, reconciliation reports, and automated tests. |
| Expired stock sold accidentally | Track batches, apply FEFO where suitable, block expired batches by default, and show clear alerts. |
| Duplicate purchase or sale after retry | Use unique references and idempotency controls for transaction submission. |
| Supplier balance mismatch | Derive balances from posted invoices, payment allocations, credits/returns, and reversals. |
| Unauthorized data access | Enforce tenant isolation and role permissions on the backend for every request. |
| Historical records silently changed | Use immutable posted transactions, reversals, audit logs, and controlled permissions. |
| Poor adoption by busy shopkeepers | Keep the interface mobile-friendly, reduce form friction, and prioritize common actions. |
| Data loss | Automated backups, monitoring, restore drills, and export options. |
| Scope becoming too large | Deliver the core purchase-to-stock-to-sale workflow first; defer offline mode and advanced integrations. |

## 17. Future Enhancements

- Barcode scanner and label printing.
- Purchase suggestions based on minimum stock, sales velocity, and supplier lead time.
- Multiple branches, warehouses, and inter-store stock transfers.
- Customer directory, credit sales, and customer balances.
- Expense tracking and a more complete profit-and-loss view.
- Supplier purchase order creation and goods-received verification.
- WhatsApp/email reminders for expiry and supplier dues, subject to consent and provider setup.
- Offline-first operation with careful synchronization and conflict resolution.
- Accounting, e-invoice, or GST-related integrations where appropriate and compliant with applicable requirements.
- Demand trends and slow-moving inventory insights.

## 18. Conclusion

ShopIQ is planned as a practical, modular management platform for small shopkeepers and vendors. Its central principle is that every important business event—purchase, sale, return, damage, expiry write-off, payment, or stock adjustment—must be recorded consistently and remain traceable. A dashboard provides quick visibility, while dedicated modules handle detailed operations and reports.

The recommended implementation sequence is to build authentication and shop setup, then products and suppliers, followed by purchases and batch-based inventory, sales, expiry and damage management, and finally reports, alerts, audit controls, and deployment hardening. This sequence establishes a reliable core before optional advanced features are introduced.
