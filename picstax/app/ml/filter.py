from abc import ABC, abstractmethod

from app.view.layout import Layout


class Filter(ABC):
    def __init__(self, layout: Layout, filter_name: str):
        self.layout = layout
        self.filter_name = filter_name
        self.register_filter()
        self.initialize()

    @abstractmethod
    def register_filter(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def apply_filter(self, frame):
        pass

    def log_selection(self):
        self.layout.log_filter_selection(self.filter_name)

    def log_completion(self):
        self.layout.log_filter_completion(self.filter_name)
