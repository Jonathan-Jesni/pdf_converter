import argparse
import os

from backend.app.converters.pdf_to_word.no_ocr import pdf_to_word_no_ocr


def main():
    parser = argparse.ArgumentParser(
        description="PDF to Word Converter (No OCR)"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input PDF file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output DOCX file"
    )

    parser.add_argument(
        "--mode",
        choices=["semantic", "layout", "form"],
        default="semantic",
        help="Conversion mode (default: semantic)"
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    mode = args.mode

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf_to_word_no_ocr(
        input_pdf_path=input_path,
        output_docx_path=output_path,
        mode=mode
    )

    print(f"✅ Conversion finished ({mode} mode)")
    print(f"📄 Output saved to: {output_path}")


if __name__ == "__main__":
    main()
