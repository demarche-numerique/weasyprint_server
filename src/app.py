import os
import sys
from flask import Flask, request, make_response
from werkzeug.exceptions import HTTPException
from weasyprint import HTML
from weasyprint.urls import FatalURLFetchingError
import sentry_sdk
from .custom_fetcher import CustomURLFetcher
from .logger import ERROR_LOGGER, ACCESS_LOGGER
import time
import json
import datetime


def before_send(event, _hint):
    # Redact the request data to avoid sending sensitive information
    if "request" in event and "data" in event["request"]:
        event["request"]["data"] = "REDACTED"
    return event


if os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        enable_tracing=True,
        traces_sample_rate=1.0,
        before_send=before_send,
    )


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        try:
            app.config["BASE_URL"] = os.environ["BASE_URL"]
        except KeyError:
            print("missing BASE_URL env var to fetch the assets (css, images ...)")
            sys.exit(1)
    else:
        app.config.from_mapping(test_config)

    @app.errorhandler(Exception)
    def handle_exception(e):
        ERROR_LOGGER.error("An error occurred", exc_info=e)

        if isinstance(e, HTTPException):
            return e

        return make_response({"error": str(e)}, 500)

    @app.route("/pdf", methods=["POST"])
    def pdf():
        request_data = request.get_json()
        string_html = request_data["html"]
        html = HTML(
            string=string_html,
            base_url=app.config["BASE_URL"],
            url_fetcher=CustomURLFetcher(),
        )
        try:
            generated_pdf = html.write_pdf()
        except FatalURLFetchingError:
            sentry_sdk.capture_message("An asset is missing")
            return make_response({"error": "an asset is missing"}, 500)

        response = make_response(generated_pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "inline;filename=fichier"
        return response

    @app.route("/ping", methods=["GET"])
    def ping():
        if os.path.isfile("maintenance"):
            return make_response({}, 404)

        return make_response({}, 200)

    @app.before_request
    def before_request():
        request.start_time = time.perf_counter()

    @app.after_request
    def after_request(response):
        if request.endpoint == "ping":
            return response

        now = datetime.datetime.now().isoformat()
        to_log = {"time": now, "code": response.status_code}

        if hasattr(request, "start_time"):
            to_log["duration"] = int((time.perf_counter() - request.start_time) * 1000)

        if request.content_type == "application/json":
            request_data = request.get_json()
            to_log["upstream_context"] = request_data.get("upstream_context")

            if os.environ.get("DUMP_NON_REG_FIXTURES"):
                fixtures_dir = "tests/fixtures"
                procedure_id = request_data["upstream_context"]["procedure_id"]
                html_file_path = os.path.join(
                    fixtures_dir, f"procedure-{procedure_id}.html"
                )
                with open(html_file_path, "w") as html_file:
                    html_file.write(request_data["html"])

                pdf_file_path = os.path.join(
                    fixtures_dir, f"procedure-{procedure_id}.pdf"
                )
                html = HTML(
                    string=request_data["html"],
                    base_url=app.config["BASE_URL"],
                    url_fetcher=CustomURLFetcher(),
                )
                with open(pdf_file_path, "wb") as f:
                    f.write(html.write_pdf())
                print(f"New reference PDF saved: {pdf_file_path}")

        if request.headers.get("X-Request-Id"):
            to_log["request_id"] = request.headers.get("X-Request-Id")

        to_log = {k: v for k, v in to_log.items() if v is not None}

        ACCESS_LOGGER.info(json.dumps(to_log))
        return response

    return app
