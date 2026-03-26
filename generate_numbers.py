import argparse
from numbers_parser import Document

def main():
    parser = argparse.ArgumentParser(description="Modify Geometry (position & size) of objects in a Numbers file.")
    parser.add_argument("input_file", help="Input .numbers file")
    parser.add_argument("output_file", nargs='?', help="Output .numbers file")
    parser.add_argument("--id", type=int, help="Object ID to modify (if known). If omitted, lists available objects with geometry.")
    parser.add_argument("--x", type=float, help="New X position")
    parser.add_argument("--y", type=float, help="New Y position")
    parser.add_argument("--w", type=float, help="New Width")
    parser.add_argument("--h", type=float, help="New Height")
    
    args = parser.parse_args()
    
    doc = Document(args.input_file)
    model = doc._model
    
    if args.id is None:
        print("No --id specified. Listing objects with geometry:")
        count = 0
        for obj_id, obj in model.objects._objects.items():
            if hasattr(obj, 'super') and hasattr(obj.super, 'geometry'):
                geom_archive = obj.super.geometry
                if geom_archive:
                    print(f"ID: {obj_id:6d} | Type: {type(obj).__name__:15} | x: {geom_archive.position.x:6.1f}, y: {geom_archive.position.y:6.1f} | w: {geom_archive.size.width:6.1f}, h: {geom_archive.size.height:6.1f}")
                    count += 1
        print(f"\nTotal {count} objects.")
        print(f"Run again with: python generate_numbers.py '{args.input_file}' <output_file> --id <ID> [--x X] [--y Y] [--w W] [--h H]")
        return
        
    if not args.output_file:
        print("Error: output_file is required when --id is specified.")
        parser.print_help()
        return

    obj = model.objects._objects.get(args.id)
    if not obj:
        print(f"Error: Object ID {args.id} not found.")
        return
        
    if not (hasattr(obj, 'super') and hasattr(obj.super, 'geometry') and obj.super.geometry):
        print(f"Error: Object ID {args.id} does not have a GeometryArchive.")
        return
        
    geom_archive = obj.super.geometry
    print(f"Modifying Object ID {args.id} ({type(obj).__name__}):")
    print(f"  Old x,y: {geom_archive.position.x:.2f}, {geom_archive.position.y:.2f}")
    print(f"  Old w,h: {geom_archive.size.width:.2f}, {geom_archive.size.height:.2f}")
    
    if args.x is not None: geom_archive.position.x = args.x
    if args.y is not None: geom_archive.position.y = args.y
    if args.w is not None: geom_archive.size.width = args.w
    if args.h is not None: geom_archive.size.height = args.h
    
    print(f"  New x,y: {geom_archive.position.x:.2f}, {geom_archive.position.y:.2f}")
    print(f"  New w,h: {geom_archive.size.width:.2f}, {geom_archive.size.height:.2f}")
    
    print(f"Saving to '{args.output_file}'...")
    doc.save(args.output_file)
    print("Done!")

if __name__ == "__main__":
    main()
