from openai import OpenAI
client = OpenAI('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')
completion = client.chat.completions.create(
 model = 'gpt-4o-mini',
    message = [
        {'role': 'system', 'content': 'You\'re helpful assistant'},
        {'role': 'user', 'content': 'Hello!'}
    ]
)

print(completion.choices[0].message)
