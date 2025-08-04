from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.mount("/images", StaticFiles(directory="generated_images"), name="images")

api_key = os.environ['API_KEY']

@app.post("/api/v1/generate_with_image")
async def generate_with_image(
    StoreName: str = Form(...),
    StoreIntroduce: str = Form(...),
    file: UploadFile = File(...)
):
    # 1. Groq 텍스트 생성
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
                
                '{StoreName}' 가게에 대해 '{StoreIntroduce}' 내용을 바탕으로 다음 조건에 맞는 간단하고 매력적인 소개 문장 하나를 문장형으로 작성해 주세요.

                10자 이내

                문장 끝은 '00입니다' 형태 금지

                문장에 ','가 있으면 쉼표 대신 줄바꿈 사용

                한국어로만 작성

                다른 문장이나 설명 없이 생성된 문장만 출력

                조건을 모두 정확히 지켜 주세요.""",
            }
        ],
        model="llama3-70b-8192",
    )
    result_text = chat_completion.choices[0].message.content.strip()

    # 2. 업로드된 이미지 읽기 및 500x500으로 리사이즈
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img = img.resize((500, 500))  # 사이즈 고정

    draw = ImageDraw.Draw(img)

    # 3. 폰트 설정 (한글폰트 경로 필요시 변경)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleGothic.ttf", 20)
    except:
        font = ImageFont.load_default()

    # 4. 텍스트 위치 계산 (왼쪽 하단)
    bbox = draw.textbbox((0, 0), result_text, font=font)
    text_height = bbox[3] - bbox[1]
    x = 10
    y = 500 - text_height - 10

    # 5. 텍스트 그리기
    draw.text((x, y), result_text, font=font, fill=(0, 0, 0))

    # 6. 이미지 저장
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
    save_path = f"generated_images/{filename}"
    img.save(save_path)

    # 7. URL 반환
    image_url = f"/images/{filename}"

    return JSONResponse(content={"result": result_text, "image_url": image_url})
