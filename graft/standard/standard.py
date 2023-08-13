from graft import architecture


class StandardLogicLayer(architecture.LogicLayer):
    def __init__(self, data_layer: architecture.DataLayer) -> None:
        super().__init__(data_layer=data_layer)
