from pyvi import ViTokenizer, ViPosTagger
from pprint import pprint
import math
import re
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Vanhuy@123",
    database="linktest"
)


# salary, experience,diploma,career,address, positon,category,sex, title
def compareStr(string1, string2):
    return string1.lower().strip() == string2.lower().strip()


def tokenize(string):
    text_token = ViTokenizer.tokenize(string).split()
    return text_token


def normalize_text(string):
    string = string.lower()
    return string.strip()


def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection / union)


def checkIntersec(list1, list2):
    if len(list(set(list1).intersection(list2))) > 0:
        return 1
    else:
        return 0


# experience
def sigmoid_experience(x):
    return 2 / (1 + math.exp(abs(x / 5)))


def get_experience(text):
    exp = re.findall('\d+', text)
    if len(exp) == 0:
        return 0
    return int(exp[0])


def compare_experience(ex1, ex2):
    exp1 = get_experience(ex1)
    exp2 = get_experience(ex2)
    if exp1 > exp2:
        min = exp2
    else:
        min = exp1
    x = abs(exp1 - exp2) / (min + 0.5)
    return sigmoid_experience(x)


# Salary
# text = ['26,000,000 VND', 'Trên 50 triệu', '15 – 20 triệu']
def get_salary(text):
    salary = 0
    # a = re.findall(u'(^|\s)(\d*([,.]?\d+)+)', text)
    a = re.findall(u'(\d*([,.]?\d+)+)', text)
    if len(a) == 0:
        return 1
    elif len(a) == 1:
        salary = int(re.sub('[^0-9]', '', a[0][0]))
    else:
        salary = (int(re.sub('[^0-9]', '', a[0][0])) + int(re.sub('[^0-9]', '', a[1][0]))) / 2
    if salary < 1000:
        salary *= 10 ** 6
    return salary


def sigmoid_salary(x):
    return 2 / (1 + math.exp(abs(x / 3)))


def compare_salary(sal1, sal2):
    salary1 = get_salary(sal1)
    salary2 = get_salary(sal2)
    if salary1 == 1 or salary2 == 1:
        return 1
    min = 1
    if (salary1 > salary2):
        min = salary2
    else:
        min = salary1
    x = abs(salary1 - salary2) / min
    return sigmoid_salary(x)


# career
def compare_career(career1, career2):
    if career1 == career2:
        return 1
    else:
        return 0


# diploma
# -- 'Trên đại học'
# -- 'Đại học'
# -- 'Cao đẳng'
# -- 'Trung cấp'
# -- 'Trung học'
# -- 'Chứng chỉ nghề'
# -- 'Không yêu cầu bằng cấp'

def compare_diploma(dip1, dip2):
    if compareStr(dip1, "Không yêu cầu bằng cấp") or compareStr(dip2, "Không yêu cầu bằng Cấp") or compareStr(dip1,
                                                                                                              dip2):
        return 1
    else:
        return 0


# -- category
# -- 'Toàn thời gian cố định'
# -- 'Toàn thời gian tạm thời'
# -- 'Bán thời gian cố định'
# -- 'Bán thời gian tạm thời'
# -- 'Theo hợp đồng tư vấn'
# -- 'Thực tập'
# -- 'Khác'

def compare_category(cate1, cate2):
    if compareStr(cate1, 'Khác') or compareStr(cate2, 'Khác'):
        return 1
    if compareStr(cate1, 'Thực tập') or compareStr(cate2, 'Thực tập'):
        return 1
    if compareStr(cate1, 'Theo hợp đồng tư vấn') or compareStr(cate2, 'Theo hợp đồng tư vấn'):
        return 1
    if compareStr(cate1, cate2):
        return 1
    else:
        return 0


# address
def compare_address(add1, add2):
    listHCM = ['Tphcm', 'Tp. Hồ Chí Minh', 'Hồ Chí Minh', 'TP HCM', 'TP Hồ Chí Minh', 'HCM']
    check1 = False
    for element in listHCM:
        if element.lower() in add1.lower():
            check1 = True
            break
    check2 = False
    for element in listHCM:
        if element.lower() in add2.lower():
            check2 = True
            break
    if check1 and check2:
        return 1

    address1 = tokenize(normalize_text(add1))
    address2 = tokenize(normalize_text(add2))
    return checkIntersec(address1, address2)


# Title
def compare_title(tit1, tit2):
    title1 = tokenize(normalize_text(tit1))
    title2 = tokenize(normalize_text(tit2))
    return jaccard_similarity(title1, title2)


# Position
def compare_position(pos1, pos2):
    position1 = tokenize(normalize_text(pos1))
    position2 = tokenize(normalize_text(pos2))
    return jaccard_similarity(position1, position2)


# Sex
def compare_sex(sexCan, sexJob):
    if compareStr(sexJob, 'Không yêu cầu'):
        return 1
    if (compareStr(sexJob, 'Nam') and sexCan == 1) or (compareStr(sexJob, 'Nữ') and sexCan == 0):
        return 1
    else:
        return 0


def score(title, career, salary, sex, category, position, diploma, experience, address):
    return title * 0.05 + career * 0.15 + salary * 0.2 + sex * 0.1 + category * 0.1 + position * 0.1 + diploma * 0.05 + experience * 0.15 + address * 0.1


def jobVsCandidate(job):
    pprint(job)
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT title, career, salary, sex, category, position, diploma, experience, address, idstudent FROM student")
    candidates = mycursor.fetchall()
    for candidate in candidates:
        title = compare_title(candidate[0], job[0])
        career = compare_career(candidate[1], job[1])
        salary = compare_salary(candidate[2], job[2])
        sex = compare_sex(candidate[3], job[3])
        category = compare_category(candidate[4], job[4])
        position = compare_position(candidate[5], job[5])
        diploma = compare_diploma(candidate[6], job[6])
        experience = compare_experience(candidate[7], job[7])
        address = compare_address(candidate[8], job[8])
        score_val = score(title, career, salary, sex, category, position, diploma, experience, address)
        if score_val > 0.8:
            try:
                sql = "INSERT INTO job_candidate (idjob, idcandidate, score) VALUES (%s, %s,%s)"
                mycursor.execute(sql, (job[9], candidate[9], score_val))
                mydb.commit()

            except:
                print("Fail Insert!")


# jobVsCandidate()

def initValue():
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT title, idcareer, salary, sex, category, position, diploma, experience, address, idpost FROM post")
    jobs = mycursor.fetchall()
    for job in jobs:
        jobVsCandidate(job)


initValue()
