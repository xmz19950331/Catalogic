#!/usr/bin/python
import os
import re



stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'the'])
not_stopword = lambda c: len(c) > 0 and c != ' ' and  (c.strip().lower() not in stopwords) and c.strip().isalpha()
record = []

def search(path, filename):
    if os.path.isdir(path):
        children = os.listdir(path)
        for child in children:
            child_path = os.path.join(path, child)
            if child == filename:   
                if os.path.isfile(child_path):
                    return child_path
            else:
                if os.path.isdir(child_path):
                    ret = search(child_path, filename)
                    if ret: return ret

def file_iter(root, regex=None):
    if os.path.isdir(root):
        children = os.listdir(root)
        for child in children:
            child_path = os.path.join(root, child)
            if os.path.isdir(child_path):
                child_iter = file_iter(child_path, regex)
                for grand_child in child_iter:
                    yield grand_child
            elif os.path.isfile(child_path):
                if regex:
                    if not regex.match(child):
                        continue
                yield child_path

def find_first(iter):
    for i in iter:
        if i is not None:
            return i

def transfer(s, abbr_dict, str_dict):
    # print ">>", s, "<<"
    l = s.strip().split('+')
    str = ''
    cnt = 0
    tags = []
    params = []
    for i in l:
        i = i.strip()
        if i[0] == i[-1] == '"':
            if i[-2] == " ":
                string = i[1:-1]
            else:
                string = i[1:-1] + ' '
            print ">>%s<<" % string
            str += string
            tag_string = string.replace(":", " ").replace(".", " ").replace(",", " ")
            tags.extend(string.split())
        else:
            str += "{%d}" % cnt
            params.append(i)
            cnt += 1
    if not tags:
        return s

    # To avoid redundancy
    if str in str_dict:
        tag = str_dict[str]
    else:
        tag = "_".join((filter(not_stopword, tags))).upper()
     
        if not tag:
            tag = "DUMMY_STR_%003d" % str_dict['__DUMMY__']
            str_dict['__DUMMY__'] += 1

        abbr_dict[tag] = str
        str_dict[str] = tag

    if cnt > 0:
        #ret_str = "String.format( LogMessages." + tag + ".toString(), " + ", ".join(params) + ")"
        #ret_str = "messageSource.getMessage(XSBEnv.getLogLocale(), LogMessages." + tag + ".toString(), " + ", ".join(params) + ")"
        ret_str = "messageSource.getMessage(XSBEnv.getLogLocale(), LogMessages." + tag + "," + ", ".join(params) + ")"
    else:
        #ret_str = "LogMessages." + tag + ".toString()"
        ret_str = "messageSource.getMessage(XSBEnv.getLogLocale(), LogMessages." + tag + ")"

    print "%s=%s" % (tag, str)
    print ret_str
    return ret_str

