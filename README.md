# Real Estate Deal Analysis Engine

## Overview

This project is a data-driven real estate underwriting engine designed to identify potentially undervalued residential properties using live market data.

The system ingests property listings and rental data, applies comparable analysis, estimates rental income, calculates financial metrics, and ranks investment opportunities.

---

## Key Features

### 1. Live Property Data
- Pulls real-time **for-sale listings**
- Pulls real-time **rental listings**
- Uses geographic targeting (ZIP codes, radius)

---

### 2. Comparable Property Analysis
- Finds nearby properties using geographic distance (Haversine formula)
- Filters comps by:
  - Distance
  - Square footage similarity
- Estimates market value using weighted price-per-square-foot

---

### 3. Rental Income Estimation (Core Upgrade)
- Uses **actual rental listings** as comps
- Matches by:
  - Distance
  - Square footage
  - Bedroom count (±1 tolerance)
- Removes outliers from rental data
- Falls back to heuristic model if insufficient comps

---

### 4. Expense Modeling
- Vacancy loss
- Operating expenses (ratio-based)
- Property taxes (if available)
- Calculates Net Operating Income (NOI)

---

### 5. Financing Model
- Mortgage calculations
- Debt service
- Cash flow
- Debt Service Coverage Ratio (DSCR)

---

### 6. Deal Scoring System
- Evaluates:
  - Cap rate
  - Cash flow
  - DSCR
  - Discount to market value
- Applies penalties for:
  - Low price (risk proxy)
  - Weak location (price per sqft proxy)
  - Low rent confidence

---

### 7. Deal Filtering
- Filters out weak opportunities
- Focuses on viable investment candidates
- Fallback logic ensures results even in tight markets

---

### 8. Multi-Market Scanning
- Supports multiple ZIP codes in a single run
- Aggregates opportunities across regions

---

## Output

The system exports a CSV file containing:

- Property details (price, sqft, location)
- Estimated rent
- NOI
- Cap rate
- Cash flow
- DSCR
- Investment score

---

## How It Works (Pipeline)

1. Fetch sale listings  
2. Fetch rental listings  
3. Normalize and clean data  
4. Run comparable analysis  
5. Estimate rent from rental comps  
6. Calculate expenses and NOI  
7. Apply financing model  
8. Score and filter deals  
9. Export results  

---

## Limitations

- Does not currently model:
  - Property condition
  - Renovation costs
  - Crime or neighborhood-level risk
- Rental estimates are based on available listings and may not reflect off-market rents
- Results should be used for **screening**, not final investment decisions

---

## Future Improvements

- Median-based rent modeling
- Neighborhood quality scoring
- Renovation cost estimation
- Portfolio-level optimization
- Automated deal alerts

---

## Tech Stack

- Python
- Pandas / NumPy
- HomeHarvest (data scraping)
- Custom financial modeling modules

---

## Usage

Run the pipeline:

```bash
./run.sh