# 导入相关模块
import os
import random
import re
import time
import tkinter as tk
from tkinter import ttk     # ttk中有更多控件
import sqlite3
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import threading


'''------------------------------链接数据库-----------------------------'''
# JiDanCi.db， 用于各种存储便于界面初始化
def open_jidanci():
    Path = os.getcwd()
    con = sqlite3.connect(Path + r'\dates\Z01.JiDanCi.db')
    cur = con.cursor()      # 使用游标能够灵活检索
    sql = '''CREATE TABLE if not exists GuiA_cbx(Cbx TEXT primary key, num INTEGEB)'''  # 如果不存在就创建表 GuiA_cbx
    cur.execute(sql)    # GuiA_cbx 记录A界面Combobox的选中内容
    con.commit()    # 提交，否者不会实现插入更新操作
    # try:  # 插入已有会出错
    #     cur.execute("INSERT INTO GuiA_cbx VALUES('Book',0)")
    #     con.commit()  # 提交，否者不会实现插入更新操作
    # except Exception as e:
    #     # print(e)
    #     pass
    # try:  # 插入已有会出错
    #     cur.execute("INSERT INTO GuiA_cbx VALUES('Unit',0)")
    #     con.commit()  # 提交，否者不会实现插入更新操作
    # except Exception as e:
    #     # print(e)
    #     pass
    cur.close()
    return con
# wordBank.db， 单词库 表words储存单词（格式查看002）；表CET6储存六级词汇（来自于恋恋有词六级词汇）
# 表wordsFromNow储存记录出现过的单词并记录累次词频；表familiarWords储存喝醉酒都认识的单词
def open_wordbank():
    Path = os.getcwd()
    con = sqlite3.connect(Path + r'\dates\Z02.wordBank.db')
    # cur = con.execute("""CREATE TABLE if not exists words(word TEXT primary key, soundmark TEXT,
    #                  paraphrase TEXT, pronunciation BLOB, picture BLOB)""")
    cur = con.execute("""CREATE TABLE if not exists wordFromNow(word TEXT primary key, frequency INTEGEB,
    firstTime TEXT, paraphrase TEXT, yesOrNo INTEGEB)""")
    con.commit()    # 提交，否者不会实现插入更新操作
    cur = con.execute("CREATE TABLE if not exists familiarWords(word TEXT primary key)")
    con.commit()  # 提交，否者不会实现插入更新操作
    cur.close()
    return con

'''-----------------------------词频统计函数-------------------------------'''
def makeVaryWordsDict():
    vary_words = { }    #元素形式： 变化形式：原型 例如 {acts:act,acting:act,boys:boy....}
    Path = os.getcwd()
    f = open(Path + r'\dates\Z06word_varys.txt', "r", encoding="gbk")
    lines = f.readlines()
    f.close()
    L = len(lines)
    for i in range(0,L,2):  #每两行是一个单词的原型及变化形式
        word = lines[i].strip()     #单词原型
        varys = lines[i+1].strip().split("|")   #变形
        for w in varys:
            vary_words[w] = word  #加入变化形式：原型  , w的原型是 word
    return vary_words
def makeSplitStr(txt):
    splitChars = set([])
    #下面找出所有文件中非字母的字符，作为分隔符
    for c in txt:
        if not ( c >= 'a' and c <= 'z' or c >= 'A' and c <= 'Z'):
            splitChars.add(c)
    splitStr = ""
    #生成用于 re.split的分隔符字符串
    for c in splitChars:
        if c in ['.','?','!','"',"'",'(',')','|','*','$','\\','[',']','^','{','}']:
            splitStr += "\\" + c + "|"
        else:
            splitStr +=  c + "|"
    splitStr+=" "
    return splitStr
def countFile(txt,vary_word_dict):
    splitStr = makeSplitStr(txt)
    words = {}
    lst = re.split(splitStr,txt)
    for x in lst:
        lx = x.lower()
        if lx == "":
            continue
        if lx in vary_word_dict:    # 如果在原型词典里能查到原型，就变成原型再统计
            lx = vary_word_dict[lx]
        # 直接写这句可以替换上面 if 语句  lx = vary_word_dict.get(lx,lx)
        words[lx] = words.get(lx,0) + 1
    return words

'''-----------------------菜单A-------------------------'''
# 菜单A界面布局Gui_A
def Gui_A():
    con = open_jidanci()   # 链接数据库JiDanCi.db，用于界面初始化
    cur = con.cursor()  # 使用游标能够灵活检索
    global frameA       # frameA便于后续清空A界面
    frameA = tk.Frame(root)
    frameA.grid(row=0, column=0, sticky="WENS")
    global GuiA_cbx1, GuiA_cbx2, GuiA_cbx3, GuiA_cbx4       # 用于调用记录cbx的内容
    frameA00 = tk.Frame(frameA, bg="lightslategrey", highlightthickness=0)
    frameA00.grid(row=0, column=0, sticky="NSWE")
    label1 = tk.Label(frameA00, text="选择词本：", height=1, bg="lightslategrey", font=('黑体', 15, 'bold'))
    label1.grid(row=0, column=0,sticky="E")
    GuiA_cbx1 = ttk.Combobox(frameA00)
    GuiA_cbx1["values"] = ("CET-4", "CET-6", "考研")     # 下拉时显示的表象
    GuiA_cbx1["state"] = "readonly"     # 将gWin.cbxCategory设置为不可输入，只能选择
    cur.execute("Select num from GuiA_cbx WHERE Cbx = 'Book'")      # 上一次选择的行
    con.commit()    # 提交，否者不会实现操作
    GuiA_cbx1.current(cur.fetchone()[0])      # 选中上一次的选择
    GuiA_cbx1.bind("<<ComboboxSelected>>", GuiAcbx1_choice)     # 绑定函数GuiAcbx1_choice
    GuiA_cbx1.grid(row=0, column=1,sticky="W")
    frameA00.rowconfigure(0, weight=1)
    frameA00.columnconfigure(0, weight=1)
    frameA00.columnconfigure(1, weight=1)

    frameA10 = tk.Frame(frameA, bg="lightslategrey", highlightthickness=0)
    frameA10.grid(row=1, column=0, sticky="NSWE")
    label2 = tk.Label(frameA10, text="选择单元：", height=1, bg="lightslategrey", font=('黑体', 15, 'bold'))
    label2.grid(row=0, column=0,sticky="E")
    GuiA_cbx2 = ttk.Combobox(frameA10)
    GuiA_cbx2["values"] = ("Unit1: day1-day4", "Unit2: day5-day8", "Unit3: day9-day12", "Unit4: day13-day16",
                           "Unit5: day17-day20", "Unit6: day21-day24", "Unit7: day25-day28")  # 下拉时显示的表象
    GuiA_cbx2["state"] = "readonly"  # 将gWin.cbxCategory设置为不可输入，只能选择
    cur.execute("Select num from GuiA_cbx WHERE Cbx = 'Unit'")      # 上一次选择的行
    con.commit()    # 提交，否者不会实现插入更新操作
    GuiA_cbx2.current(cur.fetchone()[0])      # 选中上一次的选择
    GuiA_cbx2.bind("<<ComboboxSelected>>", GuiAcbx2_choice)
    GuiA_cbx2.grid(row=0, column=1, sticky="W")
    frameA10.rowconfigure(0, weight=1)
    frameA10.columnconfigure(0, weight=1)
    frameA10.columnconfigure(1, weight=1)

    frameA20 = tk.Frame(frameA, bg="lightslategrey", highlightthickness=0)
    frameA20.grid(row=2, column=0, sticky="NSWE")
    label3 = tk.Label(frameA20, text="选择分组：", height=1, bg="lightslategrey", font=('黑体', 15, 'bold'))
    label3.grid(row=0, column=0, sticky="E")
    GuiA_cbx3 = ttk.Combobox(frameA20)
    GuiA_cbx3["state"] = "readonly"  # 将gWin.cbxCategory设置为不可输入，只能选择
    if "Unit1" in GuiA_cbx2.get():
        GuiA_cbx3["values"] = ("Day1", "Day2", "Day3", "Day4")  # 下拉时显示的表象
    elif "Unit2" in GuiA_cbx2.get():
        GuiA_cbx3["values"] = ("Day5", "Day6", "Day7", "Day8")  # 下拉时显示的表象
    elif "Unit3" in GuiA_cbx2.get():
        GuiA_cbx3["values"] = ("Day9", "Day10", "Day11", "Day12")
    elif "Unit4" in GuiA_cbx2.get():
        GuiA_cbx3["values"] = ("Day13", "Day14", "Day15", "Day16")
    elif "Unit5" in GuiA_cbx2.get():
        GuiA_cbx3["values"] = ("Day17", "Day18", "Day19", "Day20")
    elif "Unit6" in GuiA_cbx2.get():
        GuiA_cbx3["values"] = ("Day21", "Day22", "Day23", "Day24")
    elif "Unit7" in GuiA_cbx2.get():
        GuiA_cbx3["values"] = ("Day25", "Day26", "Day27", "Day28")
    GuiA_cbx3.current(0)  # 选中第0项
    GuiA_cbx3.grid(row=0, column=1, sticky="W")
    frameA20.rowconfigure(0, weight=1)
    frameA20.columnconfigure(0, weight=1)
    frameA20.columnconfigure(1, weight=1)

    frameA30 = tk.Frame(frameA, bg="lightslategrey", highlightthickness=0)
    frameA30.grid(row=3, column=0, sticky="NSWE")
    label4 = tk.Label(frameA30, text="选择模式：", height=1, bg="lightslategrey", font=('黑体', 15, 'bold'))
    label4.grid(row=0, column=0, sticky="E")
    GuiA_cbx4 = ttk.Combobox(frameA30)
    GuiA_cbx4["values"] = ("原序", "乱序", "字母顺序")
    GuiA_cbx4["state"] = "readonly"     # 将gWin.cbxCategory设置为不可输入，只能选择
    GuiA_cbx4.current(0)  # 选中第0项
    GuiA_cbx4.grid(row=0, column=1, sticky="W")
    frameA30.rowconfigure(0, weight=1)
    frameA30.columnconfigure(0, weight=1)
    frameA30.columnconfigure(1, weight=1)

    frameA40 = tk.Frame(frameA, bg="lightslategrey", highlightthickness=0)
    frameA40.grid(row=4, column=0, sticky="NSWE")
    frameA40_Button1 = tk.Button(frameA40, text="记录板", height=1, width=20, command=frameA40_Button1_Clicked)
    frameA40_Button1.grid(row=0, column=0, sticky="E")
    frameA40_Button2 = tk.Button(frameA40, text="记单词", height=1, width=20, command=frameA40_Button2_Clicked)
    frameA40_Button2.grid(row=0, column=1, sticky="W")
    frameA40.rowconfigure(0, weight=1)
    frameA40.columnconfigure(0, weight=1)
    frameA40.columnconfigure(1, weight=1)

    frameA.rowconfigure(0, weight=1)
    frameA.rowconfigure(1, weight=1)
    frameA.rowconfigure(2, weight=1)
    frameA.rowconfigure(3, weight=1)
    frameA.rowconfigure(4, weight=1)
    frameA.columnconfigure(0, weight=1)            # 窗口对象第一列里面的东西随着窗口自动上下填满
    cur.close()  # 关闭Cursor对象
    con.close()  # 关闭Connnection
    return
# 记录GuiA_cbx1中内容
def GuiAcbx1_choice(event):
    con = open_jidanci()
    cur = con.cursor()      # 使用游标能够灵活检索
    if "CET-4" in GuiA_cbx1.get():
        cur.execute("UPDATE GuiA_cbx SET num = 0 WHERE Cbx = 'Book'")
    elif "CET-6" in GuiA_cbx1.get():
        cur.execute("UPDATE GuiA_cbx SET num = 1 WHERE Cbx = 'Book'")
    elif "考研" in GuiA_cbx1.get():
        cur.execute("UPDATE GuiA_cbx SET num = 2 WHERE Cbx = 'Book'")
    con.commit()  # 提交，否者不会实现插入更新操作
    cur.close()  # 关闭Cursor对象
    con.close()  # 关闭Connnection
# 记录GuiA_cbx2中内容，并在GuiA_cbx2中内容更换的时，GuiA_cbx3中的内容随之变换
def GuiAcbx2_choice(event):
    if "Unit1" in GuiA_cbx2.get():
        GuiAcbx2_num = 0
        GuiA_cbx3["values"] = ("Day1", "Day2", "Day3", "Day4")  # 下拉时显示的表象
    elif "Unit2" in GuiA_cbx2.get():
        GuiAcbx2_num = 1
        GuiA_cbx3["values"] = ("Day5", "Day6", "Day7", "Day8")  # 下拉时显示的表象
    elif "Unit3" in GuiA_cbx2.get():
        GuiAcbx2_num = 2
        GuiA_cbx3["values"] = ("Day9", "Day10", "Day11", "Day12")
    elif "Unit4" in GuiA_cbx2.get():
        GuiAcbx2_num = 3
        GuiA_cbx3["values"] = ("Day13", "Day14", "Day15", "Day16")
    elif "Unit5" in GuiA_cbx2.get():
        GuiAcbx2_num = 4
        GuiA_cbx3["values"] = ("Day17", "Day18", "Day19", "Day20")
    elif "Unit6" in GuiA_cbx2.get():
        GuiAcbx2_num = 5
        GuiA_cbx3["values"] = ("Day21", "Day22", "Day23", "Day24")
    else:
        GuiAcbx2_num = 6
        GuiA_cbx3["values"] = ("Day25", "Day26", "Day27", "Day28")
    GuiA_cbx3.current(0)    # 选中第0项
    con = open_jidanci()
    cur = con.cursor()      # 使用游标能够灵活检索
    sql = "UPDATE GuiA_cbx SET num = %d WHERE Cbx = 'Unit'"%(int(GuiAcbx2_num))
    cur.execute(sql)
    con.commit()    # 提交，否者不会实现插入更新操作
    cur.close()     # 关闭Cursor对象
    con.close()     # 关闭Connnection
    return
