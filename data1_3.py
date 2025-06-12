# INFOS:
atom_num = 13000
step_num = 1000
step_id = [(k + 1) * 10000 for k in range(step_num)]
type_list = ["C", "H"]
type_dict = {"C":1, "H":2}
read_type_dict = {'1':'C', '2':'H'}

dot_file = "./data/example1/1000-1000/output/all.dot"
new_dot_file = "./data/example1/1000-1000/output/all1.dot"
new_svg_file = "./data/example1/1000-1000/output/all1.svg"
relations_list_file = "./data/example1/1000-1000/output/reactions_list.txt"

import os
dot_exe_path = os.path.abspath("./package/Graphviz/bin/dot.exe")

temp_folder = "./data/example1/1000-1000/datas/"

coreNum = 10

is_get_svg = True

divide_dump_file = './data/example1/1000-1000/mini1000.dump'
divide_bond_file = './data/example1/1000-1000/reax1000.bonds'

is_compare = True
compareFile = './data/example1/1000-1000/output/compare.txt'