from pyvi import ViTokenizer, ViPosTagger
from pprint import pprint
import math
import re
import json

# import mysql.connector
from database import mysql

# conn = mysql.connect()

# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="Vanhuy@123",
#     database="linktest"
# )


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


# ----SERVICE INSERT----
def jobVsCandidate(job):
    pprint(job)
    # mycursor = mydb.cursor()
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(
        "SELECT title, career, salary, sex, category, position, diploma, experience, address, idstudent FROM student")
    candidates = mycursor.fetchall()
    for candidate in candidates:
        try:
            title = compare_title(candidate[0], job["title"])
            career = compare_career(candidate[1], job["idcareer"])
            salary = compare_salary(candidate[2], job["salary"])
            sex = compare_sex(candidate[3], job["sex"])
            category = compare_category(candidate[4], job["category"])
            position = compare_position(candidate[5], job["position"])
            diploma = compare_diploma(candidate[6], job["diploma"])
            experience = compare_experience(candidate[7], job["experience"])
            address = compare_address(candidate[8], job["address"])
            score_val = score(title, career, salary, sex, category, position, diploma, experience, address)
            if score_val > 0.76:
                try:
                    sql = "INSERT INTO job_candidate (idjob, idcandidate, score) VALUES (%s, %s,%s) ON DUPLICATE KEY UPDATE score = VALUES(score);"
                    mycursor.execute(sql, (job["idpost"], candidate[9], score_val))
                    # mydb.commit()
                    conn.commit()
                except Exception as e:
                    print('Statement:', e.args)
                    print('Type:', type(e))
                    print("Fail Insert!")

        except Exception as e:
            print('Statement:', e.args)
            print('Type:', type(e))
            print("Data parsing failed!")


def candidateVsPost(candidate):
    pprint(candidate)
    # mycursor = mydb.cursor()
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(
        "SELECT title, idcareer, salary, sex, category, position, diploma, experience, address, idpost FROM post")
    posts = mycursor.fetchall()
    for job in posts:
        try:
            title = compare_title(candidate["title"], job[0])
            career = compare_career(candidate["career"], job[1])
            salary = compare_salary(candidate["salary"], job[2])
            sex = compare_sex(candidate["sex"], job[3])
            category = compare_category(candidate["category"], job[4])
            position = compare_position(candidate["position"], job[5])
            diploma = compare_diploma(candidate["diploma"], job[6])
            experience = compare_experience(candidate["experience"], job[7])
            address = compare_address(candidate["address"], job[8])
            score_val = score(title, career, salary, sex, category, position, diploma, experience, address)
            if score_val > 0.76:
                try:
                    sql = "INSERT INTO job_candidate (idjob, idcandidate, score) VALUES (%s, %s,%s) ON DUPLICATE KEY UPDATE score = VALUES(score);"
                    mycursor.execute(sql, (job[9], candidate["idstudent"], score_val))
                    # mydb.commit()
                    conn.commit()
                except Exception as e:
                    print('Statement:', e.args)
                    print('Type:', type(e))
                    print("Fail Insert!")

        except Exception as e:
            print('Statement:', e.args)
            print('Type:', type(e))
            print("Data parsing failed!")


def selectForJob(idJob):
    # mycursor = mydb.cursor()
    conn = mysql.connect()
    mycursor = conn.cursor()
    sql = "SELECT idcandidate FROM job_candidate where idjob = %s order by score desc "
    mycursor.execute(sql, (idJob,))
    results = mycursor.fetchall()
    pprint(results)
    listCandidate = []
    for candidate in results:
        mycursor.execute("select name,sex,phone,address,position   from student where idstudent = %s", (candidate[0],))
        listCandidate.append(mycursor.fetchone())
    return listCandidate


def selectForCandidate(idCandidate):
    # mycursor = mydb.cursor()
    conn = mysql.connect()
    mycursor = conn.cursor()
    sql = "SELECT idjob FROM job_candidate where idCandidate = %s order by score desc "
    mycursor.execute(sql, (idCandidate,))
    results = mycursor.fetchall()
    listJob = []
    json_data = []
    for job in results:
        mycursor.execute("select idcompany, idpost,category,salary,address,created,expired from post where idpost = %s", (job[0],))
        row_headers = [x[0] for x in mycursor.description]
        datajob = mycursor.fetchone()
        pprint(row_headers)
        json_data.append(dict(zip(row_headers, datajob)))
        listJob.append(datajob)
        pprint(json_data)
    # pprint(json.dumps(json_data))
    return json_data

# ---- INIT Value-----
def initJobVsCandidate(job):
    pprint(job)
    # mycursor = mydb.cursor()
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(
        "SELECT title, career, salary, sex, category, position, diploma, experience, address, idstudent FROM student")
    pprint(mycursor.description)
    candidates = mycursor.fetchall()
    for candidate in candidates:
        try:
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
                    sql = "INSERT INTO job_candidate (idjob, idcandidate, score) VALUES (%s, %s,%s) ON DUPLICATE KEY UPDATE score = VALUES(score);"
                    mycursor.execute(sql, (job[9], candidate[9], score_val))
                    # mydb.commit()
                    conn.commit()

                except BaseException as e:
                    print('Statement:', e.args)
                    print('Type:', type(e))
                    print("Fail Insert!")

        except BaseException as e:
            print('Statement:', e.args)
            print('Type:', type(e))
            print("Data parsing failed!")


def initCandidateVsPost(candidate):
    pprint(candidate)
    # mycursor = mydb.cursor()
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(
        "SELECT title, idcareer, salary, sex, category, position, diploma, experience, address, idpost FROM post")
    posts = mycursor.fetchall()
    for job in posts:
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
        if score_val > 0.75:
            try:
                sql = "INSERT INTO job_candidate (idjob, idcandidate, score) VALUES (%s, %s,%s) ON DUPLICATE KEY UPDATE score = VALUES(score);"
                mycursor.execute(sql, (job[9], candidate[9], score_val))
                # mydb.commit()
                conn.commit()
            except:
                print("Fail Insert!")


def initValueByJob():
    # mycursor = mydb.cursor()
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(
        "SELECT title, idcareer, salary, sex, category, position, diploma, experience, address, idpost FROM post")
    jobs = mycursor.fetchall()
    for job in jobs:
        initJobVsCandidate(job)
        # pprint(job)


# initValueByJob()

def initValueByCandidate():
    # mycursor = mydb.cursor()
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute(
        "SELECT title, career, salary, sex, category, position, diploma, experience, address, idstudent FROM student")
    candidates = mycursor.fetchall()
    for candidate in candidates:
        initCandidateVsPost(candidate)

# initValueByCandidate()
