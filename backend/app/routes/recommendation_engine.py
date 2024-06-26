from openai import OpenAI

client = OpenAI()


def get_recommendations_from_ai(book_names, existing_books):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are recommending books based on a list of user preferences. Do not include any other information in your response. Only return a string of the book titles separated by commas.",
            },
            {
                "role": "user",
                "content": f"Recommend up to 5 similar new books that are a close match in terms of genre to the following {book_names}. Choose new books from the following list: {existing_books}, or other very similar books.",
            },
        ],
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content.split(",")
