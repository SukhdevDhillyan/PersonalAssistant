import ollama
response = ollama.chat(model='deepseek-r1:1.5b', messages=[
    {
        'role': 'user',
        'content': 'Why is sky blue?',
    },
])
print(response['message']['content'])
