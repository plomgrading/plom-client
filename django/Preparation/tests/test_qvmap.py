# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Edith Coates

from django.test import TestCase

from Preparation.services import PQVMappingService


class PQVMappingServiceTests(TestCase):
    fixtures = ["spec_created.json"]

    def test_num_to_produce(self):
        """
        Test that the created QV Map has the correct number of test-papers.
        """

        pqvs = PQVMappingService()
        self.assertFalse(pqvs.is_there_a_pqv_map())

        qvmap = pqvs.generate_and_set_pqvmap(1)
        print(qvmap)
