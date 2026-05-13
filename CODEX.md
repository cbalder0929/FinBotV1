# AI Delegation Architecture Guide

## Core Principle

If something is deterministic and repeatable → use normal code.

If something requires judgment, interpretation, or language understanding → use AI.

This separation keeps AI applications:
- affordable
- scalable
- fast
- reliable

---

# What Should Be Delegated to CODE

These tasks should almost never be handled by AI.

## Parsing & Extraction

Use:
- pdfplumber
- OCR
- regex
- Python

Examples:
- extracting names
- dates
- EINs
- totals
- tables
- account numbers
- transaction rows

---

## Math & Calculations

Use:
- pandas
- numpy
- Python logic

Examples:
- totals
- subtotals
- balancing
- percentages
- variances
- reconciliations
- deductions
- comparisons

AI should not perform core arithmetic or financial calculations.

---

## Validation Rules

Use traditional backend logic.

Example:

```python
if total_income != deposits:
    flag_discrepancy()