def scan(filepath, abbr_dict, str_dict, action, count,bundle):
    if not os.path.isfile(filepath): return
    
    regex = re.compile(
            r'logger\.\w+?\((.+?)\);|LogUtil\.jobLog\w*\(logger,(.+?)(, e|)\);|String message = (.+?);|XSBException\((.+?)(, e|)\);',
            #r'logger\.\w+?\((.+?)\);|LogUtil\.jobLog\w*\(logger,(.+?)(, e|)\);|String message = (.+?);',
            re.S
            )
    ret = None

    with open(filepath, 'r') as f:
        if action == "--convert":
            content = f.read()
            if regex.search(content):
                
                #package = "import "+ content.split('\n')[0].split(" ")[1][:-1] + ".messages.LogMessages;"

                #end_1st_line = 0
                print(bundle)

                for m in re.finditer("import ", content):
                    s_line = m.start()
                    e_line = m.end()    

                for m in re.finditer("import " + bundle, content):
                    s_line = m.start()
                    e_line = m.end()



                while content[e_line] != ";":
                    e_line += 1

                package1 = "import "+ bundle + ".messages.LogMessages;"
                package2 = "import org.springframework.beans.factory.annotation.Autowired;"
                package3 = "import com.syncsort.dp.xsb.commons.context.EnumMessageSource;"
                package4 = "import com.syncsort.dp.xsb.commons.env.XSBEnv;"
                ##detect 4 packages
                if package1 not in content:
                    content = content[:e_line + 2] + package1 + "  //auto-imported\n" + content[e_line + 2:]
                    global record
                    #record.append("files: " + filepath + "auto import package:" + package1)

                if package2 not in content:
                    content = content[:e_line + 2] + package2 + "  //auto-imported\n" + content[e_line + 2:]
                    #record.append("files: " + filepath + "auto import package:" + package2)

                if package3 not in content:
                    content = content[:e_line + 2] + package3 + "  //auto-imported\n" + content[e_line + 2:]
                    #record.append("files: " + filepath + "auto import package:" + package3)

                if package4 not in content:
                    content = content[:e_line + 2] + package4 + "  //auto-imported\n" + content[e_line + 2:]
                    #record.append("files: " + filepath + "auto import package: " + package4)

                ##detect auto-wired
                auto_wired = "private EnumMessageSource messageSource;"
                if auto_wired not in content:
                    if re.search(r'public.+?class', content):
                        for m in re.finditer(r'public.+?class', content):
                            autowired_line_s = m.start()
                            autowired_line_e = m.end()
                            break
                        while content[autowired_line_e] != "\n":
                            autowired_line_e += 1
                        content = content[:autowired_line_e + 1] + "\n" + "    @Autowired\n" + "    " + auto_wired + "  //auto-imported\n" + content[autowired_line_e + 1:]

                    record.append("files: " + filepath + " need auto-wired check")

                if re.search(r'XSBException\((.+?)(, e)\);',content):
                    record.append("XSBException CHECK======" + filepath)


                match = regex.finditer(content)        
                reps = []
                poses = []
                print "+" * 50
                for each in match:
                    count += 1
                    string = find_first(each.groups())
                    s, e = each.start(), each.end()
                    whole_string = content[s: e]
                    print string
                    m = re.search(re.escape(string), whole_string)
                    _s, _e = m.start(), m.end()
                    transfered_part = transfer(whole_string[_s: _e], abbr_dict, str_dict)
                    transfered_whole = whole_string[:_s] + transfered_part + whole_string[_e:] 
                    reps.append(transfered_whole)
                    poses.append((s, e))
                ret = replace(content, poses, reps)
                print "+" * 50

        elif action == "--report":
            ret = None
            lines = f.readlines()
            for line in range(len(lines)):
                match = regex.search(lines[line])
                if match:
                    count += 1
                    errorline = str(line) + lines[line]
                    print errorline
            # print ret
    # ret = None
    if ret:
        with open(filepath, 'w') as f:
            f.write(ret)
    return count   


def replace(ori, pos, rep):
    ret = ""
    last_e = 0
    for i, (s, e) in enumerate(pos):
        ret += ori[last_e:s]
        last_e = e
        ret += rep[i]
    if pos:
        print ">>>", pos[-1]
        ret += ori[pos[-1][1]:]
    return ret



if __name__ == '__main__':
    import sys
    #print search(sys.argv[1], sys.argv[2])
    #for file in file_iter(sys.argv[1], None if len(sys.argv) == 2 else re.compile(sys.argv[2])):
    #    print file
    dic = dict()
    strs = {'__DUMMY__': 0}

    JAVA = search(sys.argv[1], "LogMessages.java")
    PROPERTY = search(sys.argv[1], "logMessages.properties")
    ACTION = sys.argv[2]
    count = 0
    pointer = len(sys.argv[1]) - 1
    while(sys.argv[1][pointer] != "/"):
        pointer -= 1
    BUNDLE = sys.argv[1][pointer+1:]
    
    if not JAVA or not PROPERTY:
        print "No LogMessages.java or logMessages.properties"
        quit(1)

    for file in file_iter(sys.argv[1], re.compile(r".+\.java")):
        # pass
        # print file
        print "Scanning", file
        count = scan(file, dic, strs, ACTION, count, BUNDLE)
    
    # quit(0)
    if ACTION == "--convert":
        with open(PROPERTY, 'a') as f:
            f.write('\n\n#Auto Generated (ming)\n')
            for tag in sorted(dic.keys()):
                f.write("%s=%s\n" % (tag, dic[tag]))

        lines = []
        with open(JAVA, 'r') as f:
            content = f.read().strip()
            lines = content.split('\n')
            lines = lines[:-1]
            lines[-1] += ","
            lines.append("    //Auto Generated (ming)")
            for tag in sorted(dic.keys()):
                lines.append("    %s," % tag)
            lines.append('}')

        with open(JAVA, 'w') as f:
            f.write('\n'.join(lines))

        print("*" * 50)
        for r in record:
            print(r)


    if ACTION == "--report":
        print ("For bundle: " + sys.argv[1])
        print ("There are %s lines detected in total" % count) 
        
