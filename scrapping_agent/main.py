from fastapi import HTTPException, FastAPI,File, UploadFile
from starlette import status
from utils.schema import Request, ChatRequest
from dotenv import load_dotenv
from scrapping_agent.services import chat
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os,uuid
from scrapping_agent.stt import transcript_obj
from rag_agent.services import retriever_query
from fastapi.responses import JSONResponse
from elevenlabs import ElevenLabs
from fastapi.staticfiles import StaticFiles


client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

load_dotenv()

agent = FastAPI()
agent.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent.mount("/static", StaticFiles(directory="static"), name="static")

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


@agent.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    upload_dir = "static/audio"
    os.makedirs(upload_dir, exist_ok=True)

    webm_path = os.path.join(upload_dir, "recording.webm")
    with open(webm_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    
    transcript = transcript_obj.transcribe(webm_path)
    result = retriever_query(transcript)
    print("result",result)
    output_filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(upload_dir, output_filename)


    audio_data = client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        output_format="mp3_44100_128",
        text=result,
        model_id="eleven_multilingual_v2"
    )

    with open(output_path, "wb") as out_f:
        for chunk in audio_data:
            out_f.write(chunk)


    audio_url = f"/static/audio/{output_filename}"

    return JSONResponse({
        "agent_response": result,
        "audio_url": audio_url
    })


@agent.post("/rag/chat-completions")
def chat_completions(request: ChatRequest):
    return retriever_query(request.text)