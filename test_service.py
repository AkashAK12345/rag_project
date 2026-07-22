from services.rag_service import RagService

rag = RagService()

response = rag.query("Summarize the purchase report")

print(response)