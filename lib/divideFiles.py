from multiprocessing.pool import Pool
from lib.data import *

def writeSingleFile(infos):
    sections, outputFileName = infos
    fa = open(outputFileName, 'w')
    fa.write(sections)
    fa.close()

def divideFile(fileName, splitText, outputFileName):
    fd = open(fileName)
    content = fd.read()
    sections = content.split(splitText)
    sections = sections[1:]
    sections = [splitText + section for section in sections]
    fd.close()

    info_list = [(sections[i], outputFileName.replace("*", str(i))) for i in range(len(sections))]

    pool = Pool(coreNum)
    pool.map(writeSingleFile, info_list)
    pool.close()
    pool.join()

def divideDump():
    splitText = 'ITEM: TIMESTEP'
    outputFileName = f'{temp_folder}/pre_*.data'
    divideFile(divide_dump_file, splitText, outputFileName)

def divideBond():
    splitText = '# Timestep'
    outputFileName = f'{temp_folder}/pre_*.bond'
    divideFile(divide_bond_file, splitText, outputFileName)

if __name__ == '__main__':
    pass