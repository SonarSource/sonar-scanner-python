from dataclasses import dataclass


@dataclass(frozen=True)
class JREResolvedPath:
        path:str

        def __post_init__(self):
            if not self.path:
                raise ValueError("JRE path cannot be empty")

