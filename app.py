import time
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
        response = chatbot.get_response_batch(
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
    
@app.route("/chat_stream", method=["POST"])
async def chat_stream(request: Request):
    try:
        user_input = await request.json()
        # get message
        user_message = user_input.get("message")
        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")
        
        # add temperature
        try: 
            temperature = float(user_input.get("temperature"))
        except:
            return {
                "error": "Invalid input, pass a valid number between 0 and 2"
            }
        
        # add token class
        try:
            selected_token_class = user_input.get("max_tokens")
            max_tokens = chatbot.token_class[selected_token_class]
        except Exception as e:
            print("Error with selecting tokens \n", e)

        # add model selection
        try:
            selected_model = user_input.get("model")
            if selected_model not in chatbot.models:
                return {
                    "error": "Model not available."
                }
            else:
                model = selected_model
        except Exception as e:
            print("Invalid model input", e)
        # generate response
        response = chatbot.get_response(
            message=user_message,
            temperature=temperature,
            model=model,
            token=max_tokens,
        )
        # stream response
        def stream_response():
            output = ""
            for message in response:
                token = message.choices[0].delta.content
                if token:
                    # print(token, end="")
                    output += token
                    yield f"""{token}"""
                    # add delay between chunks to reduce stream speed
                    time.sleep(0.05)
        return StreamingResponse(stream_response(), media_type="text/plain")
    
    except Exception as e:
        return {"error": str(e)}