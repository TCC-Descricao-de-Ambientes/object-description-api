import os
from random import choice

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

try:
    from PIL import Image
except ImportError:
    import Image

COLORS = ["#00ff00", "#ff00ff", "#00ffff", "#ff9900"]


class Req:
    def __init__(self, objects, precision=60.0) -> None:
        self._file_path = objects.path
        self._image = Image.open(objects.path)
        self._width = objects.width
        self._height = objects.height
        self._precision = precision

        self._columns = 5
        self._rows = 3

        self._objects = self._filter_objects(objects, precision)
        self._process_image()

    def _process_image(self):
        dpi = 100

        self.fig = plt.figure(
            figsize=(float(self._width / dpi), float(self._height / dpi)), dpi=dpi
        )

        self.axes = self.fig.add_subplot(111)

        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        x_interval = self._width / self._columns
        y_interval = self._height / self._rows

        loc_x = plticker.MultipleLocator(base=x_interval)
        loc_y = plticker.MultipleLocator(base=y_interval)

        self.axes.xaxis.set_major_locator(loc_x)
        self.axes.yaxis.set_major_locator(loc_y)

        self.axes.grid(
            which="major", axis="both", linestyle="-", color="r", linewidth=3
        )
        self.axes.imshow(self._image)

    def req(self):
        descriptions = []
        for obj in self._objects:
            self._draw_obj(obj)

            x_desc = self._get_description_by_coord(obj.x, axis="x")
            y_desc = self._get_description_by_coord(obj.y, axis="y")

            object_description = {"name": str(obj), "x": x_desc, "y": y_desc}
            descriptions.append(object_description)

        return self._format_descriptions(descriptions)

    def _draw_obj(self, obj):
        color = choice(COLORS)
        x_center = obj.x * self._width
        y_center = obj.y * self._height

        circle = plt.Circle((x_center, y_center), radius=5, color=color)

        x_anchor = obj.box[1] * self._width
        y_anchor = obj.box[2] * self._height
        anchor = (x_anchor, y_anchor)

        rect_width = obj.width * self._width
        rect_height = (obj.height * self._height) * -1
        rect = plt.Rectangle(
            anchor, rect_width, rect_height, fill=False, lw=5, color=color, label=obj
        )

        x_top = obj.box[1] * self._width
        y_top = obj.box[0] * self._height

        ax = self.fig.gca()
        ax.add_artist(circle)
        ax.add_artist(rect)
        ax.annotate(
            obj,
            (x_top + 3, y_top - 5),
            color="black",
            backgroundcolor=color,
            weight="bold",
            fontsize=12,
            ha="left",
            va="center",
        )

    def _get_description_by_coord(self, coord, axis):
        if axis == "x":
            direction = self._columns
            dimension = self._width

        elif axis == "y":
            direction = self._rows
            dimension = self._height
        else:
            return

        for i in range(1, direction + 1):
            if coord * dimension <= dimension * i / direction:
                return self._get_description()[axis][i]

    def save(self):
        head, tail = os.path.splitext(self._file_path)
        filename = head.split(os.sep)[-1]
        new_head = head.replace(filename, filename + '_processed')
        new_path = new_head + tail
        self.fig.savefig(new_path)
        return new_path

    @staticmethod
    def _filter_objects(detected_objects, desired_precision):
        valid_objects = []
        objects = detected_objects.objects

        for obj in objects:
            obj_precision = round(obj.score * 100, 3)
            if obj_precision >= desired_precision:
                valid_objects.append(obj)

        return valid_objects

    @staticmethod
    def _get_description():
        return {
            "x": {
                1: "muito a esquerda",
                2: "na esquerda",
                3: "no centro",
                4: "na direita",
                5: "muito a direita",
            },
            "y": {1: "em cima", 2: "no centro", 3: "embaixo"},
        }

    @staticmethod
    def _format_descriptions(objects):
        single_object_str = "A imagem é composta pelo objeto {} que está {}"
        multiple_objects_str = (
            "A imagem é composta por pelo menos {} objetos que são:\n{}"
        )

        number_objects = len(objects)
        if number_objects > 1:
            multiple_objects_list = []
            for obj in objects:
                name = obj["name"]
                x = obj["x"]
                y = obj["y"]
                if x == y:
                    description = f"{name} {x}"
                else:
                    description = f"{name} {x} e {y}"

                multiple_objects_list.append(description)

            objects_str = "\n".join(multiple_objects_list)
            return multiple_objects_str.format(number_objects, objects_str)

        elif number_objects == 1:
            name = objects[0]["name"]
            x = objects[0]["x"]
            y = objects[0]["y"]
            if x == y:
                description = x
            else:
                description = " e ".join([x, y])

            return single_object_str.format(name, description)
