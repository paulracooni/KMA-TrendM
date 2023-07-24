import pyrootutils

DIR_ROOT = pyrootutils.setup_root(__file__)

import unittest

from models import GptResult


class Classifier_Test(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_run(self):

        pass
