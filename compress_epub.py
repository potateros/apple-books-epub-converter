#!/usr/bin/env python3

import os
import sys
import zipfile
import shutil
import glob
import tempfile
from pathlib import Path

def compress_epub_folder(epub_folder_path, output_dir):
    """
    Compress an Apple Books .epub folder into a standard .epub file
    """
    os.makedirs(output_dir, exist_ok=True)
    epub_folder_path = Path(epub_folder_path)
    folder_name = epub_folder_path.name
    book_name = folder_name.replace('.epub', '')
    
    output_file_path = Path(output_dir) / f"{book_name}.epub"
    print(f"Processing: {epub_folder_path}")
    
    cover_file = None
    for ext in ['jpg', 'jpeg', 'png', 'gif']:
        potential_cover = epub_folder_path.parent / f"{book_name}.{ext}"
        if potential_cover.exists():
            cover_file = potential_cover
            break
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
      
        for item in epub_folder_path.glob('*'):
            dest = temp_dir_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
        
        if cover_file and not (temp_dir_path / cover_file.name).exists():
            shutil.copy2(cover_file, temp_dir_path)
            print(f"Added external cover: {cover_file.name}")
        
        mimetype_path = temp_dir_path / "mimetype"
        if not mimetype_path.exists():
            with open(mimetype_path, 'w') as f:
                f.write("application/epub+zip")
        
        with zipfile.ZipFile(output_file_path, 'w') as epub:
            epub.write(
                mimetype_path, 
                arcname="mimetype", 
                compress_type=zipfile.ZIP_STORED
            )
            
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file != "mimetype":
                        file_path = Path(root) / file
                        arcname = os.path.relpath(file_path, temp_dir)
                        epub.write(
                            file_path, 
                            arcname=arcname, 
                            compress_type=zipfile.ZIP_DEFLATED
                        )
    
    print(f"Created: {output_file_path}")
    return output_file_path

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory_containing_epub_folders>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = os.path.join(input_dir, "compressed_epubs")
    epub_folders = glob.glob(os.path.join(input_dir, "*.epub"))
    epub_folders = [f for f in epub_folders if os.path.isdir(f)]
    
    if not epub_folders:
        print(f"No .epub folders found in {input_dir}")
        sys.exit(1)
    
    for epub_folder in epub_folders:
        compress_epub_folder(epub_folder, output_dir)
    
    print(f"All .epub folders have been compressed to {output_dir}")

if __name__ == "__main__":
    main()
