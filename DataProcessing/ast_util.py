import javalang
import collections
import sys
from javalang.ast import Node
import os
from anytree import AnyNode, RenderTree

edges = {'Nexttoken': 2, 'Prevtoken': 3, 'Nextuse': 4, 'Prevuse': 5, 'If': 6, 'Ifelse': 7, 'While': 8, 'For': 9,
         'Nextstmt': 10, 'Prevstmt': 11, 'Prevsib': 12}


def get_name(obj):
    if (type(obj).__name__ in ['list', 'tuple']):
        a = []
        for i in obj:
            a.append(get_name(i))
        return a
    elif (type(obj).__name__ in ['dict', 'OrderedDict']):
        a = {}
        for k in obj:
            a[k] = get_name(obj[k])
        return a
    elif (type(obj).__name__ not in ['int', 'float', 'str', 'bool']):
        return type(obj).__name__
    else:
        return obj


def process_source(file_name, save_file):
    with open(file_name, 'r', encoding='utf-8') as source:
        lines = source.readlines()
    with open(save_file, 'w+', encoding='utf-8') as save:
        for line in lines:
            code = line.strip()
            tokens = list(javalang.tokenizer.tokenize(code))
            tks = []
            for tk in tokens:
                if tk.__class__.__name__ == 'String' or tk.__class__.__name__ == 'Character':
                    tks.append('STR_')
                elif 'Integer' in tk.__class__.__name__ or 'FloatingPoint' in tk.__class__.__name__:
                    tks.append('NUM_')
                elif tk.__class__.__name__ == 'Boolean':
                    tks.append('BOOL_')
                else:
                    tks.append(tk.value)
            save.write(" ".join(tks) + '\n')


def get_token(node):
    token = ''

    if isinstance(node, str):
        token = node
    elif isinstance(node, set):
        token = 'Modifier'
    elif isinstance(node, Node):
        token = node.__class__.__name__

    return token


def get_child(root):

    if isinstance(root, Node):
        children = root.children
    elif isinstance(root, set):
        children = list(root)
    else:
        children = []

    def expand(nested_list):
        for item in nested_list:
            if isinstance(item, list):
                for sub_item in expand(item):
                    yield sub_item
            elif item:
                yield item

    return list(expand(children))


def createtree(root, node, nodelist, parent=None):
    id = len(nodelist)
    token, children = get_token(node), get_child(node)
    if id == 0:
        root.token = token
        root.data = node
    else:
        newnode = AnyNode(id=id, token=token, data=node, parent=parent)
    nodelist.append(node)

    for child in children:
        if id == 0:
            createtree(root, child, nodelist, parent=root)
        else:
            createtree(root, child, nodelist, parent=newnode)


def get_sequence(node, sequence):
    token, children = get_token(node), get_child(node)
    sequence.append(token)
    for child in children:
        get_sequence(child, sequence)


def getnodeandedge(node, nodeindexlist, vocabdict, src, tgt, edgetype):
    token = node.token
    nodeindexlist.append([vocabdict[token]])
    for child in node.children:
        src.append(node.id)
        tgt.append(child.id)
        edgetype.append([0])
        src.append(child.id)
        tgt.append(node.id)
        edgetype.append([0])
        getnodeandedge(child, nodeindexlist, vocabdict, src, tgt, edgetype)


def getedge_nextsib(node, vocabdict, src, tgt, edgetype):
    token = node.token
    for i in range(len(node.children) - 1):
        src.append(node.children[i].id)
        tgt.append(node.children[i + 1].id)
        edgetype.append([1])
        src.append(node.children[i + 1].id)
        tgt.append(node.children[i].id)
        edgetype.append([edges['Prevsib']])
    for child in node.children:
        getedge_nextsib(child, vocabdict, src, tgt, edgetype)


