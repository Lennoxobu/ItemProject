from syntax import primer


@dataclass
class Implementation(object):
    name:str
    primer:str


    def __def__ (self):
        self.name = self.name,
        self.primer = primer.__dict__


        return type(self)



    def __call__(self, *args, **kwargs):
        self.name = self.name,
        self.primer = primer.__dict__
        return {
            "name: ": self.name,
            "primer: ": self.primer

        }











