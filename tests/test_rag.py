from tools.rag_tool import RAGTool

tool = RAGTool()

response = tool.run(
    "What information is available in the purchase report?"
)

print(response)