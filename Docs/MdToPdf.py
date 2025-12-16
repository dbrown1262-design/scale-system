import os
import pypandoc

# Always run from the folder where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Full path to pdflatex.exe
PDF_ENGINE = r"C:\Users\dave\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"

SOURCE_MD = "Harvesting SOP.md"
OUTPUT_PDF = "Harvesting SOP.pdf"

pypandoc.convert_file(
    SOURCE_MD,
    "pdf",
    outputfile=OUTPUT_PDF,
    extra_args=[
    f"--pdf-engine={PDF_ENGINE}",
    "-V", "fontsize=12pt", 
    "-V", "geometry:margin=1.0in"
    ]

)

print("PDF created:", os.path.join(SCRIPT_DIR, OUTPUT_PDF))

