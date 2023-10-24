import openai  # for calling the OpenAI API

# openai.api_key = "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"

# models



def get_response(query, context):
    EMBEDDING_MODEL = "text-embedding-ada-002"
    GPT_MODEL = "gpt-3.5-turbo"
    context = context
    query = f"""Use the below context to answer the subsequent question. If the answer cannot be found, write "I don't know."
    Article:
    \"\"\"
    {context}
    \"\"\"
    Question = {query}"""
    response = openai.ChatCompletion.create(
        messages=[
          {'role': 'system', 'content': 'your answer about the question.'},
            {'role': 'user', 'content': query},
        ],
        model=GPT_MODEL,
        temperature=0,
    )

    return response['choices'][0]['message']['content']