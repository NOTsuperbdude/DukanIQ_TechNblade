# DukanIQ

## An Intelligent Retail Management and Loss Intelligence Platform for Small Retailers

**Project Category:** Retail Technology | Business Intelligence | Inventory Management
**Project Type:** Full-Stack Web Application with AI-Ready Architecture
**Target Users:** Kirana store owners, small shopkeepers, independent retailers, and local businesses
**Current Development Stage:** Initial frontend and backend prototype successfully implemented

---

# 1. Executive Summary

DukanIQ is a proposed intelligent retail management platform designed to help small shopkeepers manage their businesses more efficiently, understand their financial performance, control inventory, and identify preventable losses.

Small retail businesses frequently operate without dedicated inventory management software or detailed business analytics. Many shopkeepers rely on notebooks, calculators, memory, or basic billing applications to manage their daily operations. Although these methods may work for simple transactions, they make it difficult to identify why money is being lost, which products are underperforming, and where improvements are necessary.

DukanIQ addresses this problem by bringing essential retail management capabilities into a single, easy-to-use platform.

Instead of simply recording sales and stock, the platform aims to transform everyday business information into actionable insights. It will help shopkeepers understand what is happening inside their shops, identify potential problems, and make better purchasing and operational decisions.

The central idea behind DukanIQ is:

**A shopkeeper should not merely know how much business they are doing. They should understand how much they are earning, where they are losing money, and what they can do to improve their business.**

The initial version focuses on shop profiles, inventory management, and backend connectivity. Future development will introduce persistent database storage, sales and profit analytics, three clearly differentiated loss categories, intelligent alerts, and AI-powered business recommendations.

# 2. Problem Statement

Small retailers face several operational and financial challenges.

### 2.1 Poor inventory visibility

Shopkeepers may not have an accurate, up-to-date view of their available stock. This can lead to unexpected stockouts, unnecessary purchases, and difficulty identifying slow-moving products.

### 2.2 Difficulty understanding profitability

Revenue and profit are not the same. A shop may generate substantial sales while earning relatively little after accounting for product costs, operating expenses, and losses.

Without proper calculations, shopkeepers may struggle to determine which products contribute most to their earnings.

### 2.3 Unidentified business losses

Retailers can lose money through expired products, unsold inventory, damaged goods, pricing mistakes, and other operational problems.

When these losses are recorded inconsistently or grouped together, identifying their causes becomes difficult.

### 2.4 Reactive rather than proactive decisions

Many small retailers respond to problems only after they occur. They may discover expired stock, excesive inventory, or a shortage of fast-selling products too late to prevent the financial impact.

### 2.5 Limited access to actionable business intelligence

Advanced retail analytics tools may be too expensive, complicated, or unsuitable for independent shopkeepers.

There is an opportunity for a simpler platform that translates business data into understandable information and practical recommendations.

# 3. Proposed Solution

DukanIQ provides a centralized retail management interface through which shopkeepers can maintain business information, manage inventory, monitor performance, and eventually receive intelligent recommendations.

The proposed platform follows five core principles:

1. **Simplicity:** The interface should be understandable to shopkeepers without technical expertise.
2. **Visibility:** Important business information should be available from one dashboard.
3. **Loss awareness:** Different types of losses should be identified separately instead of being presented as one confusing number.
4. **Actionability:** Analytics should help shopkeepers decide what to do next.
5. **Accessibility:** The platform should be suitable for small retailers with limited time, resources, and technical knowledge.

DukanIQ is intended to evolve from a basic inventory application into a retail intelligence assistant.

# 4. Target Users

The primary users are small and independent retailers, particularly:

- Kirana and grocery store owners.
- Convenience store operators.
- General merchandise retailers.
- Personal care and household product sellers.
- Small businesses managing stock manually.
- Independent retailers seeking better financial visibility.

The initial product can be designed around the needs of a typical Indian neighbourhood shop, with Indian rupee pricing and a simple, accessible interface.

# 5. Core Features

## 5.1 Business Dashboard

The dashboard acts as the central control panel for the shopkeeper.

It is intended to present important information without requiring the user to navigate through multiple screens.

Planned dashboard information includes:

- Total number of products.
- Total units in inventory.
- Inventory valuation.
- Daily and monthly sales.
- Estimated gross profit.
- Identified losses.
- Low-stock alerts.
- Expiring inventory alerts.
- Important actions requiring attention.

The dashboard should prioritize the information that directly affects the shopkeeper's daily decisions.

**Current implementation:** A dashboard interface displaying product count, total inventory units, stock value, shop information, and backend connection status.

Sales, profit, and loss metrics are future features and must be connected to actual transaction and cost data before they can be presented as reliable business figures.

## 5.2 Shop Profile Management

Every shop needs a basic business profile.

DukanIQ's shop profile provides a place to record identifying information about the business.

