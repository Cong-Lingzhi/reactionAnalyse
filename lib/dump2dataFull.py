from multiprocessing.pool import Pool
from lib.dataClass import MonomerInfo, ChainInfo
from lib.data import *
def readDump(dumpfile):
    c1 = open(dumpfile)
    items = c1.readlines()
    atomNum = int(items[3].strip())
    atomInfo = [None for _ in range(atomNum)]
    box = []
    for line in items[5:8]:
        lb = line.strip().replace('\t', ' ').split()
        box += lb
    for line in items[9:]:
        lb = line.strip().replace('\t', ' ').split()
        atomInfo[int(lb[0]) - 1] = (lb[1:])
    c1.close()
    return box, atomInfo

def readBond(bondfile):
    c1 = open(bondfile)
    items = c1.readlines()
    bondString = ""
    bondNum = 0
    for line in items:
        lb = line.strip().replace('\t', ' ').split()
        if len(lb) == 0 or lb[0] == '#': continue
        atomi, bondiNum = int(lb[0]), int(lb[2])
        for bondj in range(bondiNum):
            atomj = int(lb[3 + bondj])
            if atomi >= atomj: continue
            bondNum += 1
            bondString += f'{bondNum} 1 {atomi} {atomj}\n'
    c1.close()
    return bondNum, bondString

def readFullData(filename, typeDict = type_dict):
    c1 = open(filename)
    isAtom, isBond = False, False
    boxs, origin = [None] * 3, [None] * 3
    for line in c1:
        lb = line.strip().replace('\t', ' ').split()
        if len(line) > 0 and line[0] == '#': continue
        lbLen = len(lb)
        if lbLen >= 1 and lb[0] in ["Atoms", "Bonds"]: 
            lb0 = lb[0]
            if lb0 == "Atoms":
                monomer = MonomerInfo()
                types, sites = [None] * atomNum, [None] * atomNum
                atom1indexlist, atom2indexlist = [None] * bondNum, [None] * bondNum
                currentId = 0
                isAtom = True
            else :
                currentId = 0
                isAtom, isBond = False, True
        elif lbLen == 2 and lb[1] in ["atoms", "bonds"]:
            lb0, lb1 = lb
            if lb1 == "atoms": atomNum = int(lb0)
            else: bondNum = int(lb0)
        elif lbLen == 4:
            if isBond:
                atom1indexlist[currentId] = int(lb[2]) - 1
                atom2indexlist[currentId] = int(lb[3]) - 1 
                currentId += 1
            else:  
                lb0, lb1, lb2 = lb[:3]  
                if lb2 == "xlo":
                    boxs[0] = float(lb1)
                    origin[0] = float(lb0)
                elif lb2 == "ylo":
                    boxs[1] = float(lb1)
                    origin[1] = float(lb0)
                elif lb2 == "zlo":
                    boxs[2] = float(lb1)
                    origin[2] = float(lb0)
        elif isAtom and lbLen in [5, 6, 7, 9, 10]:
            if lbLen == 5:
                types[currentId] = typeDict[lb[1]]
                sites[currentId] = [float(lb[2]), float(lb[3]), float(lb[4])]
            elif lbLen == 6:
                types[currentId] = typeDict[lb[1]]
                sites[currentId] = [float(lb[3]), float(lb[4]), float(lb[5])]
            elif lbLen == 7:
                types[currentId] = typeDict[lb[2]]
                sites[currentId] = [float(lb[4]), float(lb[5]), float(lb[6])]
            elif lbLen == 9:
                types[currentId] = typeDict[lb[1]]
                sites[currentId] = [float(lb[3]), float(lb[4]), float(lb[5])]
            elif lbLen == 10:
                types[currentId] = typeDict[lb[2]]
                sites[currentId] = [float(lb[4]), float(lb[5]), float(lb[6])]
            currentId += 1
    monomer.atoms.addAtoms(types, sites)
    monomer.bonds.addBonds(atom1indexlist, atom2indexlist)
    monomer.resetIndexs()
    monomer.box.boxLength = boxs
    monomer.box.origin = origin
    c1.close()
    return monomer

def writeFile(infos):
    i, dumpfile, bondfile, data1_file = infos
    box, atomInfo = readDump(dumpfile)
    bondNum, bondString = readBond(bondfile)
    f1 = open(data1_file, 'w')
    f1.write(f'# dump for timestep {step_id[i]}\n')
    f1.write(f"{len(atomInfo)} atoms\n{bondNum} bonds\n4 atom types\n1 bond types\n")
    for k in range(3): f1.write(f"{box[k * 2]} {box[k * 2 + 1]} {['x', 'y', 'z'][k]}lo {['x', 'y', 'z'][k]}hi\n")
    f1.write('\nAtoms # full\n\n')
    for k, atomInfoi in enumerate(atomInfo):
        f1.write(f"{k + 1} 1 {atomInfoi[0]} 0")
        for j in range(3): f1.write(f" {atomInfoi[j + 1]}")
        f1.write('\n')
    f1.write('\nBonds\n\n')
    f1.write(bondString)
    f1.close()

def writeFileFull(infos):
    stepi, infile, outfile = infos
    mono1 = readFullData(infile, typeDict = read_type_dict)
    times = None
    if is_compare:
        from time import time
        from lib.dataClass import ChainInfoDFS, chainInfoBFS
        startTime = time()
        chainInfo = ChainInfoDFS(mono1)
        time1 = time() - startTime

        startTime = time()
        chainInfo = chainInfoBFS(mono1)
        time2 = time() - startTime

        startTime = time()
    chainInfo = ChainInfo(mono1)
    if is_compare:
        time3 = time() - startTime
        times = [stepi, time1, time2, time3]
    chainLabel = chainInfo.chainLabel

    f1 = open(infile)
    f2 = open(outfile, 'w')

    for line in f1:
        sline = line.strip().replace('\t', ' ').split()
        if len(sline) in [7, 10]: f2.write(' '.join([sline[0], str(chainLabel[int(sline[0]) - 1] + 1)] + sline[2:]) + '\n')
        else: f2.write(line)
    f1.close()
    f2.close()
    return times

def getFullDataPre():
    infoList = []
    for i in range(step_num):
        dumpFile = f'{temp_folder}/pre_{i}.data'
        dataFileNew = f'{temp_folder}/{i}.data1'
        k = i
        bondfile = f'{temp_folder}/pre_{k}.bond'
        infos = (i, dumpFile, bondfile, dataFileNew)
        infoList.append(infos)
    pool = Pool()
    pool.map(writeFile, infoList)
    pool.close()
    pool.join()

def getFullData():
    infoList = []
    for i in range(step_num):
        inFile = f'{temp_folder}/{i}.data1'
        outFile = f'{temp_folder}/{i}_full.data1'
        infoList.append([i, inFile, outFile])
    pool = Pool()
    res = pool.map(writeFileFull, infoList)
    pool.close()
    pool.join()
    
    if is_compare:
        f1 = open(compareFile, 'w')
        for line in res: f1.write(' '.join(map(str, line)) + '\n')
        f1.close()
    
if __name__ == '__main__':
    pass