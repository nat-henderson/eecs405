from BPlus import BPTree, BPnode, BPleaf
from Tkinter import *
from nltk.tree import Tree
from nltk.draw.tree import TreeView, TreeWidget
from simulation import Simulation
import os

from Tkinter import *
import os

class Dialog(Toplevel):
    def __init__(self, parent, title = None, msg="Enter Something:"):
        self.msg = msg
        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)
    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()
    #
    # standard button semantics

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    #
    # command hooks

    def validate(self):
        return 1 # override

    def apply(self):
        pass # override

class CustomDialog(Dialog):
    def body(self, master):
        Label(master, text=self.msg).grid(row=0)

        self.e1 = Entry(master)

        self.e1.grid(row=0, column=1)
        return self.e1 # initial focus

    def apply(self):
        try:
            self.result = int(self.e1.get())
        except Exception:
            self.result = float(self.e1.get())

class BetterTreeView(TreeView):

    def __init__(self, simulation):
        super(BetterTreeView, self).__init__(BP_tree_to_nltk_tree(
            simulation.tree.root))
        self.simulation = simulation

    def input_box(self, msg):
        d = CustomDialog(self._top, msg = msg)
        return d.result

    def rerun_sim(self):
        self.simulation.run()
        for w in self._widgets:
            self._cframe.destroy_widget(w)
        del self._widgets[:]
        bold = ('helvetica', -self._size.get(), 'bold')
        helv = ('helvetica', -self._size.get())
        widget = TreeWidget(self._cframe.canvas(), BP_tree_to_nltk_tree(self.simulation.tree.root),
                            node_font=bold, leaf_color='#008040', node_color='#004080',
                            roof_color='#004040', roof_fill='white', line_color='#004040',
                            draggable=1, leaf_font=helv)
        widget.bind_click_trees(widget.toggle_collapsed)
        self._widgets.append(widget)
        self._cframe.add_widget(widget)
        self._layout()

    def _init_menubar(self):
        menubar = Menu(self._top)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Print to Postscript', underline=0,
                             command=self._cframe.print_to_file,
                             accelerator='Ctrl-p')
        filemenu.add_command(label='Exit', underline=1,
                             command=self.destroy, accelerator='Ctrl-x')
        menubar.add_cascade(label='File', underline=0, menu=filemenu)

        zoommenu = Menu(menubar, tearoff=0)
        zoommenu.add_radiobutton(label='Tiny', variable=self._size,
                                 underline=0, value=10, command=self.resize)
        zoommenu.add_radiobutton(label='Small', variable=self._size,
                                 underline=0, value=12, command=self.resize)
        zoommenu.add_radiobutton(label='Medium', variable=self._size,
                                 underline=0, value=14, command=self.resize)
        zoommenu.add_radiobutton(label='Large', variable=self._size,
                                 underline=0, value=28, command=self.resize)
        zoommenu.add_radiobutton(label='Huge', variable=self._size,
                                 underline=0, value=50, command=self.resize)
        menubar.add_cascade(label='Zoom', underline=0, menu=zoommenu)

        simmenu = Menu(menubar, tearoff = 0)
        simmenu.add_command(label="Key Size", underline = 0,
                            command = lambda: self.simulation.alter_parameters(
                                key_size=self.input_box("New Key Size")))

        simmenu.add_command(label="Data Record Size", underline = 0,
                            command = lambda: self.simulation.alter_parameters(
                                data_record_size=self.input_box("New Data Record Size")))

        simmenu.add_command(label="Index Pointer Size", underline = 0,
                            command = lambda: self.simulation.alter_parameters(
                                index_pointer_size=self.input_box("New Index Pointer Size")))

        simmenu.add_command(label="Data Pointer Size", underline = 0,
                            command = lambda: self.simulation.alter_parameters(
                                data_pointer_size=self.input_box("New Data Pointer Size")))

        simmenu.add_command(label="Block Size", underline = 0,
                            command = lambda: self.simulation.alter_parameters(
                                block_size=self.input_box("New Block Size")))

        simmenu.add_command(label="R/D/I percentage", underline = 0,
                            command = lambda: self.simulation.alter_parameters(
                                read_percent=self.input_box("New Read Percentage"),
                                delete_percent=self.input_box("New Delete Percentage"),
                                insert_percent=self.input_box("New Insert Percentage")))

        simmenu.add_command(label="Steps", underline = 0,
                            command = lambda: self.simulation.alter_parameters(
                                steps=self.input_box("New # Steps")))

        simmenu.add_command(label="Re-run", underline = 0,
                            command = lambda: self.rerun_sim())

        menubar.add_cascade(label = "Simulation", underline = 0, menu = simmenu)

        self._top.config(menu = menubar)

def draw_a_tree(tree):
    if isinstance(tree, BPTree):
        BP_tree_to_nltk_tree(tree.root).draw()

def get_tree_view(tree):
    if isinstance(tree, BPTree):
        sim = Simulation(tree.__class__)
        sim.tree = tree
        return BetterTreeView(sim)

def BP_tree_to_nltk_tree(tree):
    root = Tree(str(tree.keys), children = [])
    if isinstance(tree, BPnode):
        for child in tree.children:
            root.append(BP_tree_to_nltk_tree(child))

    return root
