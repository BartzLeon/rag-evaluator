from giskard.rag import QATestset
from app.testset_loader.testset_loader import TestSetLoader
import os

class QATestsetLoader(TestSetLoader):
    def load(self) -> QATestset:
        return QATestset.load(self.testset_path)