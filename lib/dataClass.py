import numpy as np
import os
from lib.data import *

def getName(atomids, types):
    mono = [0 for _ in type_list]
    for atomid in atomids: mono[type_dict[types[atomid]] - 1] += 1
    monoName = ""
    for i, monoNumi in enumerate(mono):
        if monoNumi >= 1: monoName += type_list[i]
        if monoNumi > 1: monoName += str(monoNumi)
    return monoName

class BoxInfo(object):
    def __init__(self):
        self.boxLength = [10, 10, 10]
        self.angle = [90, 90, 90]
        self.origin = [0, 0, 0]
        self.period = [False, False, False]

class AtomInfo(object):
    def __init__(self):
        self.atomNum = 0
        self.indexs = []
        self.types = []
        self.sites = []

    def addAtoms(self, typeslist, siteslist):
        addAtomsNum = len(typeslist)
        newIndices = list(range(addAtomsNum))
        self.atomNum += addAtomsNum
        self.indexs.extend(newIndices)
        self.types.extend(typeslist)
        self.sites.extend(siteslist)

class BondInfo(object):
    def __init__(self):
        self.bondNum = 0
        self.indexs = []
        self.atom1 = []
        self.atom2 = []

    def addBonds(self, atom1, atom2):
        addBondsNum = len(atom1)
        newIndices = list(range(addBondsNum))
        self.bondNum += addBondsNum
        self.indexs.extend(newIndices)
        self.atom1.extend(atom1)
        self.atom2.extend(atom2)

class MonomerInfo(object):
    def __init__(self):
        self.box = BoxInfo()
        self.atoms = AtomInfo()
        self.bonds = BondInfo()

    def resetIndexs(self):
        atomNum = self.atoms.atomNum
        indexdict = np.zeros((atomNum,), dtype = int)
        for i, indexk in enumerate(self.atoms.indexs): indexdict[indexk] = i
        self.atoms.indexs = np.arange(atomNum)
        self.bonds.indexs = np.arange(self.bonds.bondNum)
        self.bonds.atom1 = indexdict[self.bonds.atom1]
        self.bonds.atom2 = indexdict[self.bonds.atom2]

    def getName(self, atomids):
        return getName(atomids, self.atoms.types)

class ChainInfoDFS(object):
    def __init__(self, monomer: MonomerInfo):
        atomNum = monomer.atoms.atomNum
        bondNum = monomer.bonds.bondNum
        bondAtom1List = monomer.bonds.atom1
        bondAtom2List = monomer.bonds.atom2
        # 定义原子和它们之间的键连接关系
        atoms = list(range(atomNum))
        bonds = [(bondAtom1List[i], bondAtom2List[i]) for i in range(bondNum)]

        # 创建一个字典来存储每个原子与其他原子之间的连接关系
        graph = {atom: [] for atom in atoms}

        # 根据键连接信息填充图
        for bond in bonds:
            atom1, atom2 = bond
            graph[atom1].append(atom2)
            graph[atom2].append(atom1)

        # 用来记录已经访问过的原子
        visited = set()

        # DFS函数，用来遍历图并标记连通的原子
        def dfs(atom, component):
            visited.add(atom)
            component.append(atom)
            for neighbor in graph[atom]:
                if neighbor not in visited:
                    dfs(neighbor, component)

        # 存储所有连通分量
        connected_components = []

        # 遍历所有原子，找到所有连通分量
        for atom in atoms:
            if atom not in visited:
                component = []
                dfs(atom, component)
                connected_components.append(component)

        return 
    
from collections import deque
class chainInfoBFS(object):
    def __init__(self, monomer: MonomerInfo):
        atomNum = monomer.atoms.atomNum
        bondNum = monomer.bonds.bondNum
        bondAtom1List = monomer.bonds.atom1
        bondAtom2List = monomer.bonds.atom2
        # 定义原子和它们之间的键连接关系
        atoms = list(range(atomNum))
        bonds = [(bondAtom1List[i], bondAtom2List[i]) for i in range(bondNum)]

        # 创建一个字典来存储每个原子与其他原子之间的连接关系
        graph = {atom: [] for atom in atoms}

        # 根据键连接信息填充图
        for bond in bonds:
            atom1, atom2 = bond
            graph[atom1].append(atom2)
            graph[atom2].append(atom1)

        # 用来记录已经访问过的原子
        visited = set()

        # BFS函数，用来遍历图并标记连通的原子
        def bfs(start_atom):
            queue = deque([start_atom])  # BFS队列
            component = []  # 当前连通分量
            visited.add(start_atom)
            
            while queue:
                atom = queue.popleft()  # 获取队列中的第一个原子
                component.append(atom)
                
                for neighbor in graph[atom]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)  # 将未访问过的相邻原子加入队列
                        
            return component

        # 存储所有连通分量
        connected_components = []

        # 遍历所有原子，找到所有连通分量
        for atom in atoms:
            if atom not in visited:
                component = bfs(atom)
                connected_components.append(component)
        return 

