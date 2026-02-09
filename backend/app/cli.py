import argparse
import os

from backend.app.converters.pdf_to_word.no_ocr import pdf_to_word_no_ocr


def parse_pages(pages_str):
    if pages_str == "all":
        return None

    pages = set()

    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            pages.update(range(int(start), int(end) + 1))
        else:
            pages.add(int(part))

    return pages


def main():
    parser = argparse.ArgumentParser(
        description="PDF to Word Converter (No OCR)"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    parser.add_argument(
        "--mode",
        choices=["semantic", "layout", "form", "auto"],
        default="semantic"
    )

    parser.add_argument(
        "--report",
        help="Path to JSON report file (optional)"
    )

    parser.add_argument(
        "--pages",
        default="all",
        help="Pages to process (e.g. 1-3, 2,5,7, all)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file not found: {args.input}")

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    pages = parse_pages(args.pages)

    pdf_to_word_no_ocr(
        input_pdf_path=args.input,
        output_docx_path=args.output,
        mode=args.mode,
        report_path=args.report,
        pages=pages
    )

    print(f"✅ Conversion finished ({args.mode} mode)")
    print(f"📄 Output saved to: {args.output}")

    if args.report:
        print(f"🧠 Decision report saved to: {args.report}")


if __name__ == "__main__":
    main()
