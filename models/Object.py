class Object:
    def __init__(self, box, score, category) -> None:
        self._box = box
        self._score = score
        self._category = category
        self._x ,self._y = self._get_center_of_mass(box)
        self._width, self._height = self._get_box_dimensions(box)
        

    def __repr__(self):
        obj_name = self._category["name"]
        precision_percentage = round(self._score * 100, 2)
        return f"<{precision_percentage}% Object '{obj_name}'>"

    def __str__(self):
        return self._category["name"]

    @property
    def box(self):
        return self._box

    @property
    def score(self):
        return self._score

    @property
    def category(self):
        return self._category
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
        
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    @staticmethod
    def _get_center_of_mass(box):
        x, y = None, None
        try:
            y = (box[0] + box[2])/2
            x = (box[1] + box[3])/2
        except Exception as e:
            print(e)
        
        if x and y:
            return x, y
        
    @staticmethod
    def _get_box_dimensions(box):
        width, height = None, None
        try:
            height = box[2] - box[0]
            width = box[3] - box[1]
        except Exception as e:
            print(e)
        
        if width and height:
            return width, height
