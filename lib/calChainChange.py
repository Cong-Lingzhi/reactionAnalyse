from multiprocessing.pool import Pool
from lib.dump2dataFull import readFullData
from lib.dataClass import ChainInfo, ReactInfo, PointInfo
from lib.data import *
def getInfo(inputData):
    infile, outfile, stepi = inputData
    mono1 = readFullData(infile, typeDict = read_type_dict)
    chainInfo = ChainInfo(mono1)
    chainLabel = chainInfo.chainLabel
    chainInfo.stepId = stepi

    f1 = open(infile)
    f2 = open(outfile, 'w')

    for line in f1:
        sline = line.strip().replace('\t', ' ').split()
        if len(sline) == 7: f2.write(' '.join([sline[0], str(chainLabel[int(sline[0]) - 1] + 1)] + sline[2:]) + '\n')
        else: f2.write(line)
    f1.close()
    f2.close()

    return (chainInfo, stepi)

def write_relations(inputData):
    stepi, chainInfoOld, chainInfoNew = inputData
    chainLabelOld, listChainOld, chainNameOld = chainInfoOld.chainLabel, chainInfoOld.listChain, chainInfoOld.chainName
    chainLabelNew, listChainNew, chainNameNew = chainInfoNew.chainLabel, chainInfoNew.listChain, chainInfoNew.chainName
    #--------------------------------------------------------------------
    #检查两次的atom的分子索引的变化
    chainChange = {}
    atomChange = {}
    for k in range(len(chainLabelOld)):
        oldChain = chainLabelOld[k]
        newChain = chainLabelNew[k]
        if oldChain not in chainChange: chainChange[oldChain] = set()
        chainChange[oldChain].add(newChain)
            
        change = (oldChain, newChain)
        if change not in atomChange: atomChange[change] = [k]
        else: atomChange[change].append(k)
    for oldChain, newChain in chainChange.items(): chainChange[oldChain] = list(newChain)
    #删除没变的链
    deleteKeys = []
    for chainKey in chainChange:
        newChain = chainChange[chainKey][0]
        if len(chainChange[chainKey]) == 1 and len(listChainOld[chainKey]) == len(listChainNew[newChain]) :
            deleteKeys.append(chainKey)
    for m in deleteKeys: 
        del atomChange[(m, chainChange[m][0])]
        del chainChange[m]

    changeAtoms = []
    for change in atomChange:
        changeAtoms.extend(atomChange[change])
    
    #写出链反应方程
    divideDict, combineDict = {}, {}
    for change in atomChange:
        chainOldId, chainNewId = change
        chainOldLen = len(listChainOld[chainOldId])
        chainNewLen = len(listChainNew[chainNewId])
        atomPartLen = len(atomChange[change])

        if chainOldLen == atomPartLen:   #全反应
            point = PointInfo(chainOldId, stepi, chainNameOld[chainOldId], 0)
            if chainNewId not in combineDict: combineDict[chainNewId] = [point]
            else: combineDict[chainNewId].append(point)
        elif chainNewLen == atomPartLen:  #全分解
            point = PointInfo(chainNewId, stepi + 1, chainNameNew[chainNewId], 0)
            if chainOldId not in divideDict: divideDict[chainOldId] = [0, point]
            else: divideDict[chainOldId].append(point)
        else:
            if chainOldId not in divideDict: divideDict[chainOldId] = [0, ]
            divideDict[chainOldId][0] += 1
            flag = divideDict[chainOldId][0]
            monoName = chainInfoOld.getName(atomChange[change])
            point = PointInfo(chainOldId, stepi, monoName, flag)
            
            divideDict[chainOldId].append(point)

            if chainNewId not in combineDict: combineDict[chainNewId] = []
            combineDict[chainNewId].append(point) 

    pointPairList = []
    for chainOldId in divideDict:
        pointi = PointInfo(chainOldId, stepi, chainNameOld[chainOldId], 0)
        for pointj in divideDict[chainOldId][1:]: pointPairList.append((pointi, pointj))
    for chainNewId in combineDict:
        pointj = PointInfo(chainNewId, stepi + 1, chainNameNew[chainNewId], 0)
        for pointi in combineDict[chainNewId]: pointPairList.append((pointi, pointj))

    outputData = changeAtoms, pointPairList
    return outputData

def getSpyAtomPoint(chainInfoOld, chainInfoNew, spyAtomsNeed, stepi):
    chainlabelOld = chainInfoOld.chainLabel
    chainlabelNew = chainInfoNew.chainLabel
    chainNeedIdSet = set()
    for atom_need_id in spyAtomsNeed:
        chain1, chain2 = chainlabelOld[atom_need_id], chainlabelNew[atom_need_id]
        chainNeedIdSet.add((chain1, chain2, stepi))
    chainNeedId = list(chainNeedIdSet)   
    return chainNeedId  

def getSpyAtoms(stepi, spyAtoms, chainInfoOld, chainInfoNew, changeAtoms):
    chainNameOld, chainNameNew = chainInfoOld.chainName, chainInfoNew.chainName
    changeAtomsSet = set(changeAtoms)
    spyAtomsNeed = list(spyAtoms - changeAtomsSet)
    spyAtomsNew = spyAtoms | changeAtomsSet
    chainNeedId = getSpyAtomPoint(chainInfoOld, chainInfoNew, spyAtomsNeed, stepi)
    pointPairSpyList = [(PointInfo(chainOldId, stepi, chainNameOld[chainOldId], 0), 
                         PointInfo(chainNewId, stepi + 1, chainNameNew[chainNewId], 0)) 
                         for chainOldId, chainNewId, stepi in chainNeedId]

    return pointPairSpyList, spyAtomsNew

def getPointPair():
    reactInfo = ReactInfo()
    spyAtoms = set()
    maxNum = 200
    currentNum = step_num
    k = 0
    chainInfosPre = None
    with Pool(20) as pool:
        while currentNum > 0:
            getNum = min(currentNum, maxNum)
            currentNum -= getNum
            chainInfos = [None] * getNum
            pointPairListAll = [None] * getNum
            pointPairSpyListAll = [None] * getNum
            
            info_list = [(f'{temp_folder}/{i + k}.data1', f'{temp_folder}/{i + k}_full.data1', i) for i in range(getNum)]
            res = pool.map(getInfo, info_list)
            for (chainInfok, stepi) in res: chainInfos[stepi] = chainInfok

            if chainInfosPre is not None: 
                chainInfos0 = chainInfos[0]
                (changeAtoms, pointPairListAll) = write_relations((k - 1, chainInfosPre, chainInfos0))
                pointPairSpyListAll, spyAtoms = getSpyAtoms(k - 1, spyAtoms, chainInfosPre, chainInfos0, changeAtoms)
                reactInfo.addPointPairList(pointPairListAll + pointPairSpyListAll)

            for i in range(getNum - 1):
                index = i + 1
                (changeAtoms, pointPairListAll) = write_relations((k + i, chainInfos[i], chainInfos[index]))
                pointPairSpyListAll, spyAtoms = getSpyAtoms(k + i, spyAtoms, chainInfos[i], chainInfos[index], changeAtoms)                
                reactInfo.addPointPairList(pointPairListAll + pointPairSpyListAll)

            chainInfosPre = chainInfos[-1]
            k += getNum
    return reactInfo
        