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
    import uuid
    # Create a unique work directory for this specific request
    request_id = str(uuid.uuid4())
    work_dir = os.path.join("/tmp", request_id)
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        sheets_array = json.loads(sheets_data)
    except Exception:
        sheets_array = [{"name": "Sheet 1", "pages": []}]
        
    # Get unique pages
    unique_pages = set()
    for s in sheets_array:
        for p in s.get("pages", []):
            unique_pages.add(p)
            
    # Save uploaded PDF to unique work dir
    temp_pdf_path = os.path.join(work_dir, f"input_{file.filename}")
    print(f"[DEBUG] Saving PDF to: {temp_pdf_path}")
    with open(temp_pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    # Extract images to unique subdirectory
    img_dir = os.path.join(work_dir, "images")
    print(f"[DEBUG] Extracting images to: {img_dir}")
    image_paths = extract_pdf_pages(temp_pdf_path, pages=list(unique_pages), output_dir=img_dir)
    print(f"[DEBUG] Total images extracted: {len(image_paths)}")
    
    # Generate numbers file in isolated dir
    output_numbers_name = f"{doc_name.replace(' ', '_')}.numbers"
    output_numbers_path = os.path.join(work_dir, output_numbers_name)
    print(f"[DEBUG] Generating Numbers file at: {output_numbers_path}")
    generate_numbers_from_images(image_paths, output_numbers_path, sheets_array)
    print(f"[DEBUG] Generation complete.")
    
    # We use BackgroundTasks or just return and clean up? 
    # FileResponse needs the file to exist. 
    # A better pattern is to return the file and then clean up.
    # But FastAPI's FileResponse doesn't delete automatically.
    
    return FileResponse(
        path=output_numbers_path,
        filename=output_numbers_name,
        media_type="application/x-iwork-numbers-sffnumbers"
    )

# Note: In a production environment with many users, 
# you might want a background task to periodically clean up /tmp folders
# or use a specialized FileResponse that deletes on completion.

if __name__ == "__main__":
    import uvicorn
    # Render provides PORT environment variable
    port = int(os.environ.get("PORT", 7000))
    uvicorn.run(app, host="0.0.0.0", port=port)
