"""
Process a single PDF with optional discussion points
Simple script for FCP integration - no AI needed
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.pdf_extractor import PDFExtractor
from app.services.pdf_filler import PDFFiller


def process_pdf(pdf_path: str, discussion_points: str = None, output_path: str = None):
    """
    Process a PDF and optionally add discussion points

    Args:
        pdf_path: Path to source Cashcalc PDF
        discussion_points: Optional discussion points text (can include \n for line breaks)
        output_path: Optional output path (defaults to same directory with _filled suffix)

    Returns:
        dict with status and output path
    """
    try:
        # Validate input
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            return {
                "success": False,
                "error": f"PDF file not found: {pdf_path}"
            }

        # Read source PDF
        with open(pdf_file, "rb") as f:
            pdf_bytes = f.read()

        # Extract data
        extractor = PDFExtractor()
        data = extractor.extract_data(pdf_bytes)

        # Fill template with discussion points
        filler = PDFFiller()
        filled_bytes = filler.fill_template(data, pdf_bytes, discussion_points)

        # Determine output path
        if not output_path:
            output_path = pdf_file.parent / f"{pdf_file.stem}_filled.pdf"
        else:
            output_path = Path(output_path)

        # Save output
        with open(output_path, "wb") as f:
            f.write(filled_bytes)

        return {
            "success": True,
            "output_path": str(output_path),
            "client_name": data.client_info.full_name,
            "file_size_kb": len(filled_bytes) / 1024
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python process_single_pdf.py <pdf_path> [discussion_points] [output_path]")
        print()
        print("Examples:")
        print('  python process_single_pdf.py "path/to/source.pdf"')
        print('  python process_single_pdf.py "path/to/source.pdf" "Some notes here"')
        print('  python process_single_pdf.py "path/to/source.pdf" "Notes" "output.pdf"')
        print()
        print("For JSON input/output:")
        print('  python process_single_pdf.py --json \'{"pdf_path":"path.pdf","discussion_points":"notes"}\'')
        sys.exit(1)

    # JSON mode
    if sys.argv[1] == "--json":
        json_input = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        params = json.loads(json_input)
        result = process_pdf(
            params.get("pdf_path"),
            params.get("discussion_points"),
            params.get("output_path")
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    # Regular mode
    pdf_path = sys.argv[1]
    discussion_points = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    result = process_pdf(pdf_path, discussion_points, output_path)

    if result["success"]:
        print(f"✅ Success!")
        print(f"   Client: {result['client_name']}")
        print(f"   Output: {result['output_path']}")
        print(f"   Size: {result['file_size_kb']:.1f} KB")
    else:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
