import json
from tqdm import tqdm
from ast_util import get_ast, get_formal_parameter, get_all_subtree
import re


def confirm_param_num(target):
    global parameter_num
    count = 0
    list12 = []
    str1_full = ""
    tree = get_ast(target["original_code"], [], [], [])
    if tree:
        try:
            ls = get_formal_parameter(tree)
            parameter_num = len(ls)
        except:
            pass

    list12 = target['original_nl']
    for slice in list12:
        str1_full = str1_full + slice

    str1_full = ''.join(list12)

    paramlist = [m.start() for m in re.finditer('@param', str1_full)]
    x = len(paramlist)
    if x == parameter_num:
        count = 1
    else:
        count = 0

    return count


def find_str_index(substr, str):
    result = []
    index = 0
    while str.find(substr, index, len(str)) != -1:
        tem_index = str.find(substr, index, len(str))
        result.append(tem_index)
        index = tem_index + 1
    return result


def get_all_nl_with_its_tree(dataset):
    total_dic = {}
    for obj in tqdm(dataset):
        try:
            if confirm_param_num(obj) == 1:
                nl_dic = {}
                nl_dic['param_list'] = []

                param_index_list = find_str_index('@param', obj['original_nl'])
                ast = get_ast(obj['original_code'], [], [], [])
                subtree = get_all_subtree(ast)
                for i in param_index_list:
                    n_index = obj['original_nl'].find('\n', i)
                    a = obj['original_nl'][i:n_index]
                    index = a.find(' ')
                    index2 = a.find(' ', index + 1)
                    if index2 < index:
                        index2 = index
                    a = a[index2 + 1:]
                    nl_dic['param_list'].append(a)

                nl_dic['all_param_subtree'] = subtree
                nl_dic['nl'] = obj['nl']
                id = obj['id']

            total_dic[str(id)] = nl_dic
        except(BaseException):
            pass

    return total_dic


def get_sbt(cur_root_id, node_list):
    index = {}
    i = 0
    for item in node_list:
        index[item['id']] = i
        i += 1
    cur_root = node_list[cur_root_id]
    tmp_list = []
    tmp_list.append("(")
    str = cur_root['value']
    tmp_list.append(str)
    if 'children' in cur_root:
        chs = cur_root['children']
        for ch in chs:
            tmp_list.extend(get_sbt(index[ch], node_list))
    tmp_list.append(")")
    tmp_list.append(str)
    return tmp_list


def write_file(filename, dataset):
    with open(filename, 'w+') as f:
        for i in tqdm(range(len(dataset))):
            f.writelines((repr(dataset[i])[1:-1]))
            f.writelines('\n')
    f.close()



if __name__ == '__main__':
    with open('dataset/Filter.json') as file:
        dataset = json.load(file)
        total_dict = get_all_nl_with_its_tree(dataset)
        ast_dataset = []
        method_nl_dataset = []
        nl_dataset = []
        for key in tqdm(total_dict.keys()):
            if 'all_param_subtree' in total_dict[key]:
                subtree_num = len(total_dict[key]['all_param_subtree'])
                nl_num = len(total_dict[key]['param_list'])
                if subtree_num != nl_num: continue

                for item in total_dict[key]['all_param_subtree']:
                    ast_dataset.append(item)

                for item in total_dict[key]['param_list']:
                    nl_dataset.append(item)
                    method_nl_dataset.append(total_dict[key]['nl'])

        print('Generating SBT')
        SBT_dataset = []
        for subtree in tqdm(ast_dataset):
            SBT_Seq = get_sbt(0, subtree)
            SBT = ' '.join(SBT_Seq)
            SBT_dataset.append(SBT)

        print('exporting dataset')
        write_file('dataset/sbt.txt', SBT_dataset)
        write_file('dataset/method.nl.txt', method_nl_dataset)
        write_file('dataset/param.nl.txt', nl_dataset)

