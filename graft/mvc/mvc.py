"""MVC."""

import abc
from typing import TYPE_CHECKING

from graft.mvc import model_controller as mc
from graft.mvc import view_controller as vc

if TYPE_CHECKING:
    from collections.abc import Callable


class Model(abc.ABC):
    """Base class for all models."""

    @abc.abstractmethod
    def channel(self, request: mc.Request) -> mc.Response:
        """Receive a request from the controller and return a response."""
        ...


class View(abc.ABC):
    """Base class for all views."""

    def __init__(self) -> None:
        """Initialise view."""
        self.controller_channel: Callable[[vc.Request], vc.Response] | None = None


class Controller(abc.ABC):
    """Base class for all controllers."""

    def __init__(self) -> None:
        """Initialise controller."""
        self.model_channel: Callable[[mc.Request], mc.Response] | None = None

    @abc.abstractmethod
    def channel(self, request: vc.Request) -> vc.Response:
        """Receive a request from the view and return a response."""
        ...


class MVC:
    """Model View Controller."""

    def __init__(self, model: Model, view: View, controller: Controller) -> None:
        """Initialize MVC."""
        self.model = model
        self.view = view
        self.controller = controller

        self.view.controller_channel = self.controller.channel
        self.controller.model_channel = self.model.channel
