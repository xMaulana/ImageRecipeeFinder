# import requests
# from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import Annotated, List

import uvicorn
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from starlette.middleware.sessions import SessionMiddleware
scopes = [
  "https://www.googleapis.com/auth/userinfo.email",
  "https://www.googleapis.com/auth/firebase.database"
]


from tools.pytools import imgCaptioning, randomname, openImageFromBase64, regexrepl, getRecipees
# from tools.session import backend, verifier, cookie

processor = BlipProcessor.from_pretrained("./model",local_files_only=True)
model = BlipForConditionalGeneration.from_pretrained("./model", local_files_only=True)

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static",StaticFiles(directory="public"), name = "public")

@app.post("/getImageCaption")
def getData(filename = Form(...), filedata = Form(...)):
    hasil = imgCaptioning(processor, model, filedata)
    return {"caption" : hasil}

@app.get("/getRecipees")
def getRecipee(bahan: str = None, creds: str = None):
    if bahan == None:
        return {
            "msg": "Gagal mencari, bahan kosong",
            "data": []
        }
    

    print(bahan)
    
    return {"hasil": getRecipees(bahan)}

@app.get("/bookmark")
def bookmark(request:Request):
    return templates.TemplateResponse(
        "bookmark.html", context={"request": request}
    )

@app.get("/home", response_class=HTMLResponse)
def home(request: Request, token:str= None):
    return templates.TemplateResponse(
    "home.html", context={"request": request}
    )

@app.get("/", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(
    "index.html", context={"request": request}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
