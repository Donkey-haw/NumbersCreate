import os
import json
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pdf_to_numbers import extract_pdf_pages, generate_numbers_from_images

app = FastAPI()

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...), 
    sheets_data: str = Form(...),
    doc_name: str = Form("Untitled")
    ):
    """
    Receives a PDF and a JSON string representing sheet mappings.
    Example sheets_data: '[{"name": "Sheet 1", "pages": [0, 1]}, {"name": "Sheet 2", "pages": [2]}]'
    """
    try:
        sheets_array = json.loads(sheets_data)
    except Exception:
        sheets_array = [{"name": "Sheet 1", "pages": []}]
        
    # Get unique pages across all sheets to extract them only once
    unique_pages = set()
    for s in sheets_array:
        for p in s.get("pages", []):
            unique_pages.add(p)
            
    # Use /tmp for all temporary processing
    temp_pdf_path = f"/tmp/temp_{file.filename}"
    with open(temp_pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    # Extract images as {page_idx: path, ...}
    img_dir = "/tmp/temp_pdf_images"
    image_paths = extract_pdf_pages(temp_pdf_path, pages=list(unique_pages), output_dir=img_dir)
    
    # Generate numbers file in /tmp
    output_numbers_name = f"output_{doc_name.replace(' ', '_')}.numbers"
    output_numbers_path = f"/tmp/{output_numbers_name}"
    generate_numbers_from_images(image_paths, output_numbers_path, sheets_array)
    
    # Clean up PDF and images
    if os.path.exists(temp_pdf_path):
        os.remove(temp_pdf_path)
    for p in image_paths.values():
        try: os.remove(p)
        except: pass
        
    return FileResponse(
        path=output_numbers_path,
        filename=output_numbers_name,
        media_type="application/x-iwork-numbers-sffnumbers"
    )

if __name__ == "__main__":
    import uvicorn
    # Render provides PORT environment variable
    port = int(os.environ.get("PORT", 7000))
    uvicorn.run(app, host="0.0.0.0", port=port)