# A界面按钮对应的command, 调出 记录版 和 天天记单词
def frameA40_Button1_Clicked():
    Path = os.getcwd()
    f = open(Path + r"\dates\Z08.tianTian_JiLuBan.txt", 'r')
    inheretxt = f.read()
    f.close()
    root1 = tk.Toplevel(root)
    root1.title('记录版')
    root1.geometry("255x265")
    text = tk.Text(root1)
    text.grid(row=0, column=0, padx=5, pady=5, sticky="NSWE")
    scrollbar1 = tk.Scrollbar(root1)
    scrollbar1.grid(row=0, column=1, padx=0, pady=5, sticky="NS")
    text['yscrollcommand'] = scrollbar1.set        #链接 文本 和 滚动条
    scrollbar1['command'] = text.yview
    root1.rowconfigure(0, weight=1)
    root1.columnconfigure(0, weight=1)
    text.insert(tk.END, inheretxt)
    root1.grab_set()
    root1.mainloop()
def frameA40_Button2_Clicked():
    # 点击按钮记单词的同时将时间和书本单元写入记录版
    time1 = time.strftime("%Y-%m-%d %X", time.localtime())
    str1 = GuiA_cbx1.get()
    str2 = GuiA_cbx3.get()
    str3 =  str1 +' '+ str2 + ' ' +time1 + '\n\n'
    Path = os.getcwd()
    f = open(Path + r"\dates\Z08.tianTian_JiLuBan.txt", 'a')
    f.write(str3)
    f.close()
    global wordsBankOfCET6, sum_unit, sum_remain
    if GuiA_cbx1.get() == "CET-4":
        wordsBankOfCET6 = getWordsOfCET4()
    elif GuiA_cbx1.get() == "CET-6":
        wordsBankOfCET6 = getWordsOfCET6()
    elif GuiA_cbx1.get() == "考研":
        wordsBankOfCET6 = getWordsOfKaoYanCiHui()
    sum_words = len(wordsBankOfCET6)    # sum_words 单词总数
    sum_unit = sum_words//28    # 每个单元的单词数量
    sum_remain = sum_words - (sum_words//28)*28
    global indexNum, sum_dayWords, dayWords
    # 设置 minIndexNum 和 maxIndexNum 用于截取单词分组
    if GuiA_cbx3.get() == "Day1":
        minIndexNum = 0
        maxIndexNum = sum_unit
    elif GuiA_cbx3.get() == "Day2":
        minIndexNum = sum_unit
        maxIndexNum = sum_unit * 2
    elif GuiA_cbx3.get() == "Day3":
        minIndexNum = sum_unit * 2
        maxIndexNum = sum_unit * 3
    elif GuiA_cbx3.get() == "Day4":
        minIndexNum = sum_unit * 3
        maxIndexNum = sum_unit * 4
    elif GuiA_cbx3.get() == "Day5":
        minIndexNum = sum_unit * 4
        maxIndexNum = sum_unit * 5
    elif GuiA_cbx3.get() == "Day6":
        minIndexNum = sum_unit * 5
        maxIndexNum = sum_unit * 6
    elif GuiA_cbx3.get() == "Day7":
        minIndexNum = sum_unit * 6
        maxIndexNum = sum_unit * 7
    elif GuiA_cbx3.get() == "Day8":
        minIndexNum = sum_unit * 7
        maxIndexNum = sum_unit * 8
    elif GuiA_cbx3.get() == "Day9":
        minIndexNum = sum_unit * 8
        maxIndexNum = sum_unit * 9
    elif GuiA_cbx3.get() == "Day10":
        minIndexNum = sum_unit * 9
        maxIndexNum = sum_unit * 10
    elif GuiA_cbx3.get() == "Day11":
        minIndexNum = sum_unit * 10
        maxIndexNum = sum_unit * 11
    elif GuiA_cbx3.get() == "Day12":
        minIndexNum = sum_unit * 11
        maxIndexNum = sum_unit * 12
    elif GuiA_cbx3.get() == "Day13":
        minIndexNum = sum_unit * 12
        maxIndexNum = sum_unit * 13
    elif GuiA_cbx3.get() == "Day14":
        minIndexNum = sum_unit * 13
        maxIndexNum = sum_unit * 14
    elif GuiA_cbx3.get() == "Day15":
        minIndexNum = sum_unit * 14
        maxIndexNum = sum_unit * 15
    elif GuiA_cbx3.get() == "Day16":
        minIndexNum = sum_unit * 15
        maxIndexNum = sum_unit * 16
    elif GuiA_cbx3.get() == "Day17":
        minIndexNum = sum_unit * 16
        maxIndexNum = sum_unit * 17
    elif GuiA_cbx3.get() == "Day18":
        minIndexNum = sum_unit * 17
        maxIndexNum = sum_unit * 18
    elif GuiA_cbx3.get() == "Day19":
        minIndexNum = sum_unit * 18
        maxIndexNum = sum_unit * 19
    elif GuiA_cbx3.get() == "Day20":
        minIndexNum = sum_unit * 19
        maxIndexNum = sum_unit * 20
    elif GuiA_cbx3.get() == "Day21":
        minIndexNum = sum_unit * 20
        maxIndexNum = sum_unit * 21
    elif GuiA_cbx3.get() == "Day22":
        minIndexNum = sum_unit * 21
        maxIndexNum = sum_unit * 22
    elif GuiA_cbx3.get() == "Day23":
        minIndexNum = sum_unit * 22
        maxIndexNum = sum_unit * 23
    elif GuiA_cbx3.get() == "Day24":
        minIndexNum = sum_unit * 23
        maxIndexNum = sum_unit * 24
    elif GuiA_cbx3.get() == "Day25":
        minIndexNum = sum_unit * 24
        maxIndexNum = sum_unit * 25
    elif GuiA_cbx3.get() == "Day26":
        minIndexNum = sum_unit * 25
        maxIndexNum = sum_unit * 26
    elif GuiA_cbx3.get() == "Day27":
        minIndexNum = sum_unit * 26
        maxIndexNum = sum_unit * 27
    else:
        minIndexNum = sum_unit * 27
        maxIndexNum = sum_unit * 28 + sum_remain
    indexNum = 0
    dayWords = wordsBankOfCET6[minIndexNum:maxIndexNum]
    sum_dayWords = len(dayWords)
    # --------------乱序 去除熟识(待补充)--------------
    if GuiA_cbx4.get() == "乱序":
        random.shuffle(dayWords)
    if GuiA_cbx4.get() == "字母顺序":
        dayWords.sort(key = lambda x:x[0])
    root1 = tk.Tk()
    root1.title('一网打尽')
    root1.geometry("500x350")
    frame = tk.Frame(root1, bg="lightgreen", highlightthickness=0)
    frame.grid(row=0, column=0, sticky="WENS")
    global frame_l1_ofWord, frame_l2_ofWord, frame_l3_ofWord, frame_l4_ofWord
    frame_l1_ofWord = tk.Label(frame, text="打好地基建高楼", bg="orange", fg="yellow", font=('黑体', 15, 'bold'))
    frame_l1_ofWord.grid(row=0, column=0, columnspan=2, ipady=8, sticky="WE")
    frame_l2_ofWord = tk.Label(frame, text=dayWords[indexNum][0], bg="lightgreen", font=('Arial', 18))
    frame_l2_ofWord.grid(row=1, column=0, columnspan=2, sticky="WES")
    frame_l3_ofWord = tk.Label(frame, text="******** ********", bg="lightgreen", font=('Arial', 8,))
    frame_l3_ofWord.grid(row=2, column=0, columnspan=2, sticky="WEN")
    frame_l4_ofWord = tk.Label(frame, text=dayWords[indexNum][1], pady=10, bg="lightgreen", font=('黑体', 15))
    frame_l4_ofWord.grid(row=3, column=0, columnspan=2, sticky="WEN")
    frame_button1 = tk.Button(frame, height=2, text="上一个", command=button1_ofLast_Clicked)
    root1.bind('<KeyPress-Left>', button1_ofLast_Clicked)  # 将按钮frame_button1与键盘上←绑定
    root1.bind('<KeyPress-A>', button1_ofLast_Clicked)  # 将按钮frame_button1与键盘上1绑定
    frame_button1.grid(row=4, column=0, sticky="WENS")
    frame_button2 = tk.Button(frame, height=2, text="下一个", command=button1_ofNext_Clicked)
    root1.bind('<KeyPress-Right>', button1_ofNext_Clicked)  # 将按钮frame_button1与键盘上→绑定
    root1.bind('<KeyPress-D>', button1_ofNext_Clicked)  # 将按钮frame_button1与键盘上3绑定

    frame_button2.grid(row=4, column=1, sticky="WEN")
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(1, weight=1)
    frame.rowconfigure(2, weight=1)
    frame.rowconfigure(3, weight=1)
    root1.columnconfigure(0, weight=1)
    root1.rowconfigure(0, weight=1)
    root1.mainloop()  # 进入消息循环，也就是显示窗口
    return
# 提取CET6词库
def getWordsOfCET6():
    con = open_wordbank()
    cur = con.cursor()  # 使用游标能够灵活检索
    sql = "SELECT word,paraphrase From CET6"
    cur.execute(sql)
    con.commit()
    WordsOfCET6 = cur.fetchall()
    cur.close()  # 关闭Cursor对象
    con.close()  # 关闭Connnection
    return WordsOfCET6
def getWordsOfCET4():
    con = open_wordbank()
    cur = con.cursor()  # 使用游标能够灵活检索
    sql = "SELECT word,paraphrase From CET4"
    cur.execute(sql)
    con.commit()
    WordsOfCET4 = cur.fetchall()
    cur.close()  # 关闭Cursor对象
    con.close()  # 关闭Connnection
    return WordsOfCET4
def getWordsOfKaoYanCiHui():
    con = open_wordbank()
    cur = con.cursor()  # 使用游标能够灵活检索
    sql = "SELECT word,paraphrase From KaoYanCiHui"
    cur.execute(sql)
    con.commit()
    WordsOfKaoYanCiHui = cur.fetchall()
    cur.close()  # 关闭Cursor对象
    con.close()  # 关闭Connnection
    return WordsOfKaoYanCiHui
# 记单词界面按钮对应的command
def button1_ofNext_Clicked(event=None):
    global indexNum, sum_dayWords
    indexNum += 1
    if indexNum == sum_dayWords:
        indexNum = 0
    num1 = indexNum+1
    textOf_framel1 = "第 %d 个 / 共 %d 个" % (num1, sum_dayWords)
    frame_l1_ofWord.config(text=textOf_framel1)
    frame_l2_ofWord.config(text=dayWords[indexNum][0])
    frame_l4_ofWord.config(text=dayWords[indexNum][1])
    # print(dayWords[indexNum])
    return
def button1_ofLast_Clicked(event=None):
    global indexNum, sum_dayWords
    indexNum -= 1
    if indexNum == -1:
        indexNum = sum_dayWords - 1
    num2 = indexNum+1
    textOf_framel1 = "第 %d 个 / 共 %d 个" % (num2,sum_dayWords)
    frame_l1_ofWord.config(text=textOf_framel1)
    frame_l2_ofWord.config(text=dayWords[indexNum][0])
    frame_l4_ofWord.config(text=dayWords[indexNum][1])
    # print(dayWords[indexNum])
    return

'''-----------------------菜单B-------------------------'''
# 菜单B界面布局Gui_B
def Gui_B():
    global frameB
    frameB = tk.Frame(root, bg="tomato")
    frameB.grid(row=0, column=0, sticky="WENS")
    frameB00 = tk.Frame(frameB, bg="coral", highlightthickness=1)
    frameB00.grid(row=0, column=0, rowspan=2, sticky="NS")
    tk.Button(frameB00, text="open", height=1, width=10, command=GuiB_openFile).grid(row=0, padx=10, pady=6)
    tk.Button(frameB00, text="save", height=1, width=10, command=GuiB_saveFile).grid(row=1, padx=10, pady=6)
    frameB00.rowconfigure(0, weight=1)
    frameB00.rowconfigure(1, weight=1)

    frameB10 = tk.Frame(frameB, bg="coral", highlightthickness=1)
    frameB10.grid(row=2, column=0, sticky="WE")
    GuiB_Button1 = tk.Button(frameB10, text="清空", height=1, width=10, command=clerGuiBText)
    GuiB_Button1.grid(row=0, padx=10, pady=15)
    global GuiB_Button2
    GuiB_Button2 = tk.Button(frameB10, text="提取", height=1, width=10, command=GuiB_Button2_Clicked)
    GuiB_Button2.grid(row=1, padx=10, pady=15)

    frameB01 = tk.Frame(frameB, bg="antiquewhite", highlightthickness=0)
    frameB01.grid(row=0, column=1, rowspan=3, sticky="NSWE")
    tk.Label(frameB01, text="文本显示框：", height=1).grid(row=0, padx=5, pady=2, sticky="W")

    global GuiB_Text
    GuiB_Text = tk.Text(frameB01, bg="beige")
    GuiB_Text.grid(row=1, padx=5, pady=5, sticky="NSWE")
    frameB01.rowconfigure(1, weight=1)
    frameB01.columnconfigure(0, weight=1)
    global CanvasB30, CanvasB30_L2
    CanvasB30 = tk.Canvas(frameB, bg="sandybrown", highlightthickness=0)
    CanvasB30.grid(row=3, column=0, columnspan=2, sticky="WE")
    CanvasB30_L1 = tk.Label(CanvasB30, text="B站：@丰收奇迹", bg="sandybrown", height=1)
    CanvasB30_L1.grid(row=0, column=0, padx=10, pady=5, sticky="W")
    CanvasB30_time = time.strftime("%Y-%m-%d %X", time.localtime())

    CanvasB30_L2 = tk.Label(CanvasB30, text=CanvasB30_time, bg="sandybrown", height=1)
    CanvasB30_L2.grid(row=0, column=1, padx=10, pady=5, sticky="E")
    try:
        t1 = threading.Timer(1, gettime)
        t1.start()
    except:
        pass
    CanvasB30.columnconfigure(0, weight=1)
    frameB.rowconfigure(0, weight=1)
    frameB.columnconfigure(1, weight=1)
    return
def gettime():
    try:
        CanvasB30_time = time.strftime("%Y-%m-%d %X", time.localtime())
        CanvasB30_L2.config(text=CanvasB30_time)
        t1 = threading.Timer(1, gettime)
        t1.start()
    except:
        return
# B界面按钮对应的command
def GuiB_openFile():
    r = askopenfilename(title='打开文件', filetypes=[('All files', '.txt')])
    if r == '':
        return
    try:
        f = open(r, 'r', encoding="gbk")
        text = f.read()
        f.close()
    except:
        f = open(r, 'r', encoding="utf-8")
        text = f.read()
        f.close()
    GuiB_Text.delete(1.0,'end')
    GuiB_Text.insert(1.0, text)
def GuiB_saveFile():
    Path = os.getcwd()
    r = asksaveasfilename(title='保存文件', initialdir=Path + r'\English_txt',
                          filetypes=[('文本文件', '.txt')])
    if r == '':
        return
    if r.endswith('.txt'):    # 判断 r 是否以 txt 结尾
        pass
    else:
        r += '.txt'
    f = open(r, 'w', encoding="gbk")
    text = GuiB_Text.get(1.0, "end")
    f.write(text)
    f.close()
def clerGuiBText():
    GuiB_Text.delete(1.0,'end')
    return
def GuiB_wordExtract():
    txt = GuiB_Text.get(1.0, "end")
    result = countFile(txt, makeVaryWordsDict())
    strText = ""
    wordExtract_dict1 = {}      # {'the': 'art. 这；那; adv. 更加 THEabbr. Technical Help to Exporters 出口商的技术协助',
    wordExtract_dict2 = {}      # 储存词频 {'the':7,
    wordExtract_str = ''
    if result != None and result != {}:
        lst = list(result.items())    # 以列表返回可遍历的（键，值）元组数组
        con = open_wordbank()
        cur = con.cursor()  # 使用游标能够灵活检索
        for x in lst:
            m = 0
            try:        # 在数据库中查询单词将查询到的单词 返回字典 {单词：释义} {单词：词频}
                sql = "SELECT word,paraphrase From words where word = '%s'" % (x[0])
                cur.execute(sql)
                con.commit()
                res = cur.fetchall()
                wordExtract_dict1[res[0][0]] = res[0][1]
                wordExtract_dict2[res[0][0]] = str(x[1])
            except:     # 为查询到执行下一步操作
                m = 1
                pass
            if m == 1:
                n1 = 0
                try:    # 将首字母变为大写后再查询一次
                    word_1 = str(x[0])
                    word_1 = word_1.capitalize()
                    sql = "SELECT word,paraphrase From words where word = '%s'" % (word_1)
                    cur.execute(sql)
                    con.commit()
                    res = cur.fetchall()
                    wordExtract_dict1[res[0][0]] = res[0][1]
                    wordExtract_dict2[res[0][0]] = str(x[1])
                except:
                    # try:
                    #     word_2 = str(x[0])
                    #     word_2 = word_2.rstrip('s')
                    #     sql = "SELECT word,paraphrase From words where word = '%s'" % (word_2)
                    #     cur.execute(sql)
                    #     con.commit()
                    #     res = cur.fetchall()
                    #     wordExtract_dict1[res[0][0]] = res[0][1]
                    #     wordExtract_dict2[res[0][0]] = str(x[1])
                    # except:
                    #     print('ddd')
                    n1 = 1
                if n1 == 1:     # 将最终为能查询到的单词收集
                    wordExtract_str = wordExtract_str + x[0] + '\n'
        cur.close()  # 关闭Cursor对象
        con.close()  # 关闭Connnection
        # 将单词收集起来，排除 之前 出现过 的单词之后 追加到文件后面
        Path = os.getcwd()
        f = open(Path + r"\dates\Z09wordSet.txt", "r",encoding="UTF-8")
        inheretxt = f.read()
        f.close()
        for i,j in wordExtract_dict1.items():
            f = open(Path + r"\dates\Z09wordSet.txt", "a",encoding="UTF-8")
            if i not in inheretxt:
                f.write(i+'\t'+j+'\n')
            f.close()
        # 将词频转换为便于输入GuiB1_Text1的字符串
        for i,j in wordExtract_dict2.items():
            strText += i + '\t' + j + '\n'
    return strText, wordExtract_str
# 当关闭GuiB_Button2子窗口时调用函数，用于提取按钮点击后被禁用，关闭之窗口后重新启用
def rootB1_destroy():
    rootB1.destroy()
    GuiB_Button2.config(state=tk.NORMAL)
    return
# 菜单B界面的GuiB_Button2子窗口布局Gui_B_1
def GuiB_Button2_Clicked():
    GuiB_Button2.config(state=tk.DISABLED)
    global rootB1
    # 设置子窗口对象，并在启动子窗口时锁定主窗口root
    rootB1 = tk.Toplevel(root)
    rootB1.title('统计结果')
    rootB1.geometry("450x300")
    rootB1.minsize(300, 200)
    rootB1.maxsize(1366, 768)
    rootB1.grab_set()           # 锁定主窗口
    word_text = GuiB_wordExtract()      # 词频以及为查询到的字符
    words_frequency = re.split("\n", word_text[0])
    num1 = 0    # 统计到的单词个数
    num2 = 0    # 记录词频总数
    for i in words_frequency:
        if i == "":
            continue
        num1 += 1
        word_frequency = re.split("\t", i)
        num2 += int(word_frequency[1])
    Label1_text = "词频统计：%d %d" % (num1,num2)
    tk.Label(rootB1, text=Label1_text, height=1).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="W")
    words_else = re.split("\n", word_text[1])       # 未查询到的单词
    num3 = 0
    for i in words_else:
        if i == "":
            continue
        num3 += 1
    Label2_text = "未查询到：%d" % (num3)
    tk.Label(rootB1, text=Label2_text, height=1).grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky="W")
    GuiB1_button1 = tk.Button(rootB1, text="保存", height=1, width=10,command=GuiB1_saveText1)
    GuiB1_button1.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    GuiB1_button2 = tk.Button(rootB1, text="保存", height=1, width=10,command=GuiB1_saveText2)
    GuiB1_button2.grid(row=2, column=2, columnspan=2, padx=5, pady=5)

    global GuiB1_text1, GuiB1_text2    # 便于后续提取文本框的内容
    GuiB1_text1 = tk.Text(rootB1)
    GuiB1_text1.grid(row=1, column=0, padx=5, pady=5, sticky="NSWE")
    GuiB1_text1.insert(tk.END, "单词\t出现次数\n")

    GuiB1_text1.insert(tk.END, word_text[0])
    GuiB1_text1.config(state=tk.DISABLED)

    GuiB1_text2 = tk.Text(rootB1)
    GuiB1_text2.grid(row=1, column=2, padx=5, pady=5, sticky="NSWE")
    GuiB1_text2.insert(tk.END, word_text[1])

    GuiB1_scrollbar1 = tk.Scrollbar(rootB1)
    GuiB1_scrollbar1.grid(row=1, column=1, padx=0, pady=5, sticky="NS")
    GuiB1_scrollbar2 = tk.Scrollbar(rootB1)
    GuiB1_scrollbar2.grid(row=1, column=3, padx=0, pady=5, sticky="NS")


    GuiB1_text1['yscrollcommand'] = GuiB1_scrollbar1.set        #链接 文本 和 滚动条
    GuiB1_scrollbar1['command'] = GuiB1_text1.yview
    GuiB1_text2['yscrollcommand'] = GuiB1_scrollbar2.set
    GuiB1_scrollbar2['command'] = GuiB1_text2.yview

    rootB1.rowconfigure(1, weight=1)
    rootB1.columnconfigure(0, weight=1)
    rootB1.columnconfigure(2, weight=1)

    rootB1.protocol('WM_DELETE_WINDOW', rootB1_destroy)
    rootB1.mainloop()
    return
