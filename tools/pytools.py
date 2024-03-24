from PIL import Image
from io import BytesIO
import base64
from translate import Translator
import re
from random import randint
import uuid
from pydantic import BaseModel
from fastapi import UploadFile, File
from typing import Union
import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent

tr = Translator(to_lang="id", from_lang= "en")


def regexrepl(string, repl):
    string = re.sub(r'[A-Za-z]*:[A-Za-z\/\;0-9]*,', repl, string).strip()

    return string

def randomname():
    return str(uuid.uuid4())

def openImageFromBase64(base64byt:str):
    base64byt = regexrepl(base64byt, "")
    if " HTTP/1.1" in base64byt:
        base64byt = base64byt.replace(" HTTP/1.1", "")

    return Image.open(BytesIO(base64.b64decode(base64byt)))


def imgCaptioning(processor, model, b64str, saveImg = False):
    text = "Photography of cooking ingridients that by specific base material includes "
    rimg = openImageFromBase64(b64str).convert("RGB")
    
    if saveImg:
        rimg.save(rf"./tmp/f{randomname()}.jpg")
    
    inputs = processor(rimg, text, return_tensors="pt")

    out = model.generate(**inputs, max_length=200)
    txt = processor.decode(out[0], skip_special_tokens=True)
    cmp = re.compile(re.escape(text), re.IGNORECASE)
    txt = cmp.sub("", txt)
    return tr.translate(txt)

def getRecipees(search: str = "ayam panggang"):
    ua = UserAgent()
    hasil = []
    try:
        res = requests.get(f"https://cookpad.com/id/cari/{search.replace(' ' , '+')}", headers= {"User-Agent": ua.random})

        bsoup = bs(res.text, "html.parser")

        alldata = bsoup.find("div", {"class":"lg:items-start"}).find_all("li")
        
        for i in alldata:
            dt = i.find("a", {"class": "block-link__main"})
            img = i.find("div", {"class":"relative"})
            img = img.find("picture").find("img") if img else None
            ingri = i.find("div", {"data-ingredients-highlighter-target": "ingredients"})
            ingri = ingri.text.strip() if ingri else None
            if dt and img:
                hasil.append({
                    "title" : dt.text.strip(),
                    "href" : f"https://www.cookpad.com{dt['href']}",
                    "img": img['src'].replace("130x160cq50","512x512cq50"),
                    "ingri": ingri
                    })

        if len(hasil) < 1:
            return {
                "status_code": res.status_code,
                "msg": "error",
                "hasil": "Tidak ada hasil yang ditemukan"
            }
        
        return {
            "status_code": res.status_code,
            "msg": "success",
            "hasil": hasil
        }
    except:
        return {
                "status_code": 404,
                "msg": "error",
                "hasil": "Tidak ada hasil yang ditemukan"
            }
