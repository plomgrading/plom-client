# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Edith Coates

from django.test import TestCase

from Demo.services import ServerConfigService, PlomConfigError


class ServerConfigTests(TestCase):
    """Tests for Demo.ServerConfigService."""

    def test_bad_keys(self):
        """Test the config validation function with unrecognized keys."""
        valid_config = {
            "num_to_produce": 8,
            "test_spec": "demo",
        }
        ServerConfigService().validate_config(valid_config)

        invalid_config = {
            "n_to_produce": 7,
            "test_spec": "demo",
        }

        with self.assertRaises(PlomConfigError):
            ServerConfigService().validate_config(invalid_config)

    def test_bundle_bad_keys(self):
        """Test the config validation with unrecognized keys in bundles."""
        valid_bundle = {
            "first_paper": 1,
            "last_paper": 1,
        }
        valid_hw_bundle = {
            "paper_number": 1,
            "pages": [[1], [2], [3]],
        }

        scs = ServerConfigService()
        scs.validate_bundle(valid_bundle)
        scs.validate_hw_bundle(valid_hw_bundle)

        invalid_bundle = {
            "frist_paper": 1,
            "last_paper": 5,
        }
        invalid_hw_bundle = {
            "papers": 1,
        }

        with self.assertRaises(PlomConfigError):
            scs.validate_bundle(invalid_bundle)

        with self.assertRaises(PlomConfigError):
            scs.validate_hw_bundle(invalid_hw_bundle)
