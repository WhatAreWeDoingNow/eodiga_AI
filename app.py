from fastapi import FastAPI
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
from fastapi.responses import StreamingResponse
import io, os

app = FastAPI()

from dotenv import load_dotenv
load_dotenv()

api_key = os.environ['API_KEY']

@app.post("/api/v1/generate")
def text_generate(StoreName: str, StoreIntroduce: str):
    # 1. 텍스트 생성
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"다른말은 더 붙이지말고 생성된 텍스트만 보내줘. 한국어로만 작성해줘. '{StoreName}'라는 가게에 대해 '{StoreIntroduce}'를 바탕으로 **20자** 이내의 간단하고 매력적인 소개 문장을 작성해줘. 단, '00입니다' 형태로 끝내지 마.  만약 문장에 ',' 이 있으면 줄바꿈을 해줘",
            }
        ],
        model="llama3-70b-8192",
    )
    result_text = chat_completion.choices[0].message.content.strip()

    # 2. 이미지 생성
    img = Image.new("RGB", (500, 500), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 한글 폰트가 필요하면 폰트 경로 변경 (예: 나눔고딕)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleGothic.ttf", 20)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), result_text, font=font)
    text_height = bbox[3] - bbox[1]

    x = 10
    y = 500 - text_height - 10
    draw.text((x, y), result_text, font=font, fill=(0, 0, 0))

    # 3. 이미지 응답
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return StreamingResponse(img_bytes, media_type="image/png")
    #return {"RESULT" : result_text}
