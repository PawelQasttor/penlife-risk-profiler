"""
Process PDFs from Google Cloud Storage with optional discussion points
Supports local paths and GCS paths (gs://bucket/path/to/file.pdf)
"""

import sys
import json
from pathlib import Path
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent))

from app.services.pdf_extractor import PDFExtractor
from app.services.pdf_filler import PDFFiller

# Google Cloud Storage support (optional - only imported if needed)
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False


def download_from_gcs(gcs_path: str) -> bytes:
    """Download file from Google Cloud Storage"""
    if not GCS_AVAILABLE:
        raise ImportError("google-cloud-storage not installed. Run: pip install google-cloud-storage")

    # Parse gs://bucket/path/to/file.pdf
    if not gcs_path.startswith("gs://"):
        raise ValueError(f"Invalid GCS path: {gcs_path}. Must start with gs://")

    path_parts = gcs_path[5:].split("/", 1)
    bucket_name = path_parts[0]
    blob_path = path_parts[1] if len(path_parts) > 1 else ""

    # Download
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    return blob.download_as_bytes()


def upload_to_gcs(gcs_path: str, data: bytes) -> str:
    """Upload file to Google Cloud Storage"""
    if not GCS_AVAILABLE:
        raise ImportError("google-cloud-storage not installed. Run: pip install google-cloud-storage")

    # Parse gs://bucket/path/to/file.pdf
    if not gcs_path.startswith("gs://"):
        raise ValueError(f"Invalid GCS path: {gcs_path}. Must start with gs://")

    path_parts = gcs_path[5:].split("/", 1)
    bucket_name = path_parts[0]
    blob_path = path_parts[1] if len(path_parts) > 1 else ""

    # Upload
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(data, content_type="application/pdf")

    return gcs_path


def process_pdf(pdf_path: str, discussion_points: str = None, output_path: str = None):
    """
    Process a PDF with optional discussion points
    Supports local paths and Google Cloud Storage paths (gs://)

    Args:
        pdf_path: Path to source PDF (local or gs://bucket/path)
        discussion_points: Optional discussion points text (use \n for line breaks)
        output_path: Output path (local or gs://bucket/path). If not provided,
                    adds _filled suffix to input path

    Returns:
        dict with status and output path
    """
    try:
        # Read source PDF
        is_gcs_input = pdf_path.startswith("gs://")

        if is_gcs_input:
            print(f"Downloading from GCS: {pdf_path}")
            pdf_bytes = download_from_gcs(pdf_path)
        else:
            # Local file
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                return {
                    "success": False,
                    "error": f"PDF file not found: {pdf_path}"
                }
            with open(pdf_file, "rb") as f:
                pdf_bytes = f.read()

        print(f"Processing PDF ({len(pdf_bytes) / 1024:.1f} KB)...")

        # Extract data
        extractor = PDFExtractor()
        data = extractor.extract_data(pdf_bytes)

        print(f"Extracted data for: {data.client_info.full_name}")

        # Fill template with discussion points
        filler = PDFFiller()
        filled_bytes = filler.fill_template(data, pdf_bytes, discussion_points)

        print(f"Generated filled PDF ({len(filled_bytes) / 1024:.1f} KB)")

        # Determine output path
        if not output_path:
            if is_gcs_input:
                # Add _filled before .pdf extension for GCS
                output_path = pdf_path.replace(".pdf", "_filled.pdf")
            else:
                # Local file
                pdf_file = Path(pdf_path)
                output_path = str(pdf_file.parent / f"{pdf_file.stem}_filled.pdf")

        # Save output
        is_gcs_output = output_path.startswith("gs://")

        if is_gcs_output:
            print(f"Uploading to GCS: {output_path}")
            upload_to_gcs(output_path, filled_bytes)
        else:
            # Local file
            output_file = Path(output_path)
            with open(output_file, "wb") as f:
                f.write(filled_bytes)

        return {
            "success": True,
            "output_path": output_path,
            "client_name": data.client_info.full_name,
            "file_size_kb": len(filled_bytes) / 1024,
            "storage_type": "gcs" if is_gcs_output else "local"
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python process_with_gcs.py <pdf_path> [discussion_points] [output_path]")
        print()
        print("PDF path can be:")
        print("  - Local file: C:/path/to/file.pdf")
        print("  - Google Cloud Storage: gs://bucket-name/path/to/file.pdf")
        print()
        print("Examples:")
        print('  python process_with_gcs.py "gs://my-bucket/source.pdf"')
        print('  python process_with_gcs.py "gs://my-bucket/input.pdf" "Discussion notes"')
        print('  python process_with_gcs.py "gs://bucket/in.pdf" "Notes" "gs://bucket/out.pdf"')
        print()
        print("For JSON input/output:")
        print('  python process_with_gcs.py --json \'{"pdf_path":"gs://...","discussion_points":"..."}\'')
        print()
        print("Note: Requires google-cloud-storage package")
        print("      pip install google-cloud-storage")
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
        print(f"\n✅ Success!")
        print(f"   Client: {result['client_name']}")
        print(f"   Output: {result['output_path']}")
        print(f"   Size: {result['file_size_kb']:.1f} KB")
        print(f"   Storage: {result['storage_type']}")
    else:
        print(f"\n❌ Error: {result['error']}")
        if "traceback" in result:
            print(f"\n{result['traceback']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
