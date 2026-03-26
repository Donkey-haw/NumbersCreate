import os
import argparse
from numbers_parser import Document
from numbers_parser.cell import BackgroundImage

def main():
    parser = argparse.ArgumentParser(description="Generate a cross-platform Numbers file with dynamic sheets and photos.")
    parser.add_argument("output_file", help="Output .numbers file path")
    parser.add_argument("--sheets", type=int, default=3, help="Number of sheets")
    parser.add_argument("--photos", type=int, default=2, help="Photos per sheet")
    parser.add_argument("--image", type=str, required=True, help="Image file to use")
    args = parser.parse_args()
    
    with open(args.image, "rb") as f: img_data = f.read()

    doc = Document()
    img_style = doc.add_style(name="PhotoStyle", bg_image=BackgroundImage(img_data, os.path.basename(args.image)))
    
    while len(doc.sheets) < args.sheets: doc.add_sheet()
        
    for s_idx in range(args.sheets):
        sheet = doc.sheets[s_idx]
        sheet.name = f"Sheet {s_idx + 1}"
        
        # Transform the default table into the first photo
        default_table = sheet.tables[0]
        default_table.name = f"Image_1_{s_idx}"
        default_table.table_name_enabled = False
        default_table.num_header_rows = 0
        default_table.num_header_cols = 0
        while default_table.num_rows > 1: default_table.delete_row(1)
        while default_table.num_cols > 1: default_table.delete_column(1)
            
        if args.photos > 0:
            default_table.write(0, 0, "", style=img_style)
            default_table.col_width(0, 300)
            default_table.row_height(0, 300)
        else:
            default_table.col_width(0, 1)
            default_table.row_height(0, 1)
            
        for p_idx in range(1, args.photos):
            photo_tbl = sheet.add_table(
                table_name=f"Image_{p_idx+1}_{s_idx}",
                x=50.0 + (p_idx * 350.0), y=50.0,
                num_rows=1, num_cols=1, num_header_rows=0, num_header_cols=0
            )
            photo_tbl.table_name_enabled = False
            photo_tbl.write(0, 0, "", style=img_style)
            photo_tbl.col_width(0, 300)
            photo_tbl.row_height(0, 300)

    doc.save(args.output_file)
    print(f"Success: {args.output_file}")

if __name__ == "__main__":
    main()
