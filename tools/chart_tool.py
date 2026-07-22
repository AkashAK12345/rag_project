import pandas as pd

class ChartTool:

    def __init__(self):

        self.purchase_df = pd.read_excel(
            "./data/Purchase Report Alwarpet.xlsx",
            header=5
        )

    def supplier_distribution(self):

        data = (
            self.purchase_df
            .groupby(
                "Supplier/Kitchen/Rest name"
            )["Subtotal (₹)"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        return data.to_dict()