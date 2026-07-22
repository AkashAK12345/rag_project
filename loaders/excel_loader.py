import os
import pandas as pd
from llama_index.core.schema import Document


def load_excel_documents(data_dir="./data"):

    documents = []

    excel_files = [
        f for f in os.listdir(data_dir)
        if f.endswith(".xlsx") or f.endswith(".xls")
    ]

    print(f"Found {len(excel_files)} Excel files")

    for file in excel_files:

        file_path = os.path.join(data_dir, file)

        print(f"Processing: {file}")

        try:

            sheets = pd.read_excel(
                file_path,
                sheet_name=None
            )

            for sheet_name, df in sheets.items():

                df = df.dropna(how="all")

                if df.empty:
                    continue

                for _, row in df.iterrows():

                    row_text = []

                    for col in df.columns:

                        value = row[col]

                        if pd.notna(value):

                            row_text.append(
                                f"{col}: {value}"
                            )

                    document_text = "\n".join(
                        row_text
                    )

                    documents.append(
                        Document(
                            text=document_text,
                            metadata={
                                "source_file": file,
                                "sheet": sheet_name
                            }
                        )
                    )

        except Exception as e:

            print(
                f"Failed to process {file}: {e}"
            )

    print(
        f"Created {len(documents)} documents"
    )

    return documents


def load_single_excel(file_path):

    documents = []

    file_name = os.path.basename(
        file_path
    )

    print(
        f"Processing: {file_name}"
    )

    try:

        sheets = pd.read_excel(
            file_path,
            sheet_name=None
        )

        for sheet_name, df in sheets.items():

            df = df.dropna(how="all")

            if df.empty:
                continue

            for _, row in df.iterrows():

                row_text = []

                for col in df.columns:

                    value = row[col]

                    if pd.notna(value):

                        row_text.append(
                            f"{col}: {value}"
                        )

                document_text = "\n".join(
                    row_text
                )

                documents.append(
                    Document(
                        text=document_text,
                        metadata={
                            "source_file": file_name,
                            "sheet": sheet_name
                        }
                    )
                )

    except Exception as e:

        print(
            f"Failed to process {file_name}: {e}"
        )

    print(
        f"Created {len(documents)} documents"
    )

    return documents