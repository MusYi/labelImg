import os
import re
import sys

# 预设标签
RULE = r"(?ms)(\n^\s<object>\n\s*?<name>)({})(</name>.*?</object>$)" # 标签字符串匹配规则
TYPES = {
    "TYPE_ANY": ".*?",  # 匹配所有标签
    "TYPE_NUM": "\d*?", # 匹配所有数字
    "TYPE_CN": "[\u4e00-\u9fa5]*?", # 匹配所有汉字
    "TYPE_EN": "[a-zA-Z]*?", # 匹配所有英文
}
def get_rule(labelortype):
    return RULE.format(TYPES.get(labelortype, labelortype))

def usage():
    print("用于批量处理xml格式的图像标注标签，使用方式如下：\n"
          "python label_handle.py <命令>\n"
          "    <命令>，不区分大小写：\n"
          "        查看帮助  ：-h 或 help\n"
          "        交互模式  ：-i 或 interact\n"
          "        查看标签  ：-l 或 list\n"
          "        删除标签  ：-d 或 del\n"
          "        替换标签  ：-c 或 change\n"
          "        大小写转换：-s 或 swap\n"
          "        \n"
          "        -l <标签目录>\n"
          "        \n"
          "        -d <标签目录> <输出目录> <标签1> [标签2] [...]\n"
          "        \n"
          "        -c <标签目录> <输出目录> <修改标签> <替换标签>\n"
          "        \n"
          "        -s <标签目录> <输出目录> <标签1> [标签2] [...]\n"
          "        \n"
          "        <标签>输入`TYPE_NUM`可以表示所有纯数字标签\n"
          "              输入`TYPE_CN`可以表示所有纯汉字标签\n"
          "              输入`TYPE_EN`可以表示所有纯英文标签\n"
          "        \n"
          "        <输出目录>输入`-`表示直接修改源文件\n"
    )
    sys.exit()

def path_handle(data_path, output_path):
    # 判断路径合法性和是否存在
    # 输出路径不存在则创建
    assert os.path.exists(data_path)
    assert os.path.exists(output_path)

def interact():
    # 提示信息
    print("首先根据提示输入路径，之后可以运行一下命令：\n"
          "    list：查看所有标签\n"
          "    change <修改标签> <替换标签>：替换标签\n"
          "    del <标签1> [标签2] [...]：删除指定标签\n"
          "    swap <标签1> [标签2] [...]：反转指定标签大小写\n"
          "    exit：退出\n"
    )
    # 设置路径
    data_path = input("输入标签文件目录：")
    output_path = input("输入输出文件目录，留空或输入`-`表示直接修改源文件：")
    if not output_path or output_path=="-": output_path = data_path
    path_handle(data_path, output_path)
    # 运行交互模式
    while True:
        cmd = input(">> ").split(" ")
        if len(cmd) < 0:
            continue
        cmd_type = cmd[0].lower()
        if cmd_type in ["-l", "list"]:
            # 查看所有标签
            list_label(data_path, output_path, *cmd[1:])
        elif cmd_type in ["-c", "change"]:
            # 替换标签
            change_label(data_path, output_path)
        elif cmd_type in ["-d", "del"]:
            # 删除标签
            del_label(data_path, output_path, *cmd[1:])
        elif cmd_type in ["-s", "swap"]:
            # 交换大小写
            swap_label(data_path, output_path, *cmd[1:])
        elif cmd_type in ["-e", "exit"]:
            # 推出
            exit()
        else:
            print("命令无效！")

