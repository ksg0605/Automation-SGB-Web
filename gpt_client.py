import openai

class GPTClient:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def generate_response(self, system_input, user_input):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_input},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content