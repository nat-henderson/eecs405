from BPlus import BPTree
from simulation import Simulation
from gui import BetterTreeView

sim = Simulation(BPTree, key_size = 5, data_record_size = 10, index_pointer_size = 10,
                 data_pointer_size = 5, block_size = 55, coalesce = False)
bv = BetterTreeView(sim)
bv.mainloop()