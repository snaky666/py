# Design Guidelines: نظام إدارة المحلات POS

## Design Approach

**System Selected:** Material Design with POS industry best practices (inspired by Square POS, Toast POS)

**Rationale:** This is a data-intensive business application requiring efficiency, clarity, and quick information access. Material Design provides excellent patterns for forms, tables, and data visualization while maintaining visual hierarchy.

**Key Principles:**
- Information density over visual decoration
- Quick access to critical functions
- Clear visual hierarchy for complex data
- RTL (Right-to-Left) Arabic language support throughout

---

## Typography

**Font Family:** 
- Primary: 'Noto Sans Arabic' via Google Fonts CDN (excellent Arabic support)
- Fallback: system-ui, -apple-system

**Scale & Usage:**
- **Page Titles:** text-3xl font-bold (h1)
- **Section Headers:** text-2xl font-semibold (h2)
- **Card Titles:** text-xl font-semibold (h3)
- **Table Headers:** text-sm font-semibold uppercase tracking-wide
- **Body Text:** text-base font-normal
- **Labels:** text-sm font-medium
- **Small Text/Metadata:** text-xs
- **Numbers/Prices:** font-mono for alignment (use 'IBM Plex Mono' for Arabic numerals)

---

## Layout System

**Spacing Primitives:** Use Tailwind units of **2, 4, 6, 8, 12, 16** (p-2, m-4, gap-6, etc.)

**Grid Structure:**
- **Sidebar Navigation:** Fixed w-64 on desktop, collapsible on tablet/mobile
- **Main Content Area:** flex-1 with max-w-7xl mx-auto px-6
- **Dashboard Cards:** grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6
- **Tables:** full-width within container, responsive scroll on mobile

**Container Strategy:**
- Page wrapper: min-h-screen with sidebar + main content flex layout
- Content sections: p-6 to p-8 consistent padding
- Cards: p-6 internal padding
- Forms: max-w-2xl for optimal readability

---

## Component Library

### Navigation
**Sidebar (Right-side for RTL):**
- Vertical navigation with icons from Heroicons (outline style)
- Logo/brand at top with h-16 height
- Active state: subtle background treatment with border-r-4 indicator
- Menu items: py-3 px-4 with icon + text horizontal layout
- Grouped sections with text-xs text-muted headers

**Top Bar:**
- h-16 with search input, notifications icon, user profile dropdown
- Breadcrumb navigation for deep pages

### Dashboard Cards
**Stats Cards (4-column grid):**
- Elevated appearance (shadow-md)
- Icon (large, p-3 in top-right corner for RTL)
- Primary metric: text-3xl font-bold
- Label: text-sm text-muted below metric
- Trend indicator: small text with arrow icon

### Forms
**Input Fields:**
- Labels: mb-2 block text-sm font-medium
- Inputs: w-full px-4 py-2.5 border rounded-lg
- Focus state: ring-2 offset treatment
- Error state: border-error with text-xs error message below
- Helper text: text-xs text-muted mt-1

**Button Hierarchy:**
- Primary: px-6 py-2.5 rounded-lg font-medium
- Secondary: outline variant with border-2
- Icon buttons: p-2 rounded-md for table actions
- Sizes: sm (py-1.5 px-4), default (py-2.5 px-6), lg (py-3 px-8)

### Tables
**Data Tables:**
- Striped rows for readability (alternate row backgrounds)
- Headers: sticky top-0 with bg-surface and border-b-2
- Cell padding: px-6 py-4
- Actions column: Right-aligned (left in RTL) with icon buttons gap-2
- Row hover state for interactivity
- Pagination: bottom with prev/next + page numbers

### Modals & Overlays
**Modal Structure:**
- Backdrop: fixed inset-0 with overlay
- Content: max-w-2xl mx-auto mt-20 rounded-xl shadow-2xl
- Header: p-6 border-b with title + close button
- Body: p-6
- Footer: p-6 border-t with action buttons flex justify-end gap-3

### Status Indicators
**Payment/Installment Status:**
- Badge component: px-3 py-1 rounded-full text-xs font-semibold
- States: Pending, Partially Paid, Fully Paid, Overdue
- Use icon + text combination for clarity

### Search & Filtering
**Search Bar (Critical for Barcode):**
- Prominent placement with icon prefix
- w-full md:max-w-md
- Autofocus on page load for POS screen
- Clear button (x) when text present
- Enter key to add item

---

## Key Pages Structure

### Dashboard
- 4-column stats cards row
- Recent sales table (5 rows max)
- Low stock alerts section
- Quick actions panel (New Sale, Add Product buttons)

### Products Page
- Search + Add Product button in header
- Filters: category, stock status (pills/chips)
- Products table: Barcode | Name | Price | Stock | Actions
- Empty state: illustration + "Add your first product" CTA

### Sales/Invoice Page
**Split Layout:**
- Left side (60%): Product search + selected items list
- Right side (40%): Cart summary, customer select, payment method, total, submit
- Selected items: mini-table with qty spinners and remove buttons

### Customers Page
- Search + Add Customer button
- Customers table: Name | Phone | Address | Total Debt | Actions
- Click row to view installment details

### Installments/Payments Page
- Filters: Customer, Status, Date range
- Installments table: Customer | Invoice # | Due Date | Amount | Paid | Balance | Status | Actions
- Payment modal: large input for amount, payment method selector

### Reports Page
- Date range picker (prominent)
- Metrics cards: Total Sales, Cash Received, Pending Installments, Inventory Value
- Charts section: Sales trend line chart, Payment status pie chart
- Detailed tables below charts

---

## Icons
**Library:** Heroicons (outline style) via CDN
- Navigation: home, users, shopping-bag, currency-dollar, chart-bar, cog
- Actions: plus, pencil, trash, eye, printer, download
- Status: check-circle, x-circle, clock, exclamation-triangle

---

## Responsive Behavior
- Desktop-first approach (primary use case)
- Tablet: Sidebar collapses to icon-only
- Mobile: Hamburger menu overlay, stack all multi-column layouts, simplified tables (card view)

---

## Arabic/RTL Considerations
- All layouts mirror horizontally (dir="rtl" on HTML)
- Text alignment: text-right by default
- Icons/badges on right side of text
- Numbers use Eastern Arabic numerals or Western with font-mono for consistency
- Navigation sidebar on right edge
- Table actions column on right (left in LTR)

---

## Accessibility
- Minimum touch target: 44px × 44px for all interactive elements
- Form inputs with associated labels (for attribute)
- Skip to main content link
- Keyboard navigation support throughout
- ARIA labels for icon-only buttons
- Focus indicators on all interactive elements