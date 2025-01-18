from abc import abstractmethod, ABC

class TestSetLoader(ABC):
    def __init__(self, testset_path):
        self.testset_path = testset_path

    @abstractmethod
    def load(self):
        pass