# Gui_B_1之 GuiA1_text1 内容保存
def GuiB1_saveText1():
    txt = GuiB1_text1.get(2.0,"end")
    # 下面保存提取的单词词频到数据库，wordFrequency.txt记录保存过的数据防止重复保存'''
    Path = os.getcwd()
    f = open(Path + r"\dates\Z04.wordFrequency.txt", "r", encoding="UTF-8")
    inheretxt = f.read()
    f.close()
    if txt not in inheretxt:    #防止多次重复保存
        firstTime = time.strftime("%Y-%m-%d", time.localtime())      # 记录当前日期
        f = open(Path + r"\dates\Z04.wordFrequency.txt", "a", encoding="UTF-8")
        f.write(txt)
        f.close()
        # 下面将词频记入数据库wordsFromNow，并每次在单词后累加
        con = open_wordbank()
        cur = con.cursor()
        wordlist = re.split("\n", txt)       # 以元素为元组的列表储存词频
        for i in wordlist:
            if i == "":
                continue
            word_frequency = re.split("\t", i)
            word = word_frequency[0]
            frequency = int(word_frequency[1])
            sql = "SELECT paraphrase From words where word = '%s'" % (word)     # 提取释义
            cur.execute(sql)
            con.commit()
            res = cur.fetchone()
            paraphrase = res[0]
            try:  # 插入已有会出错（没有则加入）
                cur.execute("INSERT INTO wordFromNow VALUES(?,?,?,?,?)",
                            (word, frequency, firstTime, paraphrase, 0))
                con.commit()  # 提交，否者不会实现插入更新操作
            except:     # 如果表wordFromNow中已有则累加词频
                cur.execute("SELECT frequency From wordFromNow where word = '%s'" % (word))
                res2 = cur.fetchone()
                prefrequency = int(res2[0])     # 存储原来累次词频
                frequency += prefrequency
                cur.execute("UPDATE wordFromNow SET frequency = '%d' WHERE word = '%s'" % (frequency, word))
                con.commit()  # 提交，否者不会实现更新操作
        cur.close()
        con.close()
    else:
        messagebox.showwarning("警告", '无内容或已经保存，勿重复操作')
    return
# Gui_A_1之 GuiA1_text1 内容保存
def GuiB1_saveText2():
    Path = os.getcwd()
    f = open(Path + r"\dates\Z07GuiB1_Text2.txt", "r",encoding="UTF-8")
    inheretxt2 = f.read()
    f.close()
    txt = GuiB1_text2.get(1.0, "end")
    '''下面保存为查询到的单词到Z07GuiB1_Text2.txt'''
    if txt not in inheretxt2:    # 防止反复保存
        f = open(Path + r"\dates\Z07GuiB1_Text2.txt", "a", encoding="UTF-8")
        f.write(txt)
        f.close()
    else:
        messagebox.showwarning("警告", '无内容或已经保存，勿重复操作')


