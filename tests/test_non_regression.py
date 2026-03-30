import os
from unittest import TestCase
from weasyprint import HTML
from src.custom_fetcher import CustomURLFetcher

fixtures_dir = "tests/fixtures"
output_dir = "tmp"

os.makedirs(output_dir, exist_ok=True)


class TestIntegrations(TestCase):
    # NOTE: App server must run in order to fetch assets.
    def test_non_regression(self):
        if "CI" in os.environ:
            self.skipTest(
                "Skipping non-regression test in CI: app server assets must run."
            )

        # Iterate through each HTML file in the fixtures directory
        for filename in os.listdir(fixtures_dir):
            if filename.endswith(".html"):
                html_file_path = os.path.join(fixtures_dir, filename)

                # Load HTML content
                with open(html_file_path, "r", encoding="utf-8") as f:
                    string_html = f.read()

                # Generate PDF.
                html = HTML(
                    string=string_html,
                    base_url=os.environ.get("BASE_URL"),
                    url_fetcher=CustomURLFetcher(),
                )

                pdf = html.write_pdf()

                # Define output PDF file path
                pdf_filename = filename.replace(".html", ".pdf")

                # Save the PDF to the specified directory
                pdf_file_path = os.path.join(output_dir, pdf_filename)
                with open(pdf_file_path, "wb") as f:
                    f.write(pdf)

                print(
                    f"Non regression PDF generated: {pdf_file_path}, compare it with reference"
                )