def getedge_flow(node, vocabdict, src, tgt, edgetype, ifedge=False, whileedge=False, foredge=False):
    token = node.token
    if whileedge == True:
        if token == 'WhileStatement' and len(node.children):
            src.append(node.children[0].id)
            tgt.append(node.children[1].id)
            edgetype.append([edges['While']])
            src.append(node.children[1].id)
            tgt.append(node.children[0].id)
            edgetype.append([edges['While']])
    if foredge == True:
        if token == 'ForStatement' and len(node.children):
            src.append(node.children[0].id)
            tgt.append(node.children[1].id)
            edgetype.append([edges['For']])
            src.append(node.children[1].id)
            tgt.append(node.children[0].id)
            edgetype.append([edges['For']])

    if ifedge == True:
        if token == 'IfStatement' and len(node.children):
            src.append(node.children[0].id)
            tgt.append(node.children[1].id)
            edgetype.append([edges['If']])
            src.append(node.children[1].id)
            tgt.append(node.children[0].id)
            edgetype.append([edges['If']])
            if len(node.children) == 3:
                src.append(node.children[0].id)
                tgt.append(node.children[2].id)
                edgetype.append([edges['Ifelse']])
                src.append(node.children[2].id)
                tgt.append(node.children[0].id)
                edgetype.append([edges['Ifelse']])
    for child in node.children:
        getedge_flow(child, vocabdict, src, tgt, edgetype, ifedge, whileedge, foredge)


def getedge_nextstmt(node, vocabdict, src, tgt, edgetype):
    token = node.token
    if token == 'BlockStatement':
        for i in range(len(node.children) - 1):
            src.append(node.children[i].id)
            tgt.append(node.children[i + 1].id)
            edgetype.append([edges['Nextstmt']])
            src.append(node.children[i + 1].id)
            tgt.append(node.children[i].id)
            edgetype.append([edges['Prevstmt']])
    for child in node.children:
        getedge_nextstmt(child, vocabdict, src, tgt, edgetype)


def getedge_nexttoken(node, vocabdict, src, tgt, edgetype, tokenlist):
    def gettokenlist(node, vocabdict, edgetype, tokenlist):
        token = node.token
        if len(node.children) == 0:
            tokenlist.append(node.id)
        for child in node.children:
            gettokenlist(child, vocabdict, edgetype, tokenlist)

    gettokenlist(node, vocabdict, edgetype, tokenlist)
    for i in range(len(tokenlist) - 1):
        src.append(tokenlist[i])
        tgt.append(tokenlist[i + 1])
        edgetype.append([edges['Nexttoken']])
        src.append(tokenlist[i + 1])
        tgt.append(tokenlist[i])
        edgetype.append([edges['Prevtoken']])


def getedge_nextuse(node, vocabdict, src, tgt, edgetype, variabledict):
    def getvariables(node, vocabdict, edgetype, variabledict):
        token = node.token
        if token == 'MemberReference':
            for child in node.children:
                if child.token == node.data.member:
                    variable = child.token
                    variablenode = child
            if 'variable' in locals().keys():
                if not variabledict.__contains__(variable):
                    variabledict[variable] = [variablenode.id]
                else:
                    variabledict[variable].append(variablenode.id)
        for child in node.children:
            getvariables(child, vocabdict, edgetype, variabledict)

    getvariables(node, vocabdict, edgetype, variabledict)

    for v in variabledict.keys():
        for i in range(len(variabledict[v]) - 1):
            src.append(variabledict[v][i])
            tgt.append(variabledict[v][i + 1])
            edgetype.append([edges['Nextuse']])
            src.append(variabledict[v][i + 1])
            tgt.append(variabledict[v][i])
            edgetype.append([edges['Prevuse']])


