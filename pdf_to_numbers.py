from concurrent.futures import ThreadPoolExecutor

def extract_pdf_pages(pdf_path, pages=None, output_dir="/tmp/pdf_images", dpi=120):
    """
    Extracts specified pages from a PDF as images in parallel for speed. 
    If pages is None, extracts all pages.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    if pages is None:
        pages = list(range(len(doc)))
    
    def render_page(p_idx):
        if p_idx < 0 or p_idx >= len(doc): return None
        # Use a fresh document handle per thread for safety in some PyMuPDF versions
        thread_doc = fitz.open(pdf_path)
        page = thread_doc.load_page(p_idx)
        pix = page.get_pixmap(dpi=dpi)
        img_path = os.path.join(output_dir, f"page_{p_idx}.png")
        pix.save(img_path)
        thread_doc.close()
        return p_idx, img_path

    image_paths = {}
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(render_page, pages))
        for res in results:
            if res:
                p_idx, path = res
                image_paths[p_idx] = path
                
    doc.close()
    return image_paths

def generate_numbers_from_images(image_paths, output_path, sheets_data):
    """
    Takes a dictionary mapping page_idx to image paths, and generates a .numbers file 
    with images arranged in a 2-column downward grid per sheet.
    sheets_data: [{"name": "...", "pages": [...]}, ...]
    """
    doc = Document()
    
    # Layout parameters
    w = 400.0
    h = 560.0
    spacing_x = 20.0
    spacing_y = 20.0
    start_x = 50.0
    start_y = 50.0
    
    # Ensure there are enough sheets created
    while len(doc.sheets) < len(sheets_data):
        doc.add_sheet()
        
    for s_idx, sheet_info in enumerate(sheets_data):
        sheet = doc.sheets[s_idx]
        sheet.name = sheet_info.get("name", f"Sheet {s_idx+1}")
        
        # Hide the default grid table on this newly generated or default sheet
        default_table = sheet.tables[0]
        default_table.name = f"HiddenBase_{s_idx}"
        default_table.table_name_enabled = False
        try: 
            default_table.num_header_rows = 0
            default_table.num_header_cols = 0
        except: 
            pass
        while default_table.num_rows > 1: default_table.delete_row(1)
        while default_table.num_cols > 1: default_table.delete_column(1)
        default_table.col_width(0, 1)
        default_table.row_height(0, 1)
        
        pages_array = sheet_info.get("pages", [])
        
        for i, page_idx in enumerate(pages_array):
            if page_idx not in image_paths: continue
            img_path = image_paths[page_idx]
            
            row = i // 2
            col = i % 2
            
            pos_x = start_x + col * (w + spacing_x)
            pos_y = start_y + row * (h + spacing_y)
            
            with open(img_path, "rb") as f:
                img_data = f.read()
                
            img_style = doc.add_style(
                name=f"PhotoStyle_{s_idx}_{i}", 
                bg_image=BackgroundImage(img_data, os.path.basename(img_path))
            )
            
            photo_tbl = sheet.add_table(
                table_name=f"Image_{s_idx}_{i}",
                x=pos_x, y=pos_y,
                num_rows=1, num_cols=1, num_header_rows=0, num_header_cols=0
            )
            photo_tbl.table_name_enabled = False
            photo_tbl.write(0, 0, "", style=img_style)
            photo_tbl.col_width(0, int(w))
            photo_tbl.row_height(0, int(h))
            
    doc.save(output_path)
    print(f"Generated {output_path} successfully!")

if __name__ == "__main__":
    # Test execution
    # extract_pdf_pages("sample.pdf", [0, 1, 2])
    pass
