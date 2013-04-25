from BTree import BTree
from simulation import Simulation
from gui import BetterTreeView

sim = Simulation(BTree, key_size = 5, data_record_size = 10, index_pointer_size = 3,
                 data_pointer_size = 5, block_size = 45, coalesce = False)
bv = BetterTreeView(sim)
bv.mainloop()