def get_ast(code, edgesrc, edgetgt, edge_attr):

    code = code.strip()

    try:
        tokens = javalang.tokenizer.tokenize(code)
        parser = javalang.parser.Parser(tokens)

    except(BaseException):
        print("Some error occur while parsing the code\n")
        return False
    try:
        parsetree = parser.parse_member_declaration()
    except (javalang.parser.JavaSyntaxError, IndexError, StopIteration, TypeError):
        return False


    nodelist = []
    newtree = AnyNode(id=0, token=None, data=None)
    createtree(newtree, parsetree, nodelist)
    alltokens = []
    get_sequence(parsetree, alltokens)
    ifcount = 0
    whilecount = 0
    forcount = 0
    blockcount = 0
    docount = 0
    switchcount = 0
    for token in alltokens:
        if token == 'IfStatement':
            ifcount += 1
        if token == 'WhileStatement':
            whilecount += 1
        if token == 'ForStatement':
            forcount += 1
        if token == 'BlockStatement':
            blockcount += 1
        if token == 'DoStatement':
            docount += 1
        if token == 'SwitchStatement':
            switchcount += 1

    alltokens = list(set(alltokens))
    vocabsize = len(alltokens)
    tokenids = range(vocabsize)
    vocabdict = dict(zip(alltokens, tokenids))


    edges = {'Nexttoken': 2, 'Prevtoken': 3, 'Nextuse': 4, 'Prevuse': 5, 'If': 6, 'Ifelse': 7, 'While': 8, 'For': 9,
             'Nextstmt': 10, 'Prevstmt': 11, 'Prevsib': 12}
    x = []

    nextsib = True
    ifedge = True
    whileedge = True
    foredge = True
    blockedge = True
    nexttoken = True
    nextuse = True
    getnodeandedge(newtree, x, vocabdict, edgesrc, edgetgt, edge_attr)
    if nextsib == True:
        getedge_nextsib(newtree, vocabdict, edgesrc, edgetgt, edge_attr)
    getedge_flow(newtree, vocabdict, edgesrc, edgetgt, edge_attr, ifedge, whileedge, foredge)
    if blockedge == True:
        getedge_nextstmt(newtree, vocabdict, edgesrc, edgetgt, edge_attr)
    tokenlist = []
    if nexttoken == True:
        getedge_nexttoken(newtree, vocabdict, edgesrc, edgetgt, edge_attr, tokenlist)
    variabledict = {}
    if nextuse == True:
        getedge_nextuse(newtree, vocabdict, edgesrc, edgetgt, edge_attr, variabledict)


    return newtree


def get_formal_parameter(tree):
    formal_parameter = []
    for child in tree.children:
        if type(child.data) is javalang.tree.FormalParameter:
            formal_parameter.append(child)
    return formal_parameter


def flatten_tree(tree, flatten_list):
    flatten_list.append(tree)
    if len(tree.children) != 0:
        for child in tree.children:
            flatten_tree(child, flatten_list)
    return flatten_list


def find_parameter_node(nodelist, paralist):
    dict = {}
    for node in nodelist:
        if node.is_leaf:
            for parameter in paralist:
                if parameter.children[1].token == node.data:
                    if parameter.children[1].token not in dict:
                        dict[parameter.children[1].token] = []
                    else:
                        dict[parameter.children[1].token].append(node)
    return dict


def get_related_edge(id, edgesrc, edgetgt, edge_attr):
    src = []
    tgt = []
    attr = []
    i = 0
    while i < len(edgesrc):
        if edgesrc[i] == id or edgetgt[i] == id:
            src.append(edgesrc[i])
            tgt.append(edgetgt[i])
            attr.append(edge_attr[i])
        i += 1
    return src, tgt, attr


def get_statement_level_subtree(node):
    if isinstance(node.data, javalang.tree.Statement):
        return node
    if node.parent:
        return get_statement_level_subtree(node.parent)
    return node


def transfer_node(node):
    node_dict = {'id': node.id, 'type': type(node.data).__name__, 'children': []}
    for child in node.children:
        node_dict['children'].append(child.id)
    node_dict['value'] = node.token

    return node_dict


def transfer_ast_to_json(tree):
    nodelist = []
    flatten_tree(tree, nodelist)
    seq = []
    for node in nodelist:
        seq.append(transfer_node(node))
    return seq


def get_all_subtree(tree):
    formal_parameter_list = get_formal_parameter(tree)
    fl = []
    flatten_tree(tree, fl)
    parameter_related_node = find_parameter_node(fl, formal_parameter_list)
    subtree_dict = {}
    for parameter in parameter_related_node:
        if parameter not in subtree_dict:
            subtree_dict[parameter] = []
        for node in parameter_related_node[parameter]:
            subtree_dict[parameter].append(get_statement_level_subtree(node))
    subtree = []
    for parameter in subtree_dict:
        subtree.append(AnyNode(id=0, token=parameter, data=parameter))
        children = subtree_dict[parameter]
        subtree[-1].children = children
        subtree[-1] = transfer_ast_to_json(subtree[-1])
    return subtree
