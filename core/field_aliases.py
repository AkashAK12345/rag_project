"""
core/field_aliases.py

Contains the canonical vocabulary and alias mappings for different business domains.
No business logic.
"""

FIELD_ALIASES = {
    # Common / Shared
    "transaction_date": ["transaction date", "date", "created at", "timestamp", "sales date", "order date"],
    "branch": ["branch", "outlet", "location", "store", "site"],
    
    # Employee Domain
    "employee_id": ["employee code", "employee id", "emp id", "staff id", "associate id", "id", "worker id", "person id", "employee no", "employee number"],
    "attendance_date": ["attendance date", "date", "log date", "shift date", "clocked date", "clock date", "punch date", "work date", "login date", "check in date", "check-in date"],
    "department": ["department", "dept", "team", "division", "unit"],
    "designation": ["designation", "title", "role", "position"],
    
    # Sales Domain
    "revenue": ["revenue", "sales amount", "invoice amount", "net sales", "total sales", "amount", "sales", "gross sales", "transaction amount"],
    "product": ["product", "item", "product name", "item sold", "article", "product description", "item name"],
    "category": ["category", "product category", "group", "item group"],
    "quantity": ["quantity", "qty", "quantity sold", "units", "count"],
    
    # Inventory / Purchase
    "unit_price": ["unit price", "price", "cost per unit", "rate", "cost price"],
    "purchase_value": ["purchase value", "total cost", "total value", "amount", "value", "cost", "total"],
    "supplier": ["supplier", "vendor", "provider", "distributor", "supplier name", "vendor name"],
    "purchase_date": ["purchase date", "po date", "order date", "date", "procurement date"],
    "movement": ["movement", "movement type", "transaction type", "type"],
    
    # Finance Domain
    "account_type": ["account type", "type", "account category", "ledger type", "category", "account"],
    "amount": ["amount", "value", "balance", "transaction amount", "debit", "credit"]
}