Initial fields include:

- Shop name.
- Owner name.
- City.

The profile establishes the foundation for future shop-specific settings, reporting, and inventory management.

**Current implementation:** Shop profile editing works in the frontend. The current values are held in page state, so permanent database storage has not yet been implemented.

## 5.3 Inventory Management

Inventory management is one of DukanIQ's first major functional modules.

It allows the shopkeeper to maintain a list of products and their quantities.

### Product information

The current interface supports:

- Product name.
- Product category.
- Quantity.
- Selling price per unit.

### Inventory operations

The implemented interface supports:

- Adding products.
- Viewing products in a table.
- Searching for products by name.
- Removing products.
- Automatically recalculating product count.
- Automatically recalculating total inventory units.
- Calculating the sum of quantity multiplied by selling price.

The inventory valuation displayed by the current prototype uses selling prices, not acquisition costs. It therefore represents potential selling value rather than the actual cost value of inventory or realized profit.

### Future inventory capabilities

The production-ready version should add:

- Product editing.
- Unique product identifiers or barcodes.
- Purchase price and selling price.
- Supplier information.
- Stock-in and stock-out records.
- Purchase and sales history.
- Minimum-stock thresholds.
- Batch and expiry-date tracking where applicable.
- Damaged and returned goods tracking.
- Inventory movement history.

These capabilities will make the inventory module more reliable and enable accurate business analytics.

## 5.4 Loss Intelligence

Loss Intelligence is a defining concept of DukanIQ.

Instead of showing the shopkeeper a single vague loss figure, the platform should clearly distinguish **three separate loss categories**.

The exact calculations must use verified stock, cost, and transaction records. The following structure provides a practical starting point.

### Loss Category 1: Expiry and Damage Loss

This category covers products that cannot be sold normally because they have expired, been damaged, or become unusable.

Examples include:

- Expired packaged food.
- Broken or damaged goods.
- Products spoiled during storage.

The system should record the affected product, quantity, acquisition cost, date, and reason.

A basic calculation is:

**Expiry and Damage Loss = Acquisition Cost of Written-Off Units − Recoverable Value**

If no value can be recovered, the recoverable value is zero.

The calculation must avoid counting a loss twice when an item has already been written off.

### Loss Category 2: Dead Stock Loss

This category covers capital tied up in inventory that is not selling or is moving significantly slower than expected.

Examples include:

- Products remaining unsold for an extended period.
- Excess inventory purchased beyond realistic demand.
- Products occupying shelf space without meaningful sales.

Dead stock should not automatically be treated as a fully realized financial loss. Unsold products may still be saleable.

DukanIQ should therefore distinguish between:

- **Capital tied up:** The acquisition cost of slow-moving inventory.
- **Realized loss:** A documented reduction in recoverable value, write-off, or other measurable financial loss.

The platform can use inventory age and sales velocity to flag products that require attention.

### Loss Category 3: Sales and Margin Loss

This category covers losses associated with selling products at prices or under conditions that reduce the expected financial return.

Examples may include:

- Selling below acquisition cost.
- Unrecorded discounts.
- Pricing mistakes.
- Transaction discrepancies.
- Other verified reductions in expected margin.

A basic calculation is:

**Sales Loss = Expected Gross Margin − Actual Gross Margin**

This comparison must use consistent products, quantities, and time periods. Discounts and transaction adjustments must be recorded to avoid double-counting.

Not every reduction in margin represents a loss: legitimate promotional discounts may be intentional business decisions.

### How Loss Intelligence should work

For each category, DukanIQ should display:

- The loss category.
- The affected product or transaction.
- The quantity involved.
- The financial amount, where measurable.
- The reason for the loss.
- The recommended action.

For example, a shopkeeper might see that a particular product is approaching its expiry date, another has remained unsold for months, and a third has repeatedly been sold below its acquisition cost.

These are three different problems and require three different responses.

The platform's objective is to help shopkeepers understand the reason behind each loss rather than simply showing them a large number.

## 5.5 Sales and Profit Analytics

A future sales module will record transactions and calculate business performance.

Planned capabilities include:

- Recording sales.
- Recording product costs.
- Calculating revenue.
- Calculating gross profit.
- Tracking discounts and returns.
- Comparing daily, weekly, and monthly performance.
- Identifying best-selling products.
- Identifying products with weak margins.

The platform must distinguish between revenue, gross profit, operating expenses, and net profit.

For example:

**Revenue = Total Value of Sales**

**Gross Profit = Net Sales Revenue − Cost of Goods Sold**

**Net Profit = Gross Profit − Operating Expenses and Other Applicable Costs**

The exact accounting treatment should be defined before the application is used for real financial reporting.

## 5.6 Smart Alerts and Recommendations

Once reliable data is available, DukanIQ can generate useful alerts.

