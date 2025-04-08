import openai


client=openai.OpenAI(api key="你的API钥"，base url="https://api.laozhang,ai/vl")
response client.chat.completions.create(model="grok-3",messages=[...])