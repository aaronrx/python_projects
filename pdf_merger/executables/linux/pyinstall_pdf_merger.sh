#pyinstaller --add-data ../PyPDF2/*:PyPDF2 ../pdf_merger.py
pyinstaller --onefile --add-data ../../PyPDF2/*:PyPDF2 ../../pdf_merger.py

# Copy required files..
cp -r ../../files dist/

# Clean-up.
rm -rf ./build

echo "Executable: dist/pdf_merger"
