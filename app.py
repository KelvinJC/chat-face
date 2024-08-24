import traceback

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse

from model import ChatBot


# initialise your application
app = FastAPI()
chatbot = ChatBot()


@app.route("/chat_batch", methods=["POST"])
async def chat_batch(request: Request):
    user_input = await request.json()
    user_message = user_input.get("message")
    temperature_input = float(user_input.get("temperature"))
    selected_model = user_input.get("model")

    try:
            
        response = chatbot.get_response(
            message=user_message,
            temperature=temperature_input,
            model=selected_model,
        )
        output = response.choices[0].message.content
        return PlainTextResponse(content=output, status_code=200)
    except Exception as e:
        print(traceback.format_exc())
        return {
            "error": str(e),
            "status_code": 400,
        }