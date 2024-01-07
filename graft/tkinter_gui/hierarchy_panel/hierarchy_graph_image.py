import functools
import pathlib
import tkinter as tk
from typing import Final, Self

from PIL import Image, ImageTk

from graft import architecture
from graft.architecture.logic import LogicLayer
from graft.tkinter_gui import system_update_dispatcher

_DATA_DIRECTORY_NAME: Final = "tkinter_gui_images"

_HIERARCHY_GRAPH_IMAGE_FILENAME = "hierarchy_graph.png"

_DATA_DIRECTORY_PATH = pathlib.Path.cwd() / _DATA_DIRECTORY_NAME

_HIERARCHY_GRAPH_IMAGE_FILEPATH = (
    _DATA_DIRECTORY_PATH / _HIERARCHY_GRAPH_IMAGE_FILENAME
)


def generate_hierarchy_graph_image(logic_layer: architecture.LogicLayer) -> None:
    pass


class HierarchyGraphImage(tk.Label):
    def __init__(self, master: tk.Misc, logic_layer: LogicLayer) -> None:
        def update_image(self: Self) -> None:
            generate_hierarchy_graph_image(logic_layer=self.logic_layer)
            img = ImageTk.PhotoImage(Image.open(_HIERARCHY_GRAPH_IMAGE_FILEPATH))
            self.configure(image=img)

        super().__init__(master)

        self.logic_layer = logic_layer

        update_image(self)

        dispatcher = system_update_dispatcher.get_singleton()
        dispatcher.add(functools.partial(update_image, self=self))
