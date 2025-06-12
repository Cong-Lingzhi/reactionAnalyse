# INFOS:
atom_num = 160
step_num = 200
step_id = [(k + 1) * 10000 for k in range(step_num)]
type_list = ["C", "H", "C", "D", "F", "R"]
type_dict = {"C":1, "H":2, "C":3, "D":4, "F":5, "R":6}
read_type_dict = {'1':'C', '2':'H', '3':'C', '4':'D', '5':'F', '6':'R'}
dot_file = "./data/example2/output/all.dot"
new_dot_file = "./data/example2/output/all1.dot"
new_svg_file = "./data/example2/output/all1.svg"
relations_list_file = "./data/example2/output/reactions_list.txt"

import os
dot_exe_path = os.path.abspath("./package/Graphviz/bin/dot.exe")

temp_folder = "./data/example2/datas/"
coreNum = 10

is_get_svg = True

divide_dump_file = None
divide_bond_file = None

is_compare = True
compareFile = './data/example2/output/compare.txt'