class ChainInfo(object):
    def __init__(self, monomer: MonomerInfo):
        self.stepId = None
        atomNum = monomer.atoms.atomNum
        bondNum = monomer.bonds.bondNum
        bondAtom1List = monomer.bonds.atom1
        bondAtom2List = monomer.bonds.atom2

        newLabel = 0
        chainLabel = [0] * atomNum
        listChain = []

        for bondi in range(bondNum):
            atom1Index = bondAtom1List[bondi]
            atom2Index = bondAtom2List[bondi]
            Label1 = chainLabel[atom1Index]
            Label2 = chainLabel[atom2Index]
            if Label1 == Label2:
                if Label1 == 0:
                    newLabel += 1
                    chainLabel[atom1Index] = newLabel 
                    chainLabel[atom2Index] = newLabel
                    listChain.append([atom1Index, atom2Index])
                continue
            if Label1 == 0:
                chainLabel[atom1Index] = Label2
                listChain[Label2 - 1].append(atom1Index)
                continue
            if Label2 == 0:
                chainLabel[atom2Index] = Label1
                listChain[Label1 - 1].append(atom2Index)
                continue
            for chainItem in listChain[Label2 - 1]: chainLabel[chainItem] = Label1
            listChain[Label1 - 1] += listChain[Label2 - 1]
            listChain[Label2 - 1] = []

        for i in range(atomNum): 
            if chainLabel[i] > 0: continue
            newLabel += 1 
            chainLabel[i] = newLabel
            listChain.append([i])
        
        dictk = {}
        indexNow = 0
        for i in range(len(listChain)):
            if listChain[i] != []:
                dictk[i + 1] = indexNow
                indexNow += 1
        for i in range(len(listChain) - 1, -1, -1):
            if listChain[i] == []:
                listChain.pop(i)
        chainNewLabel = [dictk[i] for i in chainLabel]

        self.chainLabel = chainNewLabel
        self.listChain = listChain
        self.types = monomer.atoms.types
        self.chainName = [self.getName(chain) for chain in listChain]
        self.chainNum = len(self.chainName)
    
    def getName(self, atomids):
        return getName(atomids, self.types)

class PointInfo(object):
    def __init__(self, chainId, step, name, partId):
        self.chainId = chainId
        self.step = step
        self.name = name
        self.partId = partId

    def getTuple(self):
        return(self.chainId, self.name, self.partId, self.step)
    
class ReactInfo(object):
    def __init__(self):
        self.totalPoint = [{} for _ in range(step_num)]  
        self.delPoint = [[] for _ in range(step_num)]
        self.notDelPoint = [[] for _ in range(step_num)]

    def addPointPair(self, pointA: PointInfo, pointB: PointInfo):
        stepA, stepB = pointA.step, pointB.step
        tupleA, tupleB = pointA.getTuple(), pointB.getTuple()
        if tupleA not in self.totalPoint[stepA]: self.totalPoint[stepA][tupleA] = {'up': [], 'down': [], 'reactionId': []}
        if tupleB not in self.totalPoint[stepB]: self.totalPoint[stepB][tupleB] = {'up': [], 'down': [], 'reactionId': []}
        
        self.totalPoint[stepA][tupleA]["down"].append(tupleB)
        self.totalPoint[stepB][tupleB]["up"].append(tupleA)

    def addPointPairList(self, pointPairList):
        for (PointA, pointB) in pointPairList: self.addPointPair(PointA, pointB)

    def getDelPoint(self):
        allPoint = [list(self.totalPoint[k].keys()) for k in range(step_num)]
        for stepi in range(step_num):
            for point in allPoint[stepi]:
                pointInfo = self.totalPoint[stepi][point]
                upPoint, downPoint = pointInfo["up"], pointInfo["down"]
                if not len(upPoint) == 1 : self.notDelPoint[stepi].append(point)
                if len(downPoint) > 1:
                    for downPointi in downPoint:
                        stepDown = downPointi[3]
                        self.notDelPoint[stepDown].append(downPointi)
        for stepi in range(step_num):
            self.delPoint[stepi] = list(set(allPoint[stepi]) - set(self.notDelPoint[stepi]))

    def delTotalPoint(self):
        for stepi in range(step_num):
            for delPointk in self.delPoint[stepi]:
                pointInfo = self.totalPoint[stepi][delPointk]
                upPoint, downPoint = pointInfo["up"], pointInfo["down"]
                for upPointi in upPoint:
                    stepu = upPointi[3]
                    self.totalPoint[stepu][upPointi]["down"].remove(delPointk)
                    for downPointi in downPoint:
                        stepd = downPointi[3]
                        self.totalPoint[stepd][downPointi]["up"].append(upPointi)
                        self.totalPoint[stepd][downPointi]["up"].remove(delPointk)
                        self.totalPoint[stepu][upPointi]["down"].append(downPointi)
        for stepi in range(step_num):
            for delPointk in self.delPoint[stepi]:
                self.totalPoint[stepi].pop(delPointk)

    def write(self):
        f2 = open(new_dot_file, 'w')
        f2.write('digraph G {\n')
        
        # write as Name_Step_ChainId_PartId
        for stepi in range(step_num):
            for point in set(self.notDelPoint[stepi]):
                down_point = self.totalPoint[stepi][point]["down"]
                for down_pointi in down_point:
                    f2.write(f"    {point[1]}_{point[3]}_{point[0]}_{point[2]} -> {down_pointi[1]}_{down_pointi[3]}_{down_pointi[0]}_{down_pointi[2]};\n")

        f2.write('}\n')
        f2.close()
    
    def transSvg(self):
        if is_get_svg: os.system(f"{dot_exe_path} -Tsvg {new_dot_file} -o {new_svg_file}")

        # f2 = open(new_dot_file + "aa", 'w')
        # f2.write('digraph G {\n')
        # writer = []
        # for stepi in range(step_num):
        #     for point in set(self.notDelPoint[stepi]):
        #         down_point = self.totalPoint[stepi][point]["down"]
        #         for down_pointi in down_point:
        #             writer.append(f"    {point[1]} -> {down_pointi[1]};\n")
        # writerSet = set(writer)
        # for writerk in writerSet: f2.write(writerk)
        # f2.write('}\n')
        # f2.close()
        # os.system(f"{dot_exe_path} -Tsvg {new_dot_file}aa -o {new_svg_file}aa")