from graft.local_file.local_file import LocalFileDataLayer
from graft.standard.standard import StandardLogicLayer
from graft.typer_cli.typer_cli import TyperCLIPresentationLayer


def run_graft_app() -> None:
    data_layer = LocalFileDataLayer()
    logic_layer = StandardLogicLayer(data_layer=data_layer)
    presentation_layer = TyperCLIPresentationLayer(logic_layer_=logic_layer)
    presentation_layer.run()
