import unittest

from app.workers.tasks import build_failure_result_data


class BuildFailureResultDataTests(unittest.TestCase):
    def test_invalid_url_payload_is_marked_as_invalid_url(self) -> None:
        payload = build_failure_result_data("Invalid URL format", error_type="invalid_url")

        self.assertTrue(payload["error"])
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["error_type"], "invalid_url")
        self.assertEqual(payload["message"], "Invalid URL format")

    def test_server_error_payload_is_marked_as_server_error(self) -> None:
        payload = build_failure_result_data("Unexpected server error", error_type="server_error")

        self.assertTrue(payload["error"])
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["error_type"], "server_error")
        self.assertEqual(payload["message"], "Unexpected server error")


if __name__ == "__main__":
    unittest.main()
