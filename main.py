from env.gui import SokobanGUI
from search import bfs_solve,ids_solve,ucs_solve,astar_solve
from env.sokoban import SokobanGame

if __name__ == "__main__":
    gui = SokobanGUI()
    gui.run()