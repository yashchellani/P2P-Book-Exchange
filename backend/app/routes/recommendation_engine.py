import openai

openai.api_key = "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"

def get_recommendations_from_ai(book_names):    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are recommending books to a user based on \
             an ordered list of their preferences. Return only a numbered list of the book ISBN and Title in the format 'ISBN: Title'."},
            {"role": "user", "content": f"These are the book names, in order of preference: {book_names}"},

        ]
    )

    return response
