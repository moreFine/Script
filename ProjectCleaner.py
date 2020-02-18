#!/usr/bin/python
# -*- coding :utf-8 -*-
# 脚本的使用：
# cd 到脚本文件夹
# 执行命令：python3 ProjectCleaner.py -f [工程文件路径] -i '[ignoreName]' '[ignoreName]'
import os
import shutil
import sys
import argparse

parser = argparse.ArgumentParser()
# 添加命令
parser.add_argument('-f', '--file', default='./', help='Your project path.Deafult curent ./ path. ')
parser.add_argument('-i', '--ignore', nargs='*', default=[], help='Igonre list.')

args = parser.parse_args()

_resourceMap = {}
_isCleaning = False
_projectPbxprojPath = ''
_file_dir = ''

# 过滤文件类型
def isResource(file_path):
    if os.path.isfile(file_path):
        if '.mp4' in file_path or '.png' in file_path or '@2x' in file_path or '@3x' in file_path or '@1x' in file_path or '.mp3' in file_path or 'png' in file_path or 'jpg' in file_path or 'gif' in file_path:
            return True
    return False

# 获取项目中所有资源文件的名字和路径
def searchAllResource(file_dir):
    fs = os.listdir(file_dir)
    for dir in fs:
        tmp_path = os.path.join(file_dir, dir)
        if not os.path.isdir(tmp_path):
            # 是一个文件，非目录
            if isResource(tmp_path) == True and '/Pods/' not in tmp_path and '.bundle/' not in tmp_path and '.appiconset' not in tmp_path and '.launchimage' not in tmp_path:
                imageName = tmp_path.split('/')[-1].split('.')[0]
                _resourceMap[imageName] = tmp_path
        elif os.path.isdir(tmp_path) and tmp_path.endswith('.imageset') and '/Pods/' not in tmp_path:
            # 是一个目录且是图片资源文件夹
            imageName = tmp_path.split('/')[-1].split('.')[0]
            _resourceMap[imageName] = tmp_path
        else:
            searchAllResource(tmp_path)

# 搜索project.pbxproj文件的路径并找到没有使用过的资源文件
def searchProjectPathAndFilterUnsedResource(file_dir):
    global _projectPbxprojPath

    fs = os.listdir(file_dir)
    for dir in fs:
        tmp_path = os.path.join(file_dir, dir)
        if not os.path.isdir(tmp_path):
            if tmp_path.endswith('project.pbxproj') and '/Pods/' not in tmp_path:
                print('[project.pbxproj文件路径]' + tmp_path)
                _projectPbxprojPath = tmp_path
            if '/Pods/' not in tmp_path:
                try:
                    filterUnusedResource(tmp_path)
                except Exception as e:
                    pass
                else:
                    pass
                finally:
                    pass
        else:
            searchProjectPathAndFilterUnsedResource(tmp_path)

# 查询资源是否被使用
def filterUnusedResource(tmp_path):
    global _resourceMap
    with open(tmp_path, 'r') as ropen:
        for line in ropen:
            # if tmp_path.split('/')[-1] == 'HXCustomCameraViewController.m':
            #     print(line)
            lineList = line.split('"')
            for item in lineList:
                if item in _resourceMap or item.split('.')[0] in _resourceMap or item + '@1x' in _resourceMap or item + '@2x' in _resourceMap or item + '@3x' in _resourceMap:
                    del _resourceMap[item]
        ropen.close()

# 删除各个未使用的.imageset下的文件
def deleteUnusedResource():
    global _resourceMap

    for resName in list(_resourceMap.keys()):

        tmp_path = _resourceMap[resName]
        if tmp_path.endswith('.imageset'):
            if os.path.exists(tmp_path) and os.path.isdir(tmp_path):
                try:
                    delImagesetFolder(tmp_path)
                    del _resourceMap[resName]
                    print('[删除垃圾资源成功]' + tmp_path)
                except OSError as e:
                    print('[删除垃圾资源失败][' + str(e) + ']' + tmp_path)
            else:
                print('[删除垃圾资源失败]'+ '资源不存在' + tmp_path)

    deleteResourceAtProjectPbxprojAndLocal()

# 删除imageset
def delImagesetFolder(rootdir):
    fileList = []
    fileList = os.listdir(rootdir)

    for f in fileList:
        fielpath = os.path.join(rootdir, f)
        if os.path.isfile(fielpath):
            os.remove(fielpath)
        elif os.path.isdir(fielpath):
            shutil.rmtree(fielpath, True)
    shutil.rmtree(rootdir, True)

# 删除引用到工程中且未使用资源文件
def deleteResourceAtProjectPbxprojAndLocal():
    global _projectPbxprojPath

    if _projectPbxprojPath != None:
        _projectContainReMap = []
        file_data = ''
        ropen = open(_projectPbxprojPath, 'r')
        for line in ropen:
            contain = False
            for resName in _resourceMap:
                if resName in line:
                    contain = True
                    if resName not in _projectContainReMap:
                        _projectContainReMap.append(resName)

            if contain == False:
                file_data += line
        ropen.close()

        wopen = open(_projectPbxprojPath, 'w')
        wopen.write(file_data)
        wopen.close()

        # 删除了project.pbxproj 中引用资源文件的代码之后，在项目路径中删除资源文件
        for item in _projectContainReMap:
            tmp_path = _resourceMap[item]
            if os.path.exists(tmp_path) and not os.path.isdir(tmp_path):
                os.remove(tmp_path)
                del _resourceMap[item]
                print('[删除未使用资源成功]' + tmp_path)
            else:
                pass

# 执行方法
def startClear(file_dir, ignoreList):
    global _isCleaning
    if _isCleaning == True:
        return
    _isCleaning = True
    print('-' * 30 + '程序启动' + '-' * 30 )
    print('[输入的工程路径：]' + file_dir)

    print('-' * 20 + '开始读取全部资源文件' + '-' * 20)
    searchAllResource(file_dir)
    print('-' * 20 + '打印全部资源文件列表' + '-' * 20)
    print(_resourceMap)

    searchProjectPathAndFilterUnsedResource(file_dir)
    if _projectPbxprojPath is None:
       print('找不到project.pbxproj')
       return

    for item in ignoreList:
         if item in list(_resourceMap.keys()):
             del _resourceMap[item]

    print('-' * 20 + '项目未使用的资源文件' + '-' * 20)
    for item in list(_resourceMap.keys()):
          print(item)

    print('-' * 20 + '未使用资源文件删除中' + '-' * 20)
    deleteUnusedResource()
    print('-' * 20 + '删除完成' + '-' * 20 )

    print('-' * 20 + '包含在工程文件目录中但未引入且未在代码中使用的资源,需要程序开发者确认' + '-' * 20)
    # 这种可能是拖入到工程目录时选择了'creat folder reference' 而不是 'Creat group'，或者是完全没有拖入到项目的文件
    for item in list(_resourceMap.values()):
          print(item)


def main():
    startClear(args.file,args.ignore)
    # startClear(' /Users/xjk/Desktop/XJKHealth1月开发分支版本', [])

if __name__ == '__main__':
    main()