'''-----------------------菜单C-------------------------'''
def Gui_C():
    global frameC       # frameA便于后续清空A界面
    frameC = tk.Frame(root, bg="sandybrown")
    frameC.grid(row=0, column=0, sticky="WENS")
    frameC00_Button01 = tk.Button(frameC, text="单词本-All", height=1, width=20, command=frameC00_Button01_Clicked)
    frameC00_Button01.grid(row=0, column=0)
    frameC01_Button02 = tk.Button(frameC, text="单词本-不认识", height=1, width=20, command=frameC01_Button02_Clicked)
    frameC01_Button02.grid(row=0, column=1)
    frameC02_Button03 = tk.Button(frameC, text="单词本-认识", height=1, width=20, command=frameC02_Button03_Clicked)
    frameC02_Button03.grid(row=0, column=2)
    frameC10_Button04 = tk.Button(frameC, text="过滤-单词本-All", height=1, width=20, command=frameC10_Button04_Clicked)
    frameC10_Button04.grid(row=1, column=0)
    frameC11_Button05 = tk.Button(frameC, text="过滤-单词本-不认识", height=1, width=20, command=frameC11_Button05_Clicked)
    frameC11_Button05.grid(row=1, column=1)
    frameC12_Button06 = tk.Button(frameC, text="过滤-单词本-认识", height=1, width=20, command=frameC12_Button06_Clicked)
    frameC12_Button06.grid(row=1, column=2)
    frameC20_Button07 = tk.Button(frameC, text="熟词本", height=1, width=20, command=frameC20_Button07_Clicked)
    frameC20_Button07.grid(row=2, column=0)
    frameC21_Button08 = tk.Button(frameC, text="清空熟词", height=1, width=20, command=frameC21_Button08_Clicked)
    frameC21_Button08.grid(row=2, column=1)
    frameC22_Button09 = tk.Button(frameC, text="生词本", height=1, width=20, command=frameC22_Button09_Clicked)
    frameC22_Button09.grid(row=2, column=2)
    frameC30_Button10 = tk.Button(frameC, text="词频总计", height=1, width=20, command=frameC30_Button10_Clicked)
    frameC30_Button10.grid(row=3, column=0)
    frameC31_Button11 = tk.Button(frameC, text="扩增词库", height=1, width=20, command=frameC31_Button11_Clicked)
    frameC31_Button11.grid(row=3, column=1)
    frameC32_Button12 = tk.Button(frameC, text="单词本重置", height=1, width=20, command=frameC32_Button12_Clicked)
    frameC32_Button12.grid(row=3, column=2)

    frameC.rowconfigure(0, weight=1)
    frameC.rowconfigure(1, weight=1)
    frameC.rowconfigure(2, weight=1)
    frameC.rowconfigure(3, weight=1)
    frameC.columnconfigure(0, weight=1)            # 窗口对象第一列里面的东西随着窗口自动上下填满
    frameC.columnconfigure(1, weight=1)
    frameC.columnconfigure(2, weight=1)
# C界面按钮对应的command
# -----------------------Button01-----------------------
def frameC00_Button01_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word,firstTime,paraphrase From wordFromNow')
    newWord_list = cur.fetchall()
    newWord_num = len(newWord_list)
    newWord_num = "共：%d 个\n" % (newWord_num)
    newWord_str = ""
    for i in newWord_list:
        newWord_str += i[1] + "\t\t" + i[0] + "\t\t" + i[2] + "\n"
    root1 = tk.Toplevel(root)
    root1.title('单词本-All')
    root1.geometry("600x400")
    root1.grab_set()
    text = tk.Text(root1, font=('Arial', 12))
    text.grid(row=0, column=0, padx=1, pady=1, sticky="NSWE")
    scrollbar1 = tk.Scrollbar(root1)
    scrollbar1.grid(row=0, column=1, padx=0, pady=5, sticky="NS")
    text['yscrollcommand'] = scrollbar1.set  # 链接 文本 和 滚动条
    scrollbar1['command'] = text.yview
    root1.rowconfigure(0, weight=1)
    root1.columnconfigure(0, weight=1)
    text.insert(tk.END, newWord_num)
    text.insert(tk.END, newWord_str)
    cur.close()
    con.close()
    return
# -----------------------Button02-----------------------
def frameC01_Button02_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word,firstTime,paraphrase From wordFromNow where yesOrNo=0')
    newWord_list = cur.fetchall()
    newWord_num = len(newWord_list)
    newWord_num = "共：%d 个\n" % (newWord_num)
    newWord_str = ""
    for i in newWord_list:
        newWord_str += i[1] + "\t\t" + i[0] + "\t\t" + i[2] + "\n"
    root1 = tk.Toplevel(root)
    root1.title('单词本-不认识')
    root1.geometry("600x400")
    root1.grab_set()
    text = tk.Text(root1, font=('Arial', 12))
    text.grid(row=0, column=0, padx=5, pady=5, sticky="NSWE")
    scrollbar1 = tk.Scrollbar(root1)
    scrollbar1.grid(row=0, column=1, padx=0, pady=5, sticky="NS")
    text['yscrollcommand'] = scrollbar1.set  # 链接 文本 和 滚动条
    scrollbar1['command'] = text.yview
    root1.rowconfigure(0, weight=1)
    root1.columnconfigure(0, weight=1)
    text.insert(tk.END, newWord_num)
    text.insert(tk.END, newWord_str)
    cur.close()
    con.close()
    return
# -----------------------Button03-----------------------
def frameC02_Button03_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word,firstTime,paraphrase From wordFromNow where yesOrNo=1')
    newWord_list = cur.fetchall()
    newWord_num = len(newWord_list)
    newWord_num = "共：%d 个\n" % (newWord_num)
    newWord_str = ""
    for i in newWord_list:
        newWord_str += i[1] + "\t\t" + i[0] + "\t\t" + i[2] + "\n"
    root1 = tk.Toplevel(root)
    root1.title('单词本-All-认识')
    root1.geometry("600x400")
    root1.grab_set()
    text = tk.Text(root1, font=('Arial', 12))
    text.grid(row=0, column=0, padx=5, pady=5, sticky="NSWE")
    scrollbar1 = tk.Scrollbar(root1)
    scrollbar1.grid(row=0, column=1, padx=0, pady=5, sticky="NS")
    text['yscrollcommand'] = scrollbar1.set  # 链接 文本 和 滚动条
    scrollbar1['command'] = text.yview
    root1.rowconfigure(0, weight=1)
    root1.columnconfigure(0, weight=1)
    text.insert(tk.END, newWord_num)
    text.insert(tk.END, newWord_str)
    cur.close()
    con.close()
    return
# -----------------------Button04-----------------------
def frameC10_Button04_Clicked():
    global newWord_list1, indexNum1, sum_words1
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word,paraphrase From wordFromNow')
    newWord_list1 = cur.fetchall()   # [('scientist', 'n. 科学家'),
    if newWord_list1 == []:
        messagebox.showerror("出错", '请查看《单词本-All》有无内容')
        return
    sum_words1 = len(newWord_list1)    # sum_words1 单词总数
    global rootC1
    rootC1 = tk.Toplevel(root)
    rootC1.title('过滤-单词本-All')
    rootC1.geometry("500x350")
    rootC1.grab_set()
    frame = tk.Frame(rootC1, bg="lightgreen", highlightthickness=0)
    frame.grid(row=0, column=0, sticky="WENS")

    global frame1_l2_ofnewWord1, frame1_E1_ofnewWord1
    frame1 = tk.Frame(frame, bg="red")
    frame1.grid(row=0, column=0, sticky="WES")
    frame1_l1_ofnewWord1 = tk.Label(frame1, height=2, text="第", bg="red", fg="yellow", font=('黑体', 15, 'bold'))
    frame1_l1_ofnewWord1.grid(row=0, column=0, sticky="E")
    text_offrame1_l2 = "个 / 共 %d 个" % (sum_words1)
    frame1_l2_ofnewWord1 = tk.Label(frame1, text=text_offrame1_l2, bg="red", fg="yellow", font=('黑体', 15, 'bold'))
    frame1_l2_ofnewWord1.grid(row=0, column=2, sticky="W")
    frame1_E1_ofnewWord1 = tk.Entry(frame1, width=4, borderwidth=0, justify=tk.CENTER, bg="red",
                                    font=('黑体', 15, 'bold'))
    frame1_E1_ofnewWord1.grid(row=0, column=1)
    # 读取上次frame1_E1_ofnewWord1显示的数字
    con2 = open_jidanci()
    cur2 = con2.cursor()
    cur2.execute("SELECT num From GuiC_Entry WHERE name='E1_ofnewWord1'")    # 读取上次frame1_E1_ofnewWord1显示的数字
    con2.commit()
    indexNum1 = cur2.fetchone()[0] - 1
    num_E1 = str(indexNum1 + 1)
    if int(num_E1) <= sum_words1:
        frame1_E1_ofnewWord1.insert(0, num_E1)
    else:
        indexNum1 = 0
        frame1_E1_ofnewWord1.insert(0, '1')
    frame1_B1_ofnewWord1 = tk.Button(frame1, height=1, width=5, bg="red", text="确定",
                                     command=frame1_B1_ofnewWord1_Clicked)
    frame1_B1_ofnewWord1.grid(row=0, column=3)
    rootC1.bind('<KeyPress-Return>', frame1_B1_ofnewWord1_Clicked)  # 将按钮"确定"与键盘上回车绑定
    frame1.columnconfigure(0, weight=1)
    frame1.columnconfigure(2, weight=1)

    global frame2_E1_ofnewWord1, frame2_T1_ofnewWord1
    frame2 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame2.grid(row=1, column=0, sticky="WENS")
    frame2_B1_ofnewWord1 = tk.Button(frame2, height=2, bg="lightgreen", borderwidth=0, relief="groove",
                                     text="<<", command=frame2_B1_ofnewWord1_Clicked)
    frame2_B1_ofnewWord1.grid(row=0, column=0, rowspan=2)
    frame2_B2_ofnewWord1 = tk.Button(frame2, height=2, bg="lightgreen", borderwidth=0, relief="groove",
                                     text=">>", command=frame2_B2_ofnewWord1_Clicked)
    frame2_B2_ofnewWord1.grid(row=0, column=2, rowspan=2)
    # 显示单词：
    word_L1 = newWord_list1[indexNum1][0]
    frame2_E1_ofnewWord1 = tk.Entry(frame2,  bg="lightgreen", justify="center", font=('黑体', 20))
    frame2_E1_ofnewWord1.grid(row=0, column=1, ipady=10, pady=45)
    frame2_E1_ofnewWord1.insert(0,word_L1)
    # 显示释义：
    paraphrase_E1 = newWord_list1[indexNum1][1]
    frame2_T1_ofnewWord1 = tk.Text(frame2, height=5, borderwidth=0, bg="lightgreen", font=('黑体', 15))
    frame2_T1_ofnewWord1.grid(row=1, column=1, ipady=15)
    frame2_T1_ofnewWord1.tag_configure("center",justify='center')
    frame2_T1_ofnewWord1.insert(tk.END, paraphrase_E1)
    frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')

    frame2.rowconfigure(0, weight=1)
    frame2.rowconfigure(1, weight=1)
    frame2.columnconfigure(1, weight=1)

    frame3 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame3.grid(row=2, column=0, sticky="WE")
    frame3_B1_ofnewWord1 = tk.Button(frame3, height=2, relief="groove", bg="lightgreen",
                                     text="上一个", command=frame2_B1_ofnewWord1_Clicked)
    frame3_B1_ofnewWord1.grid(row=0, column=0, sticky="WE")
    rootC1.bind('<KeyPress-Left>', frame2_B1_ofnewWord1_Clicked)  # 将按钮"上一个"与键盘上←绑定
    rootC1.bind('<KeyPress-A>', frame2_B1_ofnewWord1_Clicked)  # 将按钮"上一个"与键盘上1绑定
    frame3_B2_ofnewWord1 = tk.Button(frame3, height=2, relief="groove", bg="lightgreen",
                                     text="下一个", command=frame2_B2_ofnewWord1_Clicked)
    frame3_B2_ofnewWord1.grid(row=0, column=1, sticky="WE")
    rootC1.bind('<KeyPress-Right>', frame2_B2_ofnewWord1_Clicked)  # 将按钮"下一个"与键盘上→绑定
    rootC1.bind('<KeyPress-D>', frame2_B2_ofnewWord1_Clicked)  # 将按钮"下一个"与键盘上3绑定
    frame3.columnconfigure(0, weight=1)
    frame3.columnconfigure(1, weight=1)

    frame4 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame4.grid(row=3, column=0, sticky="WE")
    global wordHide1, paraphraseHide1, yesOrNo1, yesOrNo2
    wordHide1 = tk.IntVar()
    paraphraseHide1 = tk.IntVar()
    yesOrNo1 = tk.IntVar()
    yesOrNo2 = tk.IntVar()
    # 设置单选框
    frame4_C1_ofnewWord1 = tk.Checkbutton(frame4, bg="lightgreen", text="隐藏单词", variable=wordHide1, onvalue=1,
                                          offvalue=0, command=frame4_C1_ofnewWord1_Clicked)
    frame4_C1_ofnewWord1.grid(row=0, column=0)
    frame4_C2_ofnewWord1 = tk.Checkbutton(frame4, bg="lightgreen",  text="隐藏释义", variable=paraphraseHide1,
                                          onvalue=1,offvalue=0, command=frame4_C2_ofnewWord1_Clicked)
    frame4_C2_ofnewWord1.grid(row=0, column=1)
    # 设置复选框
    frame4_C3_ofnewWord1 = tk.Checkbutton(frame4, bg="lightgreen",  text="喝醉都认识", variable=yesOrNo1,
                                          onvalue=1,offvalue=0, command=frame4_C3_ofnewWord1_Clicked)
    frame4_C3_ofnewWord1.grid(row=0, column=2)
    cur.execute("SELECT word From familiarWords")
    global familiarWords
    familiarWords = []      # 用于存储喝醉酒都认识的单词
    for i in cur.fetchall():
        familiarWords.append(i[0])
    if word_L1 in familiarWords:
        yesOrNo1.set(1)     # 设置复选框3的状态
    else:
        yesOrNo1.set(0)
    frame4_C4_ofnewWord1 = tk.Checkbutton(frame4, bg="lightgreen",  text="认识", variable=yesOrNo2,
                                          onvalue=1,offvalue=0, command=frame4_C4_ofnewWord1_Clicked)
    frame4_C4_ofnewWord1.grid(row=0, column=3)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (word_L1))
    yesOrNo2.set(cur.fetchone()[0])         # 设置复选框4的状态

    frame4.columnconfigure(0, weight=1)
    frame4.columnconfigure(1, weight=1)
    frame4.columnconfigure(2, weight=1)
    frame4.columnconfigure(3, weight=1)

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    rootC1.columnconfigure(0, weight=1)
    rootC1.rowconfigure(0, weight=1)
    rootC1.protocol('WM_DELETE_WINDOW', rootC1_destroy)
    rootC1.mainloop()  # 进入消息循环，也就是显示窗口

    cur.close()
    con.close()
    cur2.close()
    con2.close()
    return
