import pandas as pd

class AnalyticsTool:

    def __init__(self):

        self.purchase_df = pd.read_excel(
            "./data/Purchase Report Alwarpet.xlsx",
            header=5
        )

    def get_total_purchase_value(self):

        total = self.purchase_df[
            "Subtotal (₹)"
        ].sum()

        return f"Total purchase value: ₹{total:,.2f}"

    def get_supplier_count(self):

        count = self.purchase_df[
            "Supplier/Kitchen/Rest name"
        ].nunique()

        return f"Total suppliers: {count}"