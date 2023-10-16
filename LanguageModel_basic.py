from transformers import pipeline

# Load the question-answering model
qa_pipeline = pipeline("question-answering")

while True:
    with open("story.txt", "r") as f:
        context = f.read()

    question = input("Enter your question: ")
    if question == "exit":
        break

    # Get the answer
    answer = qa_pipeline(question=question, context=context)

    print("Answer:", answer['answer'])

# cute isn't it?

# Path: LanguageModel_basic.py