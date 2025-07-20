from fastapi import APIRouter, Query, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from workflow.process_flow import run_workflow
from tools.utils import save_upload_file, extract_medical_information
from uuid import uuid4
import asyncio
import glob
import os


OUTPUT_DIR = "output"
router = APIRouter()
# ENSURE OUTPUT DIRECTORY EXISTS
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/translate-video")
async def translate_video(
    background_tasks: BackgroundTasks,
    desired_language: str = Query(..., description="Target language code (e.g., 'en' for English, 'hi' for Hindi, 'es' for Spanish)."),
    video_file: UploadFile = File(..., description="Video file to be translated")    
):
    fl_name = video_file.filename.split('.')[0]
    fl_name = fl_name.replace(' ', '_')
    transaction_id = str(uuid4())
    os.makedirs(f"./{OUTPUT_DIR}/{transaction_id}", exist_ok=True)
    
    video_path = save_upload_file(video_file, destination_folder=f"{OUTPUT_DIR}/{transaction_id}")
    audio_path = f"./{OUTPUT_DIR}/{transaction_id}/temp_{fl_name}.wav"
    translated_audio_path = f"./{OUTPUT_DIR}/{transaction_id}/translated_audio.mp3"
    output_video_path = f"./{OUTPUT_DIR}/{transaction_id}/translated_video_{desired_language}.mp4"
    subtitles_srt_path = f"./{OUTPUT_DIR}/{transaction_id}/translated_subtitles.srt"

    async def wrapped_task():
        await run_workflow(video_path, audio_path, translated_audio_path, output_video_path, subtitles_srt_path, desired_language)
    
    # Use asyncio.to_thread to avoid blocking the main event loop
    asyncio.create_task(asyncio.to_thread(asyncio.run, wrapped_task()))
    

    return {"status": "success", "transaction_id": transaction_id, "msg": f"Use {transaction_id} after the processing is completed to download the video"}


@router.post("/get-video-links")
async def get_video_links(
    transaction_id: str = Query(..., description="transaction_id of the video uploaded")
):
    output_video_dir = f"./{OUTPUT_DIR}/{transaction_id}/"
    if not os.path.exists(output_video_dir):
        raise HTTPException(status_code=404, detail="Invalid transaction_id or not started yet.")
    
    mp4_files = glob.glob(os.path.join(output_video_dir, "*.mp4"))

    if not mp4_files:
        return JSONResponse(status_code=404, content={
            "transaction_id": transaction_id,
            "status": "processing",
            "message": "Processing not completed. Please try again later."
        })
    # If multiple .mp4 files are found, return them as individual download links
    download_links = [f"/download/{transaction_id}/{os.path.basename(file)}" for file in mp4_files if "final_translated_video" in file]
    if not download_links:
        return JSONResponse(status_code=404, content={
            "transaction_id": transaction_id,
            "status": "processing",
            "message": "Processing not completed. Please try again later."
        })
    return {
        "transaction_id": transaction_id,
        "status": "completed",
        "files": download_links
    }


@router.get("/download/{transaction_id}/{filename}")
async def download_file(transaction_id: str, filename: str):
    file_path = f"./{OUTPUT_DIR}/{transaction_id}/{filename}"

    if not os.path.exists(file_path) or not ".mp4" in file_path:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, media_type="video/mp4", filename=filename)


@router.post("/healthcare-extraction", description="Extract healthcare information from text/file upload.")
async def healthcare_transaction(
    file: UploadFile = File(..., description=".txt file having conversation between patient and doctor")
    ):
    """
    Ability to extract jsonyable content from conversation.
    """
    
    if not file:
        raise HTTPException(status_code=400, detail="One of file or conversation must be provided")
    if file:
        if file.content_type != "text/plain":
            raise HTTPException(status_code=400, detail="File must be a .txt file")
        file_content = await file.read()
        query = file_content.decode("utf-8")
    response = await extract_medical_information(query)
    return {"response": response}