Examples include:

- A product is running low.
- A batch is approaching its expiry date.
- Inventory has remained unsold beyond a configured period.
- A product is repeatedly being sold at an unusually low margin.
- A purchase quantity appears excessive relative to sales.
- A product requires replenishment.

Recommendations should be understandable and actionable.

For example:

"Cooking oil is selling quickly and only 4 units remain. Review your next purchase."

Such recommendations should be based on recorded inventory and sales data rather than invented or assumed values.

# 6. How DukanIQ Works

The proposed system follows a structured workflow.

### Step 1: Shop setup

The shopkeeper enters the basic shop profile.

### Step 2: Product registration

The shopkeeper adds products, categories, quantities, and pricing information.

### Step 3: Business activity recording

As the application develops, purchases, sales, returns, write-offs, and inventory adjustments are recorded.

### Step 4: Data storage

The backend validates incoming information and stores it in the database.

### Step 5: Business calculations

The application calculates stock levels, inventory valuation, sales performance, margins, and documented losses.

### Step 6: Problem identification

Rules and analytics identify conditions such as low stock, slow-moving inventory, expiry risk, and negative margins.

### Step 7: Actionable insights

The dashboard presents the relevant information and suggests appropriate next steps.

### Step 8: Continuous improvement

As the shopkeeper records more accurate information, DukanIQ can provide better comparisons and recommendations.

**The long-term workflow is:**

Shop Activity → Data Collection → Database → Business Calculations → Loss Identification → Dashboard Insights → Shopkeeper Action

# 7. Technical Architecture

DukanIQ is being developed as a full-stack web application.

The initial technology choices are:

| Layer             | Technology          | Purpose                                       |
| ----------------- | ------------------- | --------------------------------------------- |
| Frontend          | Next.js             | User interface and dashboard                  |
| Frontend language | TypeScript          | Type safety and maintainable application code |
| Styling           | Tailwind CSS        | Responsive interface design                   |
| Backend           | Python with FastAPI | Business logic and API endpoints              |
| Data validation   | Pydantic            | Validate incoming and outgoing data           |
| Database access   | SQLAlchemy          | Manage database operations                    |
| Database          | PostgreSQL, planned | Persistent storage of shop and inventory data |
| PostgreSQL driver | Psycopg             | Connect Python to PostgreSQL                  |
| Automated testing | Pytest and HTTPX    | Test backend endpoints                        |
| Version control   | Git                 | Track changes to source code                  |

A hosted PostgreSQL provider such as Supabase is a possible database deployment option, but the persistent database connection has not yet been implemented.

### Architecture overview

The system has three main layers.

**1. Frontend layer**

The Next.js application displays the dashboard and allows the shopkeeper to interact with shop profiles and products.

**2. Backend layer**

FastAPI receives requests, validates data, applies business rules, and communicates with the database.

**3. Database layer**

PostgreSQL will persist shop profiles, products, inventory movements, sales, and loss records.

The intended communication flow is:

Next.js Frontend → FastAPI API → Database

Responses return through the backend to the frontend.

The database credentials must remain on the server and must never be exposed in browser-side code.

# 8. Current Development Status

DukanIQ has progressed beyond an initial project idea. A working frontend and a basic backend have been created and tested.

## Completed components

### Development environment

- Git installed.
- Python installed.
- Node.js and npm installed.
- Python virtual environment created.
- FastAPI and testing dependencies installed.
- Next.js frontend created.

### Backend prototype

The initial FastAPI application includes:

- A home endpoint.
- A health-check endpoint.
- Application metadata.
- Automated tests for the initial endpoints.

Both initial tests passed successfully.

The health endpoint returns a healthy status, and the frontend has successfully displayed that status.

### Frontend prototype

The current dashboard includes:

- DukanIQ branding.
- Shop profile editing.
- Product listing.
- Product creation.
- Product searching.
- Product removal.
- Product count.
- Total inventory units.
- Basic inventory valuation.
- Backend connection status.

The shop profile and inventory interface were manually tested successfully.

## Components not yet completed

The following remain development tasks:

- Persistent database integration.
- Permanent storage of shop profiles.
- Permanent storage of products.
- Product editing and detailed stock movement tracking.
- Sales recording.
- Cost-based inventory valuation.
- Reliable profit calculations.
- Implementation of the three loss categories.
- Expiry and dead-stock tracking.
- Automated alerts.
- AI-powered recommendations.
- Authentication and authorization.
- Production deployment and operational security.

The current inventory data is stored in frontend state and resets when the page is reloaded. It should therefore be considered a functional prototype rather than a production-ready retail management system.

# 9. Development Roadmap

The project can be developed sequentially through the following 15 phases.

