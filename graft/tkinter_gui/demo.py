import tkinter as tk
from tkinter import ttk

from graft import architecture


class TaskTable(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.tree = ttk.Treeview(
            self.master, columns=["id", "name", "description"], show="headings"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("description", text="Description")

        task_attributes_register = self.logic_layer.get_task_attributes_register_view()
        for uid, attributes in task_attributes_register.items():
            formatted_uid = str(uid)
            formatted_name = str(attributes.name) if attributes.name is not None else ""
            formatted_description = (
                str(attributes.description)
                if attributes.description is not None
                else ""
            )
            self.tree.insert(
                "",
                tk.END,
                values=[formatted_uid, formatted_name, formatted_description],
            )

        self.tree.grid()


class HierarchyGraph(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer


class DependencyGraph(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer


class Tabs(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master=master)
        self.logic_layer = logic_layer

        self.notebook = ttk.Notebook(self.master)

        self.task_table = TaskTable(self.notebook, logic_layer)
        self.hierarchy_graph = HierarchyGraph(self.notebook, logic_layer)
        self.dependency_graph = DependencyGraph(self.notebook, logic_layer)

        self.notebook.add(self.task_table, text="Task Table")
        self.notebook.add(self.hierarchy_graph, text="Hierarchy Graph")
        self.notebook.add(self.dependency_graph, text="Dependency Graph")

        self.notebook.grid()


class GUI:
    def __init__(self, logic_layer: architecture.LogicLayer) -> None:
        self.logic_layer = logic_layer
        self.root = tk.Tk()
        self.root.title("graft")
        # self.tabs = Tabs(self.root, logic_layer)
        # self.tabs.pack()
        self.tabs = Tabs(self.root, logic_layer)
        self.tabs.grid()

    def run(self) -> None:
        self.root.mainloop()


def run_app(logic_layer: architecture.LogicLayer) -> None:
    gui = GUI(logic_layer)
    gui.run()

    # root = tk.Tk()
    # root.title("graft")
    # frm = ttk.Frame(root, padding=10)
    # frm.grid()
    # ttk.Label(frm, text="graft").grid(column=0, columnspan=2, row=0)
    # ttk.Label(frm, text="Hello World!").grid(column=0, row=1)
    # ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=1)
    # tree = ttk.Treeview(frm, columns=("id", "name", "description"), show="headings")
    # tree.heading('id', text='ID')
    # tree.heading('last_name', text='Last Name')
    # tree.heading('email', text='Email')
    # root.mainloop()