# 按键”确定“
def frame1_B1_ofnewWord1_Clicked(event=None):
    global indexNum1
    try:
        indexNum1 = int(frame1_E1_ofnewWord1.get())
    except:
        messagebox.showwarning("警告", '请输入数字')
        return
    if indexNum1 < 1 or indexNum1 > sum_words1:
        messagebox.showwarning("警告", '请注意数字范围')
        return
    indexNum1 = indexNum1 - 1
    frame2_E1_ofnewWord1.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord1.insert(0, newWord_list1[indexNum1][0])
    frame2_T1_ofnewWord1.delete(1.0, tk.END)  # 清空原来释义
    hide2 = paraphraseHide1.get()
    if hide2 == 1:
        frame2_T1_ofnewWord1.delete(1.0, tk.END)
        frame2_T1_ofnewWord1.insert(tk.END, "********")
        frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord1.delete(1.0, tk.END)
        frame2_T1_ofnewWord1.insert(tk.END, newWord_list1[indexNum1][1])
        frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')
    return
# 按键"<<"
def frame2_B1_ofnewWord1_Clicked(event=None):
    con = open_wordbank()
    cur = con.cursor()
    global indexNum1
    indexNum1 -= 1
    if indexNum1 == -1:
        indexNum1 = sum_words1 - 1       # 如果减到-1，则跳到最后一个单词
    num_E1 = str(indexNum1 + 1)
    frame1_E1_ofnewWord1.delete(0, tk.END)  # 清空原来数字
    frame1_E1_ofnewWord1.insert(0, num_E1)
    new_word = newWord_list1[indexNum1][0]
    if new_word in familiarWords:
        yesOrNo1.set(1)     # 设置复选框3的状态
    else:
        yesOrNo1.set(0)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (new_word))
    yesOrNo2.set(cur.fetchone()[0])         # 设置复选框4的状态
    frame2_E1_ofnewWord1.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord1.insert(0, new_word)       # 填入新单词
    frame2_T1_ofnewWord1.delete(1.0, tk.END)    # 清空原来释义
    hide2 = paraphraseHide1.get()
    if hide2 == 1:
        frame2_T1_ofnewWord1.delete(1.0, tk.END)
        frame2_T1_ofnewWord1.insert(tk.END, "********")
        frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord1.delete(1.0, tk.END)
        frame2_T1_ofnewWord1.insert(tk.END, newWord_list1[indexNum1][1])
        frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')
    cur.close()
    con.close()
    return
# 按键">>"
def frame2_B2_ofnewWord1_Clicked(event=None):
    con = open_wordbank()
    cur = con.cursor()
    global indexNum1
    indexNum1 += 1
    if indexNum1 == sum_words1:
        indexNum1 = 0        # 如果加到最大，则跳到第一个单词
    num_E1 = str(indexNum1 + 1)
    frame1_E1_ofnewWord1.delete(0, tk.END)  # 清空原来数字
    frame1_E1_ofnewWord1.insert(0, num_E1)
    new_word = newWord_list1[indexNum1][0]
    if new_word in familiarWords:
        yesOrNo1.set(1)     # 设置复选框3的状态
    else:
        yesOrNo1.set(0)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (new_word))
    yesOrNo2.set(cur.fetchone()[0])         # 设置复选框4的状态
    frame2_E1_ofnewWord1.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord1.insert(0, new_word)    # 填入新的单词
    frame2_T1_ofnewWord1.delete(1.0, tk.END)  # 清空原来释义
    hide2 = paraphraseHide1.get()
    if hide2 == 1:
        frame2_T1_ofnewWord1.delete(1.0, tk.END)
        frame2_T1_ofnewWord1.insert(tk.END, "********")
        frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord1.delete(1.0, tk.END)
        frame2_T1_ofnewWord1.insert(tk.END, newWord_list1[indexNum1][1])
        frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')
    cur.close()
    con.close()
    return
# 复选框对应函数
def frame4_C1_ofnewWord1_Clicked():
    hide1 = wordHide1.get()
    if hide1 == 1:
        frame2_E1_ofnewWord1.config(show="*")
    else:
        frame2_E1_ofnewWord1.config(show="")
    return
def frame4_C2_ofnewWord1_Clicked():
    hide2 = paraphraseHide1.get()
    if hide2 == 1:
        frame2_T1_ofnewWord1.delete(1.0, tk.END)
        frame2_T1_ofnewWord1.insert(tk.END, "********")
        frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord1.delete(1.0, tk.END)
        frame2_T1_ofnewWord1.insert(tk.END, newWord_list1[indexNum1][1])
        frame2_T1_ofnewWord1.tag_add('center', '1.0', 'end')
    return
def frame4_C3_ofnewWord1_Clicked():
    word = newWord_list1[indexNum1][0]
    con = open_wordbank()
    cur = con.cursor()
    num = yesOrNo1.get()
    if num == 1:
        try:
            cur.execute("INSERT INTO familiarWords VALUES(?)",(word,))
            con.commit()
        except Exception as e:
            pass
    else:
        try:
            cur.execute("DELETE FROM familiarWords WHERE word='%s'"%(word))
            con.commit()
        except:
            pass
    cur.close()
    con.close()
def frame4_C4_ofnewWord1_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    num = yesOrNo2.get()
    word = newWord_list1[indexNum1][0]
    sql = "UPDATE GuiC_Entry SET num=%d  WHERE name = 'E1_ofnewWord1'" % (num)
    cur.execute("UPDATE wordFromNow SET yesOrNo=%d  WHERE word = '%s'" % (num, word))
    con.commit()
    cur.close()
    con.close()
    return
# rootC1关闭时调用
def rootC1_destroy():
    try:
        indexNum1 = int(frame1_E1_ofnewWord1.get())
    except:
        messagebox.showwarning("警告", '请输入数字')
        return
    if indexNum1 < 1 or indexNum1 > sum_words1:
        messagebox.showwarning("警告", '请注意数字范围')
        return
    con = open_jidanci()
    cur = con.cursor()
    num = int(indexNum1)
    # cur.execute("INSERT INTO GuiC_Entry VALUES(?,?)", ("E1_ofnewWord1", num))
    sql = "UPDATE GuiC_Entry SET num=%d  WHERE name = 'E1_ofnewWord1'" % (num)
    cur.execute(sql)
    con.commit()
    rootC1.destroy()
    cur.close()
    con.close()
    return
# -----------------------Button05-----------------------
def frameC11_Button05_Clicked():
    global newWord_list2, indexNum2, sum_words2
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word,paraphrase From wordFromNow where yesOrNo=0')
    newWord_list2 = cur.fetchall()  # [('scientist', 'n. 科学家'),
    if newWord_list2 == []:
        messagebox.showerror("出错", '请查看《单词本-不认识》有无内容')
        return
    sum_words2 = len(newWord_list2)  # sum_words2 单词总数
    global rootC2
    rootC2 = tk.Toplevel(root)
    rootC2.title('过滤-单词本-不认识')
    rootC2.geometry("500x350")
    rootC2.grab_set()
    frame = tk.Frame(rootC2, bg="lightgreen", highlightthickness=0)
    frame.grid(row=0, column=0, sticky="WENS")

    global frame1_E1_ofnewWord2
    frame1 = tk.Frame(frame, bg="red")
    frame1.grid(row=0, column=0, sticky="WES")
    frame1_l1_ofnewWord2 = tk.Label(frame1, height=2, text="第", bg="red", fg="yellow", font=('黑体', 15, 'bold'))
    frame1_l1_ofnewWord2.grid(row=0, column=0, sticky="E")
    text_offrame1_l2 = "个 / 共 %d 个" % (sum_words2)
    frame1_l2_ofnewWord2 = tk.Label(frame1, text=text_offrame1_l2, bg="red", fg="yellow", font=('黑体', 15, 'bold'))
    frame1_l2_ofnewWord2.grid(row=0, column=2, sticky="W")
    frame1_E1_ofnewWord2 = tk.Entry(frame1, width=4, borderwidth=0, justify=tk.CENTER, bg="red",
                                    font=('黑体', 15, 'bold'))
    frame1_E1_ofnewWord2.grid(row=0, column=1)
    # 读取上次frame1_E1_ofnewWord2显示的数字
    con2 = open_jidanci()
    cur2 = con2.cursor()
    cur2.execute("SELECT num From GuiC_Entry WHERE name='E1_ofnewWord2'")  # 读取上次frame1_E1_ofnewWord2显示的数字
    con2.commit()
    indexNum2 = cur2.fetchone()[0] - 1
    num_E1 = str(indexNum2 + 1)
    if int(num_E1) <= sum_words2:
        frame1_E1_ofnewWord2.insert(0, num_E1)
    else:
        indexNum2 = 0
        frame1_E1_ofnewWord2.insert(0, '1')
    frame1_B1_ofnewWord2 = tk.Button(frame1, height=1, width=5, bg="red", text="确定",
                                     command=frame1_B1_ofnewWord2_Clicked)
    frame1_B1_ofnewWord2.grid(row=0, column=3)
    rootC2.bind('<KeyPress-Return>', frame1_B1_ofnewWord2_Clicked)  # 将按钮"确定"与键盘上回车绑定
    frame1.columnconfigure(0, weight=1)
    frame1.columnconfigure(2, weight=1)

    global frame2_E1_ofnewWord2, frame2_T1_ofnewWord2
    frame2 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame2.grid(row=1, column=0, sticky="WENS")
    frame2_B1_ofnewWord2 = tk.Button(frame2, height=2, bg="lightgreen", borderwidth=0, relief="groove",
                                     text="<<", command=frame2_B1_ofnewWord2_Clicked)
    frame2_B1_ofnewWord2.grid(row=0, column=0, rowspan=2)
    frame2_B2_ofnewWord2 = tk.Button(frame2, height=2, bg="lightgreen", borderwidth=0, relief="groove",
                                     text=">>", command=frame2_B2_ofnewWord2_Clicked)
    frame2_B2_ofnewWord2.grid(row=0, column=2, rowspan=2)
    # 显示单词：
    word_L1 = newWord_list2[indexNum2][0]
    frame2_E1_ofnewWord2 = tk.Entry(frame2, bg="lightgreen", justify="center", font=('黑体', 20))
    frame2_E1_ofnewWord2.grid(row=0, column=1, ipady=10, pady=45)
    frame2_E1_ofnewWord2.insert(0, word_L1)
    # 显示释义：
    paraphrase_E1 = newWord_list2[indexNum2][1]
    frame2_T1_ofnewWord2 = tk.Text(frame2, height=5, borderwidth=0, bg="lightgreen", font=('黑体', 15))
    frame2_T1_ofnewWord2.grid(row=1, column=1, ipady=15)
    frame2_T1_ofnewWord2.tag_configure("center", justify='center')
    frame2_T1_ofnewWord2.insert(tk.END, paraphrase_E1)
    frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')

    frame2.rowconfigure(0, weight=1)
    frame2.rowconfigure(1, weight=1)
    frame2.columnconfigure(1, weight=1)

    frame3 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame3.grid(row=2, column=0, sticky="WE")
    frame3_B1_ofnewWord2 = tk.Button(frame3, height=2, relief="groove", bg="lightgreen",
                                     text="上一个", command=frame2_B1_ofnewWord2_Clicked)
    frame3_B1_ofnewWord2.grid(row=0, column=0, sticky="WE")
    rootC2.bind('<KeyPress-Left>', frame2_B1_ofnewWord2_Clicked)  # 将按钮"上一个"与键盘上←绑定
    rootC2.bind('<KeyPress-A>', frame2_B1_ofnewWord2_Clicked)  # 将按钮"上一个"与键盘上1绑定
    frame3_B2_ofnewWord2 = tk.Button(frame3, height=2, relief="groove", bg="lightgreen",
                                     text="下一个", command=frame2_B2_ofnewWord2_Clicked)
    frame3_B2_ofnewWord2.grid(row=0, column=1, sticky="WE")
    rootC2.bind('<KeyPress-Right>', frame2_B2_ofnewWord2_Clicked)  # 将按钮"下一个"与键盘上→绑定
    rootC2.bind('<KeyPress-D>', frame2_B2_ofnewWord2_Clicked)  # 将按钮"下一个"与键盘上3绑定
    frame3.columnconfigure(0, weight=1)
    frame3.columnconfigure(1, weight=1)

    frame4 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame4.grid(row=3, column=0, sticky="WE")
    global wordHide2, paraphraseHide2, yesOrNo10, yesOrNo20
    wordHide2 = tk.IntVar()
    paraphraseHide2 = tk.IntVar()
    yesOrNo10 = tk.IntVar()
    yesOrNo20 = tk.IntVar()
    # 设置单选框
    frame4_C1_ofnewWord2 = tk.Checkbutton(frame4, bg="lightgreen", text="隐藏单词", variable=wordHide2, onvalue=1,
                                          offvalue=0, command=frame4_C1_ofnewWord2_Clicked)
    frame4_C1_ofnewWord2.grid(row=0, column=0)
    frame4_C2_ofnewWord2 = tk.Checkbutton(frame4, bg="lightgreen", text="隐藏释义", variable=paraphraseHide2,
                                          onvalue=1, offvalue=0, command=frame4_C2_ofnewWord2_Clicked)
    frame4_C2_ofnewWord2.grid(row=0, column=1)
    # 设置复选框
    frame4_C3_ofnewWord2 = tk.Checkbutton(frame4, bg="lightgreen", text="喝醉都认识", variable=yesOrNo10,
                                          onvalue=1, offvalue=0, command=frame4_C3_ofnewWord2_Clicked)
    frame4_C3_ofnewWord2.grid(row=0, column=2)
    cur.execute("SELECT word From familiarWords")
    global familiarWords
    familiarWords = []  # 用于存储喝醉酒都认识的单词
    for i in cur.fetchall():
        familiarWords.append(i[0])
    if word_L1 in familiarWords:
        yesOrNo10.set(1)  # 设置复选框3的状态
    else:
        yesOrNo10.set(0)
    frame4_C4_ofnewWord2 = tk.Checkbutton(frame4, bg="lightgreen", text="认识", variable=yesOrNo20,
                                          onvalue=1, offvalue=0, command=frame4_C4_ofnewWord2_Clicked)
    frame4_C4_ofnewWord2.grid(row=0, column=3)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (word_L1))
    yesOrNo20.set(cur.fetchone()[0])  # 设置复选框4的状态

    frame4.columnconfigure(0, weight=1)
    frame4.columnconfigure(1, weight=1)
    frame4.columnconfigure(2, weight=1)
    frame4.columnconfigure(3, weight=1)

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    rootC2.columnconfigure(0, weight=1)
    rootC2.rowconfigure(0, weight=1)
    rootC2.protocol('WM_DELETE_WINDOW', rootC2_destroy)
    rootC2.mainloop()  # 进入消息循环，也就是显示窗口

    cur.close()
    con.close()
    cur2.close()
    con2.close()
    return
