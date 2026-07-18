#!/usr/bin/env python3

from __future__ import annotations

import unittest

from validate_draft import validate_cta_policy


class ConfirmedCtaTests(unittest.TestCase):
    def test_unknown_cta_requires_placeholder(self) -> None:
        self.assertEqual(
            validate_cta_policy("[CTA — НУЖНО ПОДТВЕРДИТЬ]", {"confirmed_facts": {}}),
            [],
        )

    def test_confirmed_cta_replaces_placeholder(self) -> None:
        cta = "«vibe» в комменты — скинем детали"
        self.assertEqual(
            validate_cta_policy(cta, {"confirmed_facts": {"cta": cta}}),
            [],
        )

    def test_confirmed_cta_must_be_exact(self) -> None:
        cta = "«vibe» в комменты — скинем детали"
        errors = validate_cta_policy(
            "напишите vibe",
            {"confirmed_facts": {"cta": cta}},
        )
        self.assertIn("exact confirmed CTA is missing from public copy", errors)


if __name__ == "__main__":
    unittest.main()
