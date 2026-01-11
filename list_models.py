
from groq import Groq
client = Groq(api_key="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")
for model in client.models.list().data:
    print(model.id)