# 按键”确定“
def frame1_B1_ofnewWord2_Clicked(event=None):
    global indexNum2
    try:
        indexNum2 = int(frame1_E1_ofnewWord2.get())
    except:
        messagebox.showwarning("警告", '请输入数字')
        return
    if indexNum2 < 1 or indexNum2 > sum_words2:
        messagebox.showwarning("警告", '请注意数字范围')
        return
    indexNum2 = indexNum2 - 1
    frame2_E1_ofnewWord2.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord2.insert(0, newWord_list2[indexNum2][0])
    frame2_T1_ofnewWord2.delete(1.0, tk.END)  # 清空原来释义
    hide2 = paraphraseHide2.get()
    if hide2 == 1:
        frame2_T1_ofnewWord2.delete(1.0, tk.END)
        frame2_T1_ofnewWord2.insert(tk.END, "********")
        frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord2.delete(1.0, tk.END)
        frame2_T1_ofnewWord2.insert(tk.END, newWord_list2[indexNum2][1])
        frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')
    return
# 按键"<<"
def frame2_B1_ofnewWord2_Clicked(event=None):
    con = open_wordbank()
    cur = con.cursor()
    global indexNum2
    indexNum2 -= 1
    if indexNum2 == -1:
        indexNum2 = sum_words2 - 1  # 如果减到-1，则跳到最后一个单词
    num_E1 = str(indexNum2 + 1)
    frame1_E1_ofnewWord2.delete(0, tk.END)  # 清空原来数字
    frame1_E1_ofnewWord2.insert(0, num_E1)
    new_word = newWord_list2[indexNum2][0]
    if new_word in familiarWords:
        yesOrNo10.set(1)  # 设置复选框3的状态
    else:
        yesOrNo10.set(0)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (new_word))
    yesOrNo20.set(cur.fetchone()[0])  # 设置复选框4的状态
    frame2_E1_ofnewWord2.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord2.insert(0, new_word)  # 填入新单词
    frame2_T1_ofnewWord2.delete(1.0, tk.END)  # 清空原来释义
    hide2 = paraphraseHide2.get()
    if hide2 == 1:
        frame2_T1_ofnewWord2.delete(1.0, tk.END)
        frame2_T1_ofnewWord2.insert(tk.END, "********")
        frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord2.delete(1.0, tk.END)
        frame2_T1_ofnewWord2.insert(tk.END, newWord_list2[indexNum2][1])
        frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')
    cur.close()
    con.close()
    return
# 按键">>"
def frame2_B2_ofnewWord2_Clicked(event=None):
    con = open_wordbank()
    cur = con.cursor()
    global indexNum2
    indexNum2 += 1
    if indexNum2 == sum_words2:
        indexNum2 = 0  # 如果加到最大，则跳到第一个单词
    num_E1 = str(indexNum2 + 1)
    frame1_E1_ofnewWord2.delete(0, tk.END)  # 清空原来数字
    frame1_E1_ofnewWord2.insert(0, num_E1)
    new_word = newWord_list2[indexNum2][0]
    if new_word in familiarWords:
        yesOrNo10.set(1)  # 设置复选框3的状态
    else:
        yesOrNo10.set(0)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (new_word))
    yesOrNo20.set(cur.fetchone()[0])  # 设置复选框4的状态
    frame2_E1_ofnewWord2.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord2.insert(0, new_word)  # 填入新的单词
    frame2_T1_ofnewWord2.delete(1.0, tk.END)  # 清空原来释义
    hide2 = paraphraseHide2.get()
    if hide2 == 1:
        frame2_T1_ofnewWord2.delete(1.0, tk.END)
        frame2_T1_ofnewWord2.insert(tk.END, "********")
        frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord2.delete(1.0, tk.END)
        frame2_T1_ofnewWord2.insert(tk.END, newWord_list2[indexNum2][1])
        frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')
    cur.close()
    con.close()
    return
# 复选框对应函数
def frame4_C1_ofnewWord2_Clicked():
    hide1 = wordHide2.get()
    if hide1 == 1:
        frame2_E1_ofnewWord2.config(show="*")
    else:
        frame2_E1_ofnewWord2.config(show="")
    return
def frame4_C2_ofnewWord2_Clicked():
    hide2 = paraphraseHide2.get()
    if hide2 == 1:
        frame2_T1_ofnewWord2.delete(1.0, tk.END)
        frame2_T1_ofnewWord2.insert(tk.END, "********")
        frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord2.delete(1.0, tk.END)
        frame2_T1_ofnewWord2.insert(tk.END, newWord_list2[indexNum2][1])
        frame2_T1_ofnewWord2.tag_add('center', '1.0', 'end')
    return
def frame4_C3_ofnewWord2_Clicked():
    word = newWord_list2[indexNum2][0]
    con = open_wordbank()
    cur = con.cursor()
    num = yesOrNo10.get()
    if num == 1:
        try:
            cur.execute("INSERT INTO familiarWords VALUES(?)", (word,))
            con.commit()
        except Exception as e:
            pass
    else:
        try:
            cur.execute("DELETE FROM familiarWords WHERE word='%s'" % (word))
            con.commit()
        except:
            pass
    cur.close()
    con.close()
def frame4_C4_ofnewWord2_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    num = yesOrNo20.get()
    word = newWord_list2[indexNum2][0]
    sql = "UPDATE GuiC_Entry SET num=%d  WHERE name = 'E1_ofnewWord2'" % (num)
    cur.execute("UPDATE wordFromNow SET yesOrNo=%d  WHERE word = '%s'" % (num, word))
    con.commit()
    cur.close()
    con.close()
    return
# rootC2关闭时调用
def rootC2_destroy():

    try:
        indexNum2 = int(frame1_E1_ofnewWord2.get())
    except:
        messagebox.showwarning("警告", '请输入数字')
        return
    if indexNum2 < 1 or indexNum2 > sum_words2:
        messagebox.showwarning("警告", '请注意数字范围')
        return
    con = open_jidanci()
    cur = con.cursor()
    num = int(indexNum2)
    # cur.execute("INSERT INTO GuiC_Entry VALUES(?,?)", ("E1_ofnewWord2", num))
    sql = "UPDATE GuiC_Entry SET num=%d  WHERE name = 'E1_ofnewWord2'" % (num)
    cur.execute(sql)
    con.commit()
    rootC2.destroy()
    cur.close()
    con.close()
    return
# -----------------------Button06-----------------------
def frameC12_Button06_Clicked():
    global newWord_list3, indexNum3, sum_words3
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word,paraphrase From wordFromNow where yesOrNo=1')
    newWord_list3 = cur.fetchall()  # [('scientist', 'n. 科学家'),
    if newWord_list3 == []:
        messagebox.showerror("出错", '请查看《单词本-认识》有无内容')
        return
    sum_words3 = len(newWord_list3)  # sum_words3 单词总数
    global rootC3
    rootC3 = tk.Toplevel(root)
    rootC3.title('过滤-单词本-认识')
    rootC3.geometry("500x350")
    rootC3.grab_set()
    frame = tk.Frame(rootC3, bg="lightgreen", highlightthickness=0)
    frame.grid(row=0, column=0, sticky="WENS")

    global frame1_E1_ofnewWord3
    frame1 = tk.Frame(frame, bg="red")
    frame1.grid(row=0, column=0, sticky="WES")
    frame1_l1_ofnewWord3 = tk.Label(frame1, height=2, text="第", bg="red", fg="yellow", font=('黑体', 15, 'bold'))
    frame1_l1_ofnewWord3.grid(row=0, column=0, sticky="E")
    text_offrame1_l2 = "个 / 共 %d 个" % (sum_words3)
    frame1_l2_ofnewWord3 = tk.Label(frame1, text=text_offrame1_l2, bg="red", fg="yellow", font=('黑体', 15, 'bold'))
    frame1_l2_ofnewWord3.grid(row=0, column=2, sticky="W")
    frame1_E1_ofnewWord3 = tk.Entry(frame1, width=4, borderwidth=0, justify=tk.CENTER, bg="red",
                                    font=('黑体', 15, 'bold'))
    frame1_E1_ofnewWord3.grid(row=0, column=1)
    # 读取上次frame1_E1_ofnewWord3显示的数字
    con2 = open_jidanci()
    cur2 = con2.cursor()
    cur2.execute("SELECT num From GuiC_Entry WHERE name='E1_ofnewWord3'")  # 读取上次frame1_E1_ofnewWord3显示的数字
    con2.commit()
    indexNum3 = cur2.fetchone()[0] - 1
    num_E1 = str(indexNum3 + 1)
    if int(num_E1) <= sum_words3:
        frame1_E1_ofnewWord3.insert(0, num_E1)
    else:
        indexNum3 = 0
        frame1_E1_ofnewWord3.insert(0, '1')
    frame1_B1_ofnewWord3= tk.Button(frame1, height=1, width=5, bg="red", text="确定",
                                     command=frame1_B1_ofnewWord3_Clicked)
    frame1_B1_ofnewWord3.grid(row=0, column=3)
    rootC3.bind('<KeyPress-Return>', frame1_B1_ofnewWord3_Clicked)  # 将按钮"确定"与键盘上回车绑定
    frame1.columnconfigure(0, weight=1)
    frame1.columnconfigure(2, weight=1)

    global frame2_E1_ofnewWord3, frame2_T1_ofnewWord3
    frame2 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame2.grid(row=1, column=0, sticky="WENS")
    frame2_B1_ofnewWord3 = tk.Button(frame2, height=2, bg="lightgreen", borderwidth=0, relief="groove",
                                     text="<<", command=frame2_B1_ofnewWord3_Clicked)
    frame2_B1_ofnewWord3.grid(row=0, column=0, rowspan=2)
    frame2_B2_ofnewWord3 = tk.Button(frame2, height=2, bg="lightgreen", borderwidth=0, relief="groove",
                                     text=">>", command=frame2_B2_ofnewWord3_Clicked)
    frame2_B2_ofnewWord3.grid(row=0, column=2, rowspan=2)
    # 显示单词：
    word_L1 = newWord_list3[indexNum3][0]
    frame2_E1_ofnewWord3 = tk.Entry(frame2, bg="lightgreen", justify="center", font=('黑体', 20))
    frame2_E1_ofnewWord3.grid(row=0, column=1, ipady=10, pady=45)
    frame2_E1_ofnewWord3.insert(0, word_L1)
    # 显示释义：
    paraphrase_E1 = newWord_list3[indexNum3][1]
    frame2_T1_ofnewWord3 = tk.Text(frame2, height=5, borderwidth=0, bg="lightgreen", font=('黑体', 15))
    frame2_T1_ofnewWord3.grid(row=1, column=1, ipady=15)
    frame2_T1_ofnewWord3.tag_configure("center", justify='center')
    frame2_T1_ofnewWord3.insert(tk.END, paraphrase_E1)
    frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')

    frame2.rowconfigure(0, weight=1)
    frame2.rowconfigure(1, weight=1)
    frame2.columnconfigure(1, weight=1)

    frame3 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame3.grid(row=2, column=0, sticky="WE")
    frame3_B1_ofnewWord3 = tk.Button(frame3, height=2, relief="groove", bg="lightgreen",
                                     text="上一个", command=frame2_B1_ofnewWord3_Clicked)
    frame3_B1_ofnewWord3.grid(row=0, column=0, sticky="WE")
    rootC3.bind('<KeyPress-Left>', frame2_B1_ofnewWord3_Clicked)  # 将按钮"上一个"与键盘上←绑定
    rootC3.bind('<KeyPress-A>', frame2_B1_ofnewWord3_Clicked)  # 将按钮"上一个"与键盘上1绑定
    frame3_B2_ofnewWord3 = tk.Button(frame3, height=2, relief="groove", bg="lightgreen",
                                     text="下一个", command=frame2_B2_ofnewWord3_Clicked)
    frame3_B2_ofnewWord3.grid(row=0, column=1, sticky="WE")
    rootC3.bind('<KeyPress-Right>', frame2_B2_ofnewWord3_Clicked)  # 将按钮"下一个"与键盘上→绑定
    rootC3.bind('<KeyPress-D>', frame2_B2_ofnewWord3_Clicked)  # 将按钮"下一个"与键盘上3绑定
    frame3.columnconfigure(0, weight=1)
    frame3.columnconfigure(1, weight=1)

    frame4 = tk.Frame(frame, bg="lightgreen", highlightthickness=0)
    frame4.grid(row=3, column=0, sticky="WE")
    global wordHide2, paraphraseHide3, yesOrNo100, yesOrNo200
    wordHide2 = tk.IntVar()
    paraphraseHide3 = tk.IntVar()
    yesOrNo100 = tk.IntVar()
    yesOrNo200 = tk.IntVar()
    # 设置单选框
    frame4_C1_ofnewWord3 = tk.Checkbutton(frame4, bg="lightgreen", text="隐藏单词", variable=wordHide2, onvalue=1,
                                          offvalue=0, command=frame4_C1_ofnewWord3_Clicked)
    frame4_C1_ofnewWord3.grid(row=0, column=0)
    frame4_C2_ofnewWord3 = tk.Checkbutton(frame4, bg="lightgreen", text="隐藏释义", variable=paraphraseHide3,
                                          onvalue=1, offvalue=0, command=frame4_C2_ofnewWord3_Clicked)
    frame4_C2_ofnewWord3.grid(row=0, column=1)
    # 设置复选框
    frame4_C3_ofnewWord3 = tk.Checkbutton(frame4, bg="lightgreen", text="喝醉都认识", variable=yesOrNo100,
                                          onvalue=1, offvalue=0, command=frame4_C3_ofnewWord3_Clicked)
    frame4_C3_ofnewWord3.grid(row=0, column=2)
    cur.execute("SELECT word From familiarWords")
    global familiarWords
    familiarWords = []  # 用于存储喝醉酒都认识的单词
    for i in cur.fetchall():
        familiarWords.append(i[0])
    if word_L1 in familiarWords:
        yesOrNo100.set(1)  # 设置复选框3的状态
    else:
        yesOrNo100.set(0)
    frame4_C4_ofnewWord3 = tk.Checkbutton(frame4, bg="lightgreen", text="认识", variable=yesOrNo200,
                                          onvalue=1, offvalue=0, command=frame4_C4_ofnewWord3_Clicked)
    frame4_C4_ofnewWord3.grid(row=0, column=3)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (word_L1))
    yesOrNo200.set(cur.fetchone()[0])  # 设置复选框4的状态

    frame4.columnconfigure(0, weight=1)
    frame4.columnconfigure(1, weight=1)
    frame4.columnconfigure(2, weight=1)
    frame4.columnconfigure(3, weight=1)

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    rootC3.columnconfigure(0, weight=1)
    rootC3.rowconfigure(0, weight=1)
    rootC3.protocol('WM_DELETE_WINDOW', rootC3_destroy)
    rootC3.mainloop()  # 进入消息循环，也就是显示窗口

    cur.close()
    con.close()
    cur2.close()
    con2.close()
    return
