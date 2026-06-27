class Scene:
    def __init__(self):
        self.person = False
        self.phone = False
        self.book = False
        self.cup = False
        self.bottle = False
        self.backpack = False
        self.laptop = False
        self.keyboard = False
        self.mouse = False
        
        self.objects = []

    def __str__(self):
        return (
            f"Scene(person={self.person}, phone={self.phone}, "
            f"book={self.book}, cup={self.cup}, laptop={self.laptop}, "
            f"objects={self.objects})"
        )