from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from code import PDFTableProcessor

app = FastAPI()


@app.post("/upload/")
async def create_upload_file(file: UploadFile = File(...)):

    # Genera un nome unico per il file
    unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    file_location = f"files/{unique_filename}"
    
    # Salva il file
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    processor = PDFTableProcessor()

    print(file_location)

    response = processor.processor(file_location)

    try:
        os.remove(file_location)
        print(f"File {file_location} eliminato con successo")
    except Exception as e:
        print(f"Errore durante l'eliminazione del file {file_location}: {e}")

    return JSONResponse(content=response)

    print("got here")
