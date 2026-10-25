---
name: Retail Operations Modern
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#434655'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#006c4a'
  on-secondary: '#ffffff'
  secondary-container: '#82f5c1'
  on-secondary-container: '#00714e'
  tertiary: '#824500'
  on-tertiary: '#ffffff'
  tertiary-container: '#a65900'
  on-tertiary-container: '#ffede1'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#85f8c4'
  secondary-fixed-dim: '#68dba9'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#ffdcc3'
  tertiary-fixed-dim: '#ffb77d'
  on-tertiary-fixed: '#2f1500'
  on-tertiary-fixed-variant: '#6e3900'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
  crimson-danger: '#DC2626'
  surface-canvas: '#F8FAFC'
  surface-card: '#FFFFFF'
  border-subtle: '#E2E8F0'
  status-safe: '#10B981'
  status-expiring: '#F59E0B'
  status-urgent: '#EA580C'
  status-expired: '#DC2626'
  status-draft: '#64748B'
  status-reversed: '#475569'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  metric-display:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  data-table:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.025em
  caption-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-mobile: 0.75rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

This design system is engineered for retail shop owners, store managers, and inventory operators who require high-speed operational clarity, accurate stock bookkeeping, and clear real-time financial tracking. The tone is utilitarian, dependable, precise, and alert—enabling rapid decision-making under high-throughput conditions.

The aesthetic blends **Modern Corporate SaaS** with **High-Density Data Utility**:
- Crisp, low-contrast structural borders paired with slate surfaces for sustained all-day viewing.
- Unambiguous semantic color coding for inventory longevity (FEFO batch monitoring) and transactional ledger states (Draft, Posted, Settled, Reversed).
- Highly legible numerical tables and metric badges with tabular alignment to ensure zero ambiguity during cashiering and receiving workflows.

## Colors

The color system balances neutral operational surfaces with targeted, functional hues that indicate inventory lifecycle and transactional validity.

### Functional Color Assignments
- **Primary (`#2563EB`)**: Used for primary action buttons, focused input states, key navigation highlights, purchase orders, and supplier records.
- **Secondary (`#059669`)**: Used exclusively for positive financial events, active in-stock records, sales velocity indicators, and `Posted` or `Paid` statuses.
- **Tertiary / Warning (`#D97706`)**: Applied to `Expiring Soon` warnings (8–30 days), partial ledger settlements, and low-inventory reorder prompts.
- **Crimson Danger (`#DC2626`)**: Reserved for stock write-offs, `Expired` inventory, damages, destructive confirmation dialogs, and `Unpaid` balances.
- **Neutral Dark (`#0F172A`)**: High-contrast slate tone used for primary typography, table headers, and structural UI elements.

Background surfaces rely on crisp `#F8FAFC` canvas layers with `#FFFFFF` card layers, framed by 1px subtle borders (`#E2E8F0`) to maintain tabular structure without visual clutter.

## Typography

Typography prioritizes tabular legibility and rapid skimming under varying retail lighting conditions.

- **Headings & KPI Cards**: Set in **Plus Jakarta Sans** for crisp, modern geometric authority on revenue totals, stock valuations, and main navigation headers.
- **Body & Data Tables**: Set in **Inter** with native tabular numeric formatting enabled (`font-variant-numeric: tabular-nums`). All monetary figures, quantities, batch timestamps, and SKUs must use tabular alignment to guarantee vertical number scanning across lines.
- **Status Badges & Captions**: Rendered in uppercase or bold title case with subtle tracking (`letterSpacing: 0.025em`) to provide instant status recognition without dominating adjacent transactional rows.

## Layout & Spacing

This design system uses a fluid, responsive 12-column grid optimized for compact, high-density inventory views.

### Screen Adaptations
- **Desktop (1280px+)**: Persistent left-side navigation rail (240px wide). 12-column data grid with `1.25rem` gutters. Metric cards display 4 across in a row. Main ledger tables display full columns: Batch ID, SKU, Quantity, FEFO Expiry, Unit Cost, Total Value, Status, and Actions.
- **Tablet (768px - 1279px)**: Collapsible sidebar navigation. 6-column grid with `1rem` gutters. Metric cards wrap in a 2x2 grid. Data tables hide non-critical metadata (e.g., creation timestamp) behind row-expansion toggles.
- **Mobile (<768px)**: Off-canvas drawer menu. Single-column stacked cards. Tables convert into clean card lists or horizontal scrollable containers with sticky primary columns (Product Name/SKU).

