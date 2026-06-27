class Scene:

    def __init__(self):

        self.person = False
        self.phone = False
        self.book = False
        self.cup = False

        self.objects = []

    def __str__(self):

        return (
            f"Scene("
            f"person={self.person}, "
            f"phone={self.phone}, "
            f"book={self.book}, "
            f"cup={self.cup})"
        )