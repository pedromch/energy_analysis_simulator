from dataclasses import dataclass, field

@dataclass
class Stream:

    name: str
    Tin: float
    Tout: float
    mCp: float
    is_hot: bool = field(init=False)

    def __post_init__(self):
        self.is_hot = self.Tin > self.Tout

    def __eq__(self, obj):
        return isinstance(obj, Stream) and self.name == obj.name

    def get_temperature_range(self):
        return [self.Tout, self.Tin] if self.is_hot else [self.Tin, self.Tout]

