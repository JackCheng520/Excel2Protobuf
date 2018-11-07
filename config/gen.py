#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("./scripts")

import os, platform, shutil, xls2pb

work_dir = os.path.abspath(os.getcwd())
tmp_dir = os.path.join(work_dir, "scripts/tmp/")
protoc_exe = os.path.join(work_dir, "bin/protoc/protoc")
protogen_exe = os.path.join(work_dir, "bin/ProtoGen/protogen")


# 创建目录结构
if os.path.exists(tmp_dir):
	shutil.rmtree(tmp_dir)
os.mkdir(tmp_dir)

xls_files = []

# 获得excel列表
files = os.listdir(work_dir)
for file in files:
	if file.endswith(".xls") and file[0] != "~":
		xls_files.append(os.path.abspath(os.path.join(work_dir, file)))

for xls in xls_files:
	print("generating " + xls)
	# 生成proto文件
	generator = xls2pb.SheetInterpreter(xls, tmp_dir, protoc_exe)
	protos = generator.generate()

	# 导出数据
	parser = xls2pb.DataParser(xls, tmp_dir)
	parser.parse()

	# 生成csharp
	for proto in protos["cs"]:
		#拆分文件和拓展名
		(filepath, tempfilename) = os.path.split(proto)
		(shotname, extension) = os.path.splitext(tempfilename)
		path_proto_name = "./scripts/tmp/" + shotname + ".proto"
		path_desc_name = tmp_dir + shotname + ".protodesc"
		path_cs_name = tmp_dir + shotname + ".cs"

		#设置生成CS文件指令
		cmd_proto2desc = "call " + protoc_exe + " " + path_proto_name + " --descriptor_set_out=" + path_desc_name
		cmd_desc2cs = "call " + protogen_exe + " -i:" + path_desc_name + " -o:" + path_cs_name

		try:
			os.system(cmd_proto2desc)
			os.system(cmd_desc2cs)
		except BaseException, e:
			print "protoc failed!"
			raise

#拷贝文件到客户端
client_dir = os.path.join(work_dir, "../../qin-client")
if os.path.exists(client_dir):
	#删除原始的CS文件
	dest_dir = os.path.join(client_dir, "Qin/Assets/Scripts/Config")
	dest_dir = os.path.abspath(dest_dir)
	files = os.listdir(dest_dir)
	for file in files:
		if file.endswith(".cs") or file.endswith(".meta"):
			target_file = os.path.join(dest_dir, file)
			os.remove(target_file)

	#拷贝生成好的CS文件到 dest_dir
	datas = []
	files = os.listdir(tmp_dir)
	for file in files:
		if file.endswith(".cs"):
			src_file = os.path.join(tmp_dir, file)
			print ("copy " + src_file)
			shutil.copy(src_file, dest_dir)
		if file.endswith(".cs"):
			datas.append(file[:-3] + ".bytes")

	#拷贝*.bytes文件到目标目录
	dest_dir = os.path.join(client_dir, "Qin/Assets/AllOfResources/Prefab/Config")
	dest_dir = os.path.abspath(dest_dir)
	files = os.listdir(dest_dir)
	for file in files:
		if file.endswith(".bytes") or file.endswith(".meta"):
			target_file = os.path.join(dest_dir, file)

	files = os.listdir(tmp_dir)
	for data in datas:
		src_file = os.path.join(tmp_dir,data)
		print ("copy " + src_file)
		shutil.copy(src_file,dest_dir)

print("===============================generating success!===============================")

if platform.system() == "Windows":
	os.system("@pause")