## Elevation & Depth

To preserve the focus required for fast-paced retail POS and warehouse stocktaking, elevation relies on clean structural separation rather than heavy skeuomorphism:

- **Borders over Shadows**: Component boundaries are articulated primarily via 1px low-contrast strokes (`#E2E8F0` / `border-slate-200`) on white or light slate surfaces.
- **Card Depth**: Standard metric and analytical cards use a subtle ambient elevation: `0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)`.
- **Flyouts & Dropdowns**: Searchable select menus, autocomplete popovers, and date pickers use a structured elevated shadow: `0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.03)`.
- **Destructive & Confirmation Modals**: Transaction write-offs and ledger reversal overlays use a high-contrast dark scrim backdrop (`rgba(15, 23, 42, 0.5)`) paired with a sharp card layer to ensure irreversible financial operations demand full operator focus.

## Shapes

The design system employs a soft, utilitarian border radius profile (`roundedness: 1`, default base radius of `0.25rem` or `4px` to `6px`). 

- **Inputs, Buttons, and Table Cells**: Structured with `rounded-md` (4px–6px) corners to preserve a precise, compact software feel and maximize screen real estate.
- **Metric Cards & Modals**: Soft `0.5rem` (`rounded-lg`) borders to soften high-density dashboard layouts.
- **Status Badges & Pill Chips**: Retain a clean pill shape (`rounded-full`) to contrast against rectangular table rows and input grids.

## Components

### Buttons
- **Primary**: Solid blue (`#2563EB`) with white text, font size `14px`, medium weight. Height of 36px for standard actions and 32px for compact table action rows.
- **Secondary / Outline**: 1px border (`#E2E8F0`), neutral dark text (`#0F172A`), white background. Hover state fills with `#F8FAFC`.
- **Destructive**: Solid crimson (`#DC2626`) for irreversible write-offs or soft tinted red (`#FEE2E2` background with `#B91C1C` text) for secondary actions like item removals from the POS cart.

### Form Inputs & Barcode Pickers
- **Text & Number Inputs**: Height 36px, horizontal padding `12px`, 1px border (`#CBD5E1`). Focus state introduces a crisp ring in primary blue with zero blur (`outline: 2px solid #2563EB`).
- **Tabular Inputs (Quick Entry)**: Embedded in purchase and sales rows with minimal padding (height 30px) and mono/tabular alignment for instant price and quantity recalculation.

### Status Badges & Chips
- **Safe / Active Stock**: Mint-emerald background (`#ECFDF5`), deep green text (`#065F46`), border `1px solid #A7F3D0`.
- **Expiring Soon (8–30 Days)**: Soft amber background (`#FFFBEB`), deep amber text (`#92400E`), border `1px solid #FDE68A`.
- **Urgent Expiry (1–7 Days)**: Soft orange background (`#FFF7ED`), dark burnt-orange text (`#9A3412`), border `1px solid #FFEDD5`.
- **Expired / Damaged**: Soft red background (`#FEF2F2`), crimson text (`#991B1B`), border `1px solid #FECACA`.
- **Draft / Reversed**: Slate background (`#F1F5F9`), slate text (`#475569`), border `1px solid #CBD5E1`.

### Data Tables
- **Header**: `#F8FAFC` background, height 36px, `11px` uppercase tracking, text `#64748B`.
- **Rows**: Alternating or white-surface with 1px border bottoms (`#F1F5F9`). Row height set to 44px for high density. Right-aligned numerical amounts with `font-variant-numeric: tabular-nums`.

### Metric Cards
- White surface, `1.25rem` padding, 1px border (`#E2E8F0`). Contains top row with uppercase caption and icon, prominent 28px bold numeric value, and bottom trend delta indicator in green or crimson.