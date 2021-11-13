import uvicorn
import requests
import cv2
import json

from typing import Optional

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

app = FastAPI()


@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}

@app.post("/predict_by_url/")
def create_file(file_url: str):
    # Make http request for remote file data
    data = requests.get(file_url)

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Save file data to local copy
    with open('my_pic.jpg', 'wb') as file:
        file.write(data.content)
        img = cv2.imread('my_pic.jpg')
        faces = face_cascade.detectMultiScale(img, 1.1, 4)
        print(faces)
        if faces.any():
            out = {"bbox": json.dumps(faces.tolist())}
        else:
            out = {"bbox": None}
    return out

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