# 按键”确定“
def frame1_B1_ofnewWord3_Clicked(event=None):
    global indexNum3
    try:
        indexNum3 = int(frame1_E1_ofnewWord3.get())
    except:
        messagebox.showwarning("警告", '请输入数字')
        return
    if indexNum3 < 1 or indexNum3 > sum_words3:
        messagebox.showwarning("警告", '请注意数字范围')
        return
    indexNum3 = indexNum3 - 1
    frame2_E1_ofnewWord3.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord3.insert(0, newWord_list3[indexNum3][0])
    frame2_T1_ofnewWord3.delete(1.0, tk.END)  # 清空原来释义
    hide2 = paraphraseHide3.get()
    if hide2 == 1:
        frame2_T1_ofnewWord3.delete(1.0, tk.END)
        frame2_T1_ofnewWord3.insert(tk.END, "********")
        frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord3.delete(1.0, tk.END)
        frame2_T1_ofnewWord3.insert(tk.END, newWord_list3[indexNum3][1])
        frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')
    return
    # 按键"<<"
def frame2_B1_ofnewWord3_Clicked(event=None):
    con = open_wordbank()
    cur = con.cursor()
    global indexNum3
    indexNum3 -= 1
    if indexNum3 == -1:
        indexNum3 = sum_words3 - 1  # 如果减到-1，则跳到最后一个单词
    num_E1 = str(indexNum3 + 1)
    frame1_E1_ofnewWord3.delete(0, tk.END)  # 清空原来数字
    frame1_E1_ofnewWord3.insert(0, num_E1)
    new_word = newWord_list3[indexNum3][0]
    if new_word in familiarWords:
        yesOrNo100.set(1)  # 设置复选框3的状态
    else:
        yesOrNo100.set(0)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (new_word))
    yesOrNo200.set(cur.fetchone()[0])  # 设置复选框4的状态
    frame2_E1_ofnewWord3.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord3.insert(0, new_word)  # 填入新单词
    frame2_T1_ofnewWord3.delete(1.0, tk.END)  # 清空原来释义
    hide2 = paraphraseHide3.get()
    if hide2 == 1:
        frame2_T1_ofnewWord3.delete(1.0, tk.END)
        frame2_T1_ofnewWord3.insert(tk.END, "********")
        frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord3.delete(1.0, tk.END)
        frame2_T1_ofnewWord3.insert(tk.END, newWord_list3[indexNum3][1])
        frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')
    cur.close()
    con.close()
    return
    # 按键">>"
def frame2_B2_ofnewWord3_Clicked(event=None):
    con = open_wordbank()
    cur = con.cursor()
    global indexNum3
    indexNum3 += 1
    if indexNum3 == sum_words3:
        indexNum3 = 0  # 如果加到最大，则跳到第一个单词
    num_E1 = str(indexNum3 + 1)
    frame1_E1_ofnewWord3.delete(0, tk.END)  # 清空原来数字
    frame1_E1_ofnewWord3.insert(0, num_E1)
    new_word = newWord_list3[indexNum3][0]
    if new_word in familiarWords:
        yesOrNo100.set(1)  # 设置复选框3的状态
    else:
        yesOrNo100.set(0)
    cur.execute("SELECT yesOrNo From wordFromNow where word='%s'" % (new_word))
    yesOrNo200.set(cur.fetchone()[0])  # 设置复选框4的状态
    frame2_E1_ofnewWord3.delete(0, tk.END)  # 清空原来单词
    frame2_E1_ofnewWord3.insert(0, new_word)  # 填入新的单词
    frame2_T1_ofnewWord3.delete(1.0, tk.END)  # 清空原来释义
    hide2 = paraphraseHide3.get()
    if hide2 == 1:
        frame2_T1_ofnewWord3.delete(1.0, tk.END)
        frame2_T1_ofnewWord3.insert(tk.END, "********")
        frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord3.delete(1.0, tk.END)
        frame2_T1_ofnewWord3.insert(tk.END, newWord_list3[indexNum3][1])
        frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')
    cur.close()
    con.close()
    return
    # 复选框对应函数
def frame4_C1_ofnewWord3_Clicked():
    hide1 = wordHide2.get()
    if hide1 == 1:
        frame2_E1_ofnewWord3.config(show="*")
    else:
        frame2_E1_ofnewWord3.config(show="")
    return
def frame4_C2_ofnewWord3_Clicked():
    hide2 = paraphraseHide3.get()
    if hide2 == 1:
        frame2_T1_ofnewWord3.delete(1.0, tk.END)
        frame2_T1_ofnewWord3.insert(tk.END, "********")
        frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')
    else:
        frame2_T1_ofnewWord3.delete(1.0, tk.END)
        frame2_T1_ofnewWord3.insert(tk.END, newWord_list3[indexNum3][1])
        frame2_T1_ofnewWord3.tag_add('center', '1.0', 'end')
    return
def frame4_C3_ofnewWord3_Clicked():
    word = newWord_list3[indexNum3][0]
    con = open_wordbank()
    cur = con.cursor()
    num = yesOrNo100.get()
    if num == 1:
        try:
            cur.execute("INSERT INTO familiarWords VALUES(?)", (word,))
            con.commit()
        except Exception as e:
            pass
    else:
        try:
            cur.execute("DELETE FROM familiarWords WHERE word='%s'" % (word))
            con.commit()
        except:
            pass
    cur.close()
    con.close()
def frame4_C4_ofnewWord3_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    num = yesOrNo200.get()
    word = newWord_list3[indexNum3][0]
    sql = "UPDATE GuiC_Entry SET num=%d  WHERE name = 'E1_ofnewWord3'" % (num)
    cur.execute("UPDATE wordFromNow SET yesOrNo=%d  WHERE word = '%s'" % (num, word))
    con.commit()
    cur.close()
    con.close()
    return
    # rootC3关闭时调用
def rootC3_destroy():
    try:
        indexNum3 = int(frame1_E1_ofnewWord3.get())
    except:
        messagebox.showwarning("警告", '请输入数字')
        return
    if indexNum3 < 1 or indexNum3 > sum_words3:
        messagebox.showwarning("警告", '请注意数字范围')
        return
    con = open_jidanci()
    cur = con.cursor()
    num = int(indexNum3)
    # cur.execute("INSERT INTO GuiC_Entry VALUES(?,?)", ("E1_ofnewWord3", num))
    sql = "UPDATE GuiC_Entry SET num=%d  WHERE name = 'E1_ofnewWord3'" % (num)
    cur.execute(sql)
    con.commit()
    rootC3.destroy()
    cur.close()
    con.close()
    return
# -----------------------Button07-----------------------
def frameC20_Button07_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word From familiarWords')
    familiarWord_list = cur.fetchall()
    familiarWord_num = len(familiarWord_list)
    familiarWord_num = "共：%d 个\n" % (familiarWord_num)
    familiarWord_str = ""
    familiarWord_list.sort()
    for i in familiarWord_list:
        familiarWord_str += "    " + i[0] + "\n"
    root1 = tk.Toplevel(root)
    root1.title('喝醉酒都认识的单词')
    root1.geometry("600x400")
    root1.grab_set()
    text = tk.Text(root1, borderwidth=0, bg="lightgreen", font=('Arial', 12))
    text.grid(row=0, column=0, padx=5, pady=5, sticky="NSWE")
    scrollbar1 = tk.Scrollbar(root1)
    scrollbar1.grid(row=0, column=1, padx=0, pady=5, sticky="NS")
    text['yscrollcommand'] = scrollbar1.set  # 链接 文本 和 滚动条
    scrollbar1['command'] = text.yview
    root1.rowconfigure(0, weight=1)
    root1.columnconfigure(0, weight=1)
    text.insert(tk.END, familiarWord_num)
    text.insert(tk.END, familiarWord_str)
    cur.close()
    con.close()
    return
# -----------------------Button08-----------------------
def frameC21_Button08_Clicked():
    m = messagebox.askokcancel("再次确认", "确定清空熟词吗？")
    if m == True:
        con = open_wordbank()
        cur = con.cursor()
        cur.execute('DELETE FROM familiarWords')
        con.commit()
        cur.close()
        con.close()
    else:
        pass
    return
# -----------------------Button09-----------------------
def frameC22_Button09_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word From wordFromNow where yesOrNo=0')
    newWord_list = cur.fetchall()
    newWord_num = len(newWord_list)
    newWord_num = "共：%d 个\n" % (newWord_num)
    newWord_str = ""
    for i in newWord_list:
        newWord_str += i[0] + "\n"
    root1 = tk.Toplevel(root)
    root1.title('生词本')
    root1.geometry("600x400")
    root1.grab_set()
    text = tk.Text(root1, font=('Arial', 12))
    text.grid(row=0, column=0, padx=5, pady=5, sticky="NSWE")
    scrollbar1 = tk.Scrollbar(root1)
    scrollbar1.grid(row=0, column=1, padx=0, pady=5, sticky="NS")
    text['yscrollcommand'] = scrollbar1.set  # 链接 文本 和 滚动条
    scrollbar1['command'] = text.yview
    root1.rowconfigure(0, weight=1)
    root1.columnconfigure(0, weight=1)
    text.insert(tk.END, newWord_num)
    text.insert(tk.END, newWord_str)
    cur.close()
    con.close()
    return
