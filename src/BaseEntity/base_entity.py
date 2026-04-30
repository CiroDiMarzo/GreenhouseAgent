class BaseEntity:
    def __init__(self, is_dirty: bool = False):
        self.is_dirty = is_dirty