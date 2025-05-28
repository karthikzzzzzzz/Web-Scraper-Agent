from fastapi import HTTPException, FastAPI
from starlette import status
from utils.schema import Request
from dotenv import load_dotenv
from services import chat


load_dotenv()

agent = FastAPI()

@agent.post(
    "/v1/chat-completions",
    summary="Scraps the internet for the live stock price of a given market",
)
async def process_query(
    request: Request,
):
    try:
        result = await chat.run_query(request.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

