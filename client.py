from openai import OpenAI
 

# if you saved the key under a different environment variable name, you can do something like:
client = OpenAI(
  api_key="<your_API_KEY_here.>",
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a virtual assistant named friday skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)
