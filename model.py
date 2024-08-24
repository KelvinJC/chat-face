import groq

from config import groq_api_key


class ChatBot():
    # set groq api key
    client = groq.Groq(api_key=groq_api_key)
    query: str
    output: str
    models = [
        # "llama-3.1-405b-reasoning",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]
    output_type = ["Stream", "Batch"]
    sys_prompt = f"""You are an intelligent generative search assistant. As an expert trained on diverse knowledge base. \
                provide to the best of your ability response to my query using the most recent information"""
    
    def get_response(self, message, model="llama-3.1-70b-versatile", temperature=0):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content":f"{self.sys_prompt}"},
                    {"role": "user", "content": f"{message}"}
                ],
                stream=True,
                temperature=temperature,
                max_tokens=1536,
            )
            return response
        except Exception as e:
            return {"error": str(e)}
        
    def get_response_batch(self, message, model="llama-3.1-70b-versatile", temperature=0):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content":f"{self.sys_prompt}"},
                    {"role": "user", "content": f"{message}"}
                ],
                response_format={"type": "text"},
                temperature=temperature,
            )
            return response
        except Exception as e:
            return {"error": str(e)}
        
    