| Phase | Development objective                    | Expected outcome                                                 |
| ----- | ---------------------------------------- | ---------------------------------------------------------------- |
| 1     | Project setup and architecture           | Frontend and backend running locally                             |
| 2     | Shop profile and inventory interface     | Functional shop and product screens                              |
| 3     | Database integration                     | Persistent shop and product records                              |
| 4     | Inventory API development                | Create, read, update, and delete product operations              |
| 5     | Inventory validation and stock movements | Reliable quantity and stock history management                   |
| 6     | Purchase and sales recording             | Recorded business transactions                                   |
| 7     | Sales and profit analytics               | Revenue, gross profit, and performance summaries                 |
| 8     | Loss Intelligence                        | Three distinct loss categories and calculations                  |
| 9     | Expiry and dead-stock monitoring         | Product risk tracking and alerts                                 |
| 10    | Dashboard analytics                      | Connected metrics and business summaries                         |
| 11    | Smart recommendations                    | Rule-based, data-driven business suggestions                     |
| 12    | Authentication and user management       | Secure access and shop-specific data isolation                   |
| 13    | Reporting and exports                    | Downloadable business summaries and reports                      |
| 14    | Testing and deployment                   | Validated application deployed to a suitable hosting environment |
| 15    | Optimization and intelligent features    | Improved usability, reliability, and AI-assisted analytics       |

The roadmap is a development plan, not a claim that all 15 phases have been completed.

Each phase should be tested before moving to the next one. This will reduce integration problems and make the application easier to maintain.

# 10. Security, Reliability, and Data Integrity

A retail management platform handles commercially sensitive information, including sales, product costs, stock levels, and profitability.

The production version should incorporate:

- Secure authentication.
- Authorization checks on backend endpoints.
- Shop-specific data access restrictions.
- Server-side input validation.
- Secure database credential management.
- HTTPS in deployment.
- Database backups.
- Error logging and monitoring.
- Protection against duplicate transactions.
- Audit trails for important stock adjustments.
- Proper handling of financial calculations.

Loss calculations should be traceable to underlying transactions or stock records. Shopkeepers should be able to understand why an amount has been classified as a loss.

The system should not label an item as a confirmed financial loss merely because it is slow-moving or approaching expiry. Those conditions are warnings until the actual financial impact is established.

# 11. Future Scope and AI Integration

DukanIQ can eventually incorporate AI-assisted retail analytics.

Potential future capabilities include:

### Demand forecasting

Estimate future product demand from historical sales, seasonality, and other available signals.

### Intelligent replenishment

Recommend purchase quantities based on stock levels, sales velocity, and supplier lead times.

### Anomaly detection

Identify unusual stock discrepancies, unexpected margin changes, or suspicious transaction patterns.

### Natural-language business assistant

Allow shopkeepers to ask questions such as:

- Which products generated the highest gross profit this month?
- Which products have not sold for 30 days?
- How much inventory value is currently tied up in slow-moving products?
- Which products need to be reordered?
- What are my recorded losses in each of the three categories?

These features require appropriate historical data, validated calculations, and testing before their recommendations can be relied upon.

AI should support the shopkeeper's decisions, not replace accurate accounting or reliable source records.

# 12. Expected Benefits

When fully implemented and validated, DukanIQ aims to deliver the following benefits.

**Improved inventory visibility:** Shopkeepers can see what they have in stock and identify products that require attention.

**Better financial awareness:** Sales, acquisition costs, and operating expenses can be analyzed separately to provide a clearer view of profitability.

**More understandable losses:** Three distinct loss categories can help users understand different operational and financial problems.

**Improved purchasing decisions:** Inventory and sales history can help reduce unnecessary purchases and avoid preventable stock shortages.

**Time savings:** A centralized digital interface can reduce dependence on scattered records and repetitive manual calculations.

**Better business decisions:** Clear summaries and actionable recommendations can help shopkeepers prioritize the issues that matter most.

These are intended benefits. Their actual impact should be evaluated through pilot testing with real retailers.

# 13. Conclusion

DukanIQ is envisioned as an intelligent business assistant for small retailers, combining inventory management, financial visibility, loss identification, and actionable insights in one accessible application.

Its defining objective is to help shopkeepers move beyond simply recording business activity and toward understanding the performance of their businesses.

The three-category Loss Intelligence approach is especially important because it distinguishes between expiry and damage, capital tied up in dead stock, and losses associated with sales and margins. These problems have different causes and require different responses.

The current prototype establishes the technical foundation through a working Next.js interface, a FastAPI backend, and basic shop and inventory interactions. The next major milestone is persistent database integration, followed by transaction recording, reliable financial calculations, and Loss Intelligence.

The long-term vision is to make DukanIQ a practical, accessible, and data-driven retail management platform that helps small shopkeepers understand their business, reduce preventable losses, and make better decisions.

**DukanIQ — Know Your Stock. Understand Your Losses. Run Your Business Smarter.**
