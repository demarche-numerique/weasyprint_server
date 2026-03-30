import json
import os
import http.server
import socketserver
import threading
from unittest import TestCase
from unittest.mock import patch
from src.app import create_app


PORT = 8000


class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/main.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            self.wfile.write(b"body { background-color: #f0f0f0; }")
        else:
            # Pour toute autre URL, renvoie un 404 Not Found
            self.send_error(404, "File not found.")


class TestIntegrations(TestCase):
    @classmethod
    def setUpClass(cls):
        handler = SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address = True
        cls.httpd = socketserver.TCPServer(("", PORT), handler, bind_and_activate=True)

        # Lance le serveur dans un thread séparé
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        cls.app = create_app({"BASE_URL": f"http://localhost:{PORT}/"}).test_client()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.server_thread.join()
        print("Serveur arrêté")

    def test_simple_generation(self):
        html = '<link rel="stylesheet" type="text/css" href="main.css" /> <h1>Hello, world!</h1>'
        data = {"html": html}

        response = self.app.post(
            "/pdf",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertEqual(
            response.headers["Content-Disposition"], "inline;filename=fichier"
        )

    def test_failing_generation_caused_by_missing_assets(self):
        html = '<link rel="stylesheet" type="text/css" href="missing.css" /> <h1>Hello, world!</h1>'
        data = {"html": html}

        response = self.app.post(
            "/pdf",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.get_json(), {"error": "an asset is missing"})

    def test_generation_crash_returns_500(self):
        def crashing_worker(html_string, base_url, queue):
            os.abort()

        with patch("src.app._pdf_worker", crashing_worker):
            response = self.app.post(
                "/pdf",
                data=json.dumps({"html": "<h1>test</h1>"}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "pdf generation crashed"})
