from .Object import Object

class DetectedObjects:
    def __init__(self, boxes, scores, classes, num, category_index, path, shape) -> None:
        self._boxes = boxes
        self._scores = scores
        self._classes = classes
        self._num = num
        self._category_index = category_index
        self._path = path
        self._height = shape[0]
        self._width = shape[1]
        self._depth = shape[2]
        
        self._objects = self._create_objects()
    
    @property
    def path(self):
        return self._path
    
    @property
    def height(self):
        return self._height
    
    @property
    def width(self):
        return self._width
    
    @property
    def depth(self):
        return self._depth
    
    @property
    def objects(self):
        return self._objects
         
    def _create_objects(self):
        objects = []
        for box, score, class_ in zip(self._boxes[0], self._scores[0], self._classes[0]):
            class_string = str(int(class_))
            category = self._category_index[class_string]
            object = Object(box, score, category)
            objects.append(object)
        
        return objects

    def to_json(self):
        json_objects = {'objects': []}
        objects = self._objects
        for obj in objects:
            box_raw = [str(i) for i in list(obj.box)]
            box = {
                'ymin': box_raw[0],
                'xmin': box_raw[1],
                'ymax': box_raw[2],
                'xmax': box_raw[3],
            }
            
            json_object = {
                'name': str(obj),
                'box': box,
                'score': str(obj.score),
                'x': str(obj.x),
                'y': str(obj.y),
                'height': str(obj.height),
                'width':str(obj.width)
            }
        
            json_objects['objects'].append(json_object)

        return json_objects
        