import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from capabilities.external_authorization import ExternalAuthorization


class ExternalAuthorizationTests(unittest.TestCase):

    def test_unauthorized_request_is_rejected(self):
        authorization = ExternalAuthorization()

        request = {
            "operation": "focus",
            "title": "Blender",
        }

        self.assertFalse(
            authorization.consume("desktop", request)
        )

    def test_authorized_request_is_consumed_once(self):
        authorization = ExternalAuthorization()

        request = {
            "operation": "focus",
            "title": "Blender",
        }

        self.assertTrue(
            authorization.authorize("desktop", request)
        )

        self.assertTrue(
            authorization.consume("desktop", request)
        )

        self.assertFalse(
            authorization.consume("desktop", request)
        )

    def test_authorization_is_specific_to_request(self):
        authorization = ExternalAuthorization()

        focus_request = {
            "operation": "focus",
            "title": "Blender",
        }

        other_request = {
            "operation": "focus",
            "title": "Firefox",
        }

        authorization.authorize(
            "desktop",
            focus_request,
        )

        self.assertTrue(
            authorization.consume(
                "desktop",
                focus_request,
            )
        )

        self.assertFalse(
            authorization.consume(
                "desktop",
                other_request,
            )
        )


if __name__ == "__main__":
    unittest.main()