# -----------------------Button10-----------------------
def frameC30_Button10_Clicked():
    con = open_wordbank()
    cur = con.cursor()
    cur.execute('SELECT word,frequency From wordFromNow order by frequency DESC')
    Word_list = cur.fetchall()
    Word_num = len(Word_list)
    Word_num = "共：%d 个\n" % (Word_num)
    Word_str = ""
    for i in Word_list:
        Word_str += i[0] + "\t\t" + str(i[1]) + "\n"
    root1 = tk.Toplevel(root)
    root1.title('词频总计')
    root1.geometry("600x400")
    root1.grab_set()
    text = tk.Text(root1, font=('Arial', 12))  # Helvetica Bodoni Garamond Frutiger
    text.grid(row=0, column=0, padx=5, pady=5, sticky="NSWE")
    scrollbar1 = tk.Scrollbar(root1)
    scrollbar1.grid(row=0, column=1, padx=0, pady=5, sticky="NS")
    text['yscrollcommand'] = scrollbar1.set  # 链接 文本 和 滚动条
    scrollbar1['command'] = text.yview
    root1.rowconfigure(0, weight=1)
    root1.columnconfigure(0, weight=1)
    text.insert(tk.END, Word_num)
    text.insert(tk.END, Word_str)
# -----------------------Button11-----------------------
def frameC31_Button11_Clicked():
    root1 = tk.Toplevel(root)
    root1.title('单词本-All')
    root1.geometry("600x400")
    root1.grab_set()
    global text_ofAddWords
    text_ofAddWords = tk.Text(root1, font=('Arial', 12))
    text_ofAddWords.grid(row=0, column=0, padx=5, pady=1, sticky="NSWE")
    text_ofAddWords.insert(tk.END, "按如下格式输入：（输入前将本段删除！）\n1\ta\tart. 一；任何一\n2\tgo\tvi. 去；走\n、、、"
                                   "\n（注意中间不是空格，是制表符“Tab”！）")
    scrollbar1 = tk.Scrollbar(root1)
    scrollbar1.grid(row=0, column=1, padx=0, pady=5, sticky="NS")
    text_ofAddWords['yscrollcommand'] = scrollbar1.set  # 链接 文本 和 滚动条
    scrollbar1['command'] = text_ofAddWords.yview
    button_ofAddWords = tk.Button(root1, text='确定', command=button_ofAddWords_Clicked)
    button_ofAddWords.grid(row=1, column=0, ipadx=12, pady=5)

    root1.rowconfigure(0, weight=1)
    root1.columnconfigure(0, weight=1)
    return
# 确定添加到词库
def button_ofAddWords_Clicked():
    m = messagebox.askokcancel("再次确认", "确定 添加进词库吗？")
    if m == True:
        pass
    else:
        return
    con = open_wordbank()
    cur = con.cursor()
    text = text_ofAddWords.get(2.0, "end")
    text = text.split('\n')
    for i in text:      # 检查输入的格式对不对
        if i == '':  # 忽略空行
            continue
        str2 = i.rstrip().split('\t')
        try:
            word = str2[1]
        except:
            messagebox.showwarning("警告", '请查看格式是否正确')
            return
    for str1 in text:
        if str1 == '':
            continue
        str2 = str1.rstrip().split('\t')
        split_str = " 时 态| 形容词| 名 词| 比较级| 副 词|时 态|形容词|名 词|比较级|副 词|abbr"
        word = str2[1]
        text_ofAddWords.insert(1.0, word + '\n\n')
        paraphrase = re.split(split_str, str2[2])[0]
        if " " not in word:
            try:
                cur.execute('insert into words(word,soundmark,paraphrase,pronunciation,picture) values(?,?,?,?,?)',
                         (word, None, paraphrase, None, None))
                con.commit()
            except Exception as e:
                str1 = str(e)
                text_ofAddWords.insert(1.0, str1+'\n\n')
        else:
            continue
    cur.close()
    con.close()
    return
# -----------------------Button12-----------------------
def frameC32_Button12_Clicked():
    m = messagebox.askokcancel("再次确认", "确定 清空单词本 重新开始吗？")
    if m == True:
        Path = os.getcwd()
        f = open(Path + r'\dates\Z04.wordFrequency.txt', 'w', encoding="UTF-8")
        f.write("# 追加模式，本文件用于保存每次提取的词频，防止反复保存\n单词	出现次数")
        f.close()
        con = open_wordbank()
        cur = con.cursor()
        cur.execute('DELETE FROM wordFromNow')
        con.commit()
        cur.close()
        con.close()
    else:
        pass
    return

'''-----------------------菜单D-------------------------'''
# 菜单D界面布局Gui_D
def Gui_D():
    global frameD, GuiD_Text      # frameD便于后续清空D界面
    frameD = tk.Frame(root, bg="orange")
    frameD.grid(row=0, column=0, sticky="WENS")
    global v1
    v1 = tk.IntVar()
    v1.set(1)
    tk.Radiobutton(frameD, variable=v1, value=1, text='简介', width=5, bg="khaki",
                   command=Gui_D_Radio_clicked).grid(row=0, column=0, sticky="WNS", padx=2, pady=2)
    tk.Radiobutton(frameD, variable=v1, value=2, text='A', width=5, bg="khaki",
                   command=Gui_D_Radio_clicked).grid(row=1, column=0, sticky="WNS", padx=2, pady=2)
    tk.Radiobutton(frameD, variable=v1, value=3, text='B', width=5, bg="khaki",
                   command=Gui_D_Radio_clicked).grid(row=2, column=0, sticky="WNS", padx=2, pady=2)
    tk.Radiobutton(frameD, variable=v1, value=4, text='C', width=5, bg="khaki",
                   command=Gui_D_Radio_clicked).grid(row=3, column=0, sticky="WNS", padx=2, pady=2)
    GuiD_Text = tk.Text(frameD, bd=0, bg="navajowhite", font=('system', 12))
    GuiD_Text.grid(row=0, column=1, rowspan=4, sticky="WENS", pady=2, padx=0)

    str = """曾听考研区up @颉斌斌老师 一言，醍醐灌顶!\n\n市面上没有一本词汇书是为你量身定做的!\n \
    \n各式各样的记单词大法，归根到底不过是重复重复再重复!\n\n而本程序旨在助力重复的过程中定制出专属于自己的单词本！\n \
    \n\n最开始编写程序的时候正是想实现如界面A这么一个功能\n\n来辅助我记单词\n\n但是没有找到音标资源用的很别扭\n \
    \n再加上记单词记得很是无聊\n\n就想能不能一篇一篇文章的积累单词\n\n因而后又乱七八糟有了B界面和C界面\n \
    \n后发现可打包为可执行程序\n\n因此又加上了D来记录功能"""
    GuiD_Text.insert(tk.END, str)
    str = "\n\n\n\n\n该可执行程序归个人所有，请勿商用。    \n\nB站：@丰收奇迹\n\n\n\n\n\n\n\n\n"
    GuiD_Text.insert(tk.END, str)
    scrollbar1 = tk.Scrollbar(frameD)
    scrollbar1.grid(row=0, column=2, rowspan=4, padx=2, pady=2, sticky="NS")
    GuiD_Text['yscrollcommand'] = scrollbar1.set  # 链接 文本 和 滚动条
    scrollbar1['command'] = GuiD_Text.yview
    frameD.columnconfigure(1, weight=1)
    frameD.rowconfigure(0, weight=1)
    frameD.rowconfigure(1, weight=1)
    frameD.rowconfigure(2, weight=1)
    frameD.rowconfigure(3, weight=1)
def Gui_D_Radio_clicked():
    GuiD_Text.delete(1.0, tk.END)
    num = v1.get()
    if num == 1:
        str = """曾听考研区up @颉斌斌老师 一言，醍醐灌顶!\n\n市面上没有一本词汇书是为你量身定做的!\n \
        \n各式各样的记单词大法，归根到底不过是重复重复再重复!\n\n而本程序旨在助力重复的过程中定制出专属于自己的单词本！\n \
        \n\n最开始编写程序的时候正是想实现如界面A这么一个功能\n\n来辅助我记单词\n\n但是没有找到音标资源用的很别扭\n \
        \n再加上记单词记得很是无聊\n\n就想能不能一篇一篇文章的积累单词\n\n因而后又乱七八糟有了B界面和C界面\n \
        \n后发现可打包为可执行程序\n\n因此又加上了D来记录功能"""
        GuiD_Text.insert(1.0, str)
        str = "\n\n\n\n\n该可执行程序归个人所有，请勿商用。    \n\nB站：@丰收奇迹\n\n\n\n\n\n\n\n\n"
        GuiD_Text.insert(tk.END, str)
    if num == 2:
        str = """功能详记：\tA\n\n正如A界面所示\n\n可以选择词本，词本收录在数据库文件中\n \
        \n（CET-4、CET-6以及考研词汇选择的是恋恋有词四六级及考研词汇）\n\n然后本程序会自动将其分为:7个单元、每单元4个分组、共28组\n \
        \n点击按钮记单词的同时\n\n程序会自动保存当时的时间和选择的词本以及分组\n\n点击按钮记录板可以查看\n \
        \n\n\n\n\n建议：  28 / 28 / 14 / 14 / 7 / 7 / 7.....\n\n在选择好词本后，建议使用B站:@颉斌斌老师的方法，反复记忆单词\n \
        \n第一轮每天一个分组，第二轮依旧每天一个分组\n\n28天一轮\n\n在过单词的时候熟悉的单词快速过\n \
        \n不认识的单词可以多停留几秒，在脑海中过一边加深印象\n\n两轮之后熟悉词越来越多\n\n第三、四轮可以根据情况每天多加一个分组\n \
        \n14天一轮\n\n再之后陌生词汇越来越少，但是为了保持对单词的熟悉度\n\n依然继续每天记忆，此时可根据自身情况每天记一个单元\n \
        \n一周一轮\n\n\n\n\n\n\n\n\n"""
        GuiD_Text.insert(tk.END, str)
    if num == 3:
        str = """功能详记：\tB\n\nB界面的功能是将文章进行词频统计\n\n点击按钮提取后出现的就是词频记录\n \
        \n新弹出的窗口点击保存会将其记录进数据库，可以在C界面单词本查看\n\n每次保存会将词频进行累计，可在C界面词频总计查看 \
        \n\n\n\n\n\n\n\n\n"""
        GuiD_Text.insert(1.0, str)
    if num == 4:
        str = """功能详记：\tC\n\n\n单词本：可以查看累积遇见的单词，左边是首次遇见该单词的日期\n \
        \n\n过滤—单词：略\n\n\n熟词本：略\n\n\n清空熟词：略\n\n\n生词本:记录了不认识的单词\n \
        \n格式便于复制后到欧路词典官方网站https://my.eudic.net/studyList\n \
        \n粘贴保存单词到欧路词典的生词本\n\n进而便于用手机记忆最后的顽固单词\n\n同时弥补没有音标、音频、发音和不便移动的缺陷\n \
        \n\n词频总计：略\n\n\n扩增词库：略\n\n\n单词本重置：清空等于重新开始记录，慎重！\n\n\n\n\n\n\n\n\n"""
        GuiD_Text.insert(1.0, str)

'''--------------------菜单对应的command---------------------'''
def MenuA_clicked():
    try:
        frameB.destroy()
    except:
        pass
    try:
        frameC.destroy()
    except:
        pass
    try:
        frameD.destroy()
    except:
        pass
    Gui_A()
    return
def MenuB_clicked():
    try:
        frameA.destroy()
    except:
        pass
    try:
        frameC.destroy()
    except:
        pass
    try:
        frameD.destroy()
    except:
        pass
    Gui_B()
    return
def MenuC_clicked():
    try:
        frameA.destroy()
    except:
        pass
    try:
        frameB.destroy()
    except:
        pass
    try:
        frameD.destroy()
    except:
        pass
    Gui_C()
    return
def MenuD_clicked():
    try:
        frameA.destroy()
    except:
        pass
    try:
        frameB.destroy()
    except:
        pass
    try:
        frameC.destroy()
    except:
        pass
    Gui_D()
    return

''' 主程序：'''
if __name__ == "__main__":
    root = tk.Tk()
    root.title('EnglinshQiJi_1.0')
    root.geometry("600x400")
    root.minsize(450, 300)
    root.maxsize(1366, 768)
    menu = tk.Menu(root)      # 创建menu对象
    menu.add_command(label="    A    ", command=MenuA_clicked)
    menu.add_command(label="    B    ", command=MenuB_clicked)
    menu.add_command(label="    C    ", command=MenuC_clicked)
    menu.add_command(label="    Help    ", command=MenuD_clicked)
    # helpmenu = tk.Menu(menu, tearoff=0)        # 指定 helpmenu 是 menu 的子菜单,去除虚线
    # # helpmenu = menu.add_cascade(label="  Help  ", command=MenuD_clicked)
    # menu.add_cascade(label='  Help  ', menu=helpmenu)
    # v = tk.IntVar()
    # v.set(1)
    # helpmenu.add_radiobutton(label='A', command=MenuD_clicked, variable=v, value=1)
    # helpmenu.add_radiobutton(label='B', command=MenuD_clicked, variable=v, value=2)
    # helpmenu.add_radiobutton(label='C', command=MenuD_clicked, variable=v, value=3)
    root['menu'] = menu  # 附加主菜单到窗口
    Gui_A()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()  # 进入消息循环，也就是显示窗口