def list_label(data_path):
    # 获取文件列表
    file_list = os.listdir(data_path)
    # 遍历文件
    label_dict = {}
    label_cnt = 0
    file_cnt = 0
    for file in file_list:
        # 筛选文件
        if file.split(".")[-1] != "xml": # 跳过非xml文件
            continue
        file_cnt += 1
        file_path = os.path.join(data_path, file)
        # 读文件
        with open(file_path, 'r', encoding="utf-8") as f:
            match = re.findall(get_rule("TYPE_ANY"), f.read())
        if match: # 如果文件中匹配到标签
            for lab in match:
                label_cnt += 1
                label_dict[lab[1]] = label_dict.get(lab[1], 0) + 1
        else:
            # print(f"{file_path}中没有标签")
            pass
    # # 输出
    # print(f"共计文件{file_cnt}个，标签{label_cnt}个")
    # print("标签有：", end="")
    # for l in sorted(label_dict):
    #     print(f"{l}:{label_dict[l]}", end="  ")
    # print("")
    return label_dict

def change_label(data_path, output_path, change_from, change_to):
    # 获取文件列表
    file_list = os.listdir(data_path)
    if output_path == "-":
        output_path = data_path
    # 遍历文件
    for file in file_list:
        if file.split(".")[-1] != "xml": # 跳过非xml文件
            continue
        file_path = os.path.join(data_path, file)
        outfile_path = os.path.join(output_path, file)
        # 读文件
        with open(file_path, 'r', encoding="utf-8") as f:
            rst = f.read()
        fun = lambda matchobj: matchobj.group(1) + change_to + matchobj.group(3) 
        rst = re.sub(get_rule(change_from), fun, rst)
        # 写文件
        with open(outfile_path, 'w', encoding="utf-8") as f:
            f.write(rst)
    # 提示
    print("修改完成")

def del_label(data_path, output_path, *labels):
    # 获取文件列表
    file_list = os.listdir(data_path)
    if output_path == "-":
        output_path = data_path
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    # 遍历文件
    for file in file_list:
        if file.split(".")[-1] != "xml": # 跳过非xml文件
            continue
        file_path = os.path.join(data_path, file)
        outfile_path = os.path.join(output_path, file)
        # 读文件
        with open(file_path, 'r', encoding="utf-8") as f:
            rst = f.read()
        # 删除指定标签
        for label in labels:
            rst = re.sub(get_rule(label), "", rst)
        # 判断是否还有标签
        match = re.findall(get_rule("TYPE_ANY"), rst)
        if match:
            # 写文件
            with open(outfile_path, 'w', encoding="utf-8") as f:
                f.write(rst)
        elif os.path.exists(outfile_path):
            os.remove(outfile_path)
    # 提示
    print("修改完成")

def swap_label(data_path, output_path, *labels):
    # BUG 无法正确处理预设类型
    # 获取文件列表
    file_list = os.listdir(data_path)
    if output_path == "-":
        output_path = data_path
    # 遍历文件
    for file in file_list:
        # 筛选和处理文件路径
        if file.split(".")[-1] != "xml": # 跳过非xml文件
            continue
        file_path = os.path.join(data_path, file)
        outfile_path = os.path.join(output_path, file)
        # 读文件
        with open(file_path, 'r', encoding="utf-8") as f:
            rst = f.read()
        # 处理标签
        for label in labels:
            # 处理预设类型
            fun = lambda matchobj: matchobj.group(1) + \
                matchobj.group(2).swapcase() + matchobj.group(3)
            rst = re.sub(get_rule(label), fun, rst)
        # 写文件
        with open(outfile_path, 'w', encoding="utf-8") as f:
            f.write(rst)
    # 提示
    print("修改完成")

if __name__ == "__main__":
    # 处理参数，进行处理
    if len(sys.argv) < 2:
        # 交互模式
        interact()
    cmd = sys.argv[1].lower()
    if cmd in ["-h", "help"]:
        usage()
    elif cmd in ["-i", "interact"]:
        # 交互模式
        interact()
    elif cmd in ["-l", "list"]:
        # 查看所有标签
        list_label(sys.argv[2])
    elif cmd in ["-c", "change"]:
        # 替换标签
        change_label(*sys.argv[2:])
    elif cmd in ["-d", "delete"]:
        # 删除标签
        del_label(*sys.argv[2:])
    elif cmd in ["-s", "swap"]:
        # 交换大小写
        swap_label(*sys.argv[2:])
    else:
        usage()