# -*- coding:utf-8 -*-
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import redisUtil
import checkCode

# 保存题库
def init_answer():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')
    browser = webdriver.Chrome(executable_path='./driver/chromedriver.exe',
                               chrome_options=chrome_options)
    # 访问登录页面
    browser.get(url)

    time.sleep(1)

    # 题目数
    count = get_question_count(browser)

    click_start_exam(browser)

    time.sleep(1)
    # 交卷
    commit_answer(browser)

    # 确认提交
    confirm_commit_answer(browser)

    # 继续交卷
    confirm_commit_next_answer(browser)

    # 添加错题
    add_error_question(browser, count)


def get_question_count(browser):
    question_count = browser.find_element_by_css_selector("[class='info-value question-counts']")
    print(question_count.text)
    count = int(question_count.text)
    return count


def click_start_exam(browser):
    start_btn = browser.find_element_by_id("exam-btn-wrapper")
    print(start_btn.text)
    start_btn.click()
    param_know = (By.CLASS_NAME, "modal-alert-footer")
    windows = WebDriverWait(browser, 20).until(EC.visibility_of_element_located(param_know))
    windows.click()


def confirm_commit_next_answer(browser):
    wait_confirm_commit_next = (By.CLASS_NAME, "zn-modal-confirm-footer")
    confirm_commit_div_next = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located(wait_confirm_commit_next))
    confirm_commit_next = confirm_commit_div_next.find_element_by_css_selector(
        "[class='btn confirm-cancel zn-btn-empty']")
    confirm_commit_next.click()


def confirm_commit_continue_answer(browser):
    wait_confirm_commit_next = (By.CLASS_NAME, "zn-modal-confirm-footer")
    confirm_commit_div_next = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located(wait_confirm_commit_next))
    confirm_commit_next = confirm_commit_div_next.find_element_by_css_selector(
        "[class='btn confirm-ok zn-btn-default']")
    confirm_commit_next.click()


def confirm_commit_answer(browser):
    wait_confirm_commit = (By.CLASS_NAME, "zn-modal-answer-sheet-footer")
    confirm_commit_div = WebDriverWait(browser, 10).until(EC.visibility_of_element_located(wait_confirm_commit))
    confirm_commit = confirm_commit_div.find_element_by_css_selector("[class='btn submitExam zn-btn-default']")
    confirm_commit.click()


def commit_answer(browser):
    commit = browser.find_element_by_css_selector("[class='btn submit-btn zn-btn-default']")
    print(commit.text)
    commit.click()


# 添加错误题目答案
def add_error_question(browser, count):
    # 查看错题
    wait_query_error_question = (By.CLASS_NAME, "error-bank")
    query_error_question = WebDriverWait(browser, 10).until(EC.visibility_of_element_located(wait_query_error_question))
    query_error_question.click()
    for i in range(count):

        num, question = get_question(browser)

        # 正确答案
        wait_correct_answer = (By.CLASS_NAME, "correct-answer")
        correct_answer = WebDriverWait(browser, 10).until(EC.visibility_of_element_located(wait_correct_answer))
        print(u"正确答案", correct_answer.text)

        r_conn = redisUtil.get_connection()
        r_conn.setnx(key_pref + question, correct_answer.text)

        # 下一题
        wait_next_question_div = (By.CLASS_NAME, "body-footer")
        next_question_div = WebDriverWait(browser, 10).until(EC.visibility_of_element_located(wait_next_question_div))
        next_question = None
        next_question_button = next_question_div.find_elements_by_xpath('button')
        count_button_len = len(next_question_button)
        if count_button_len == 1:
            next_question = next_question_button[0]
        elif count_button_len == 2:
            next_question = next_question_button[1]
        # try:
        #     next_question = next_question_div.find_element_by_css_selector("[class='btn next-btn zn-btn-default']")
        # except Exception as e:
        #     next_question = next_question_div.find_element_by_css_selector("[class='btn next-btn zn-btn-default zn-btn-default-hover zn-btn-default-active']");
        if i < count - 1:
            next_question.click()

        time.sleep(1)


def get_question(browser):
    # 问题
    wait_question = (By.CLASS_NAME, "question-title")
    question = WebDriverWait(browser, 5).until(EC.visibility_of_element_located(wait_question))
    question_str = question.text.split('.', 1)
    print(question_str[0], question_str[1])
    return question_str[0], question_str[1]


def start_exam(browser):
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--start-maximized')
    # browser = webdriver.Chrome(executable_path='./driver/chromedriver.exe',
    #                            chrome_options=chrome_options)
    # # 访问登录页面
    # browser.get(url)

    # 题目数
    count = get_question_count(browser)

    # 开始考试
    click_start_exam(browser)

    r_conn = redisUtil.get_connection()

    for i in range(count):

        # 问题
        num, question = get_question(browser)
        answer_map = r_conn.get(key_pref + question)

        wait_question_type = (By.CLASS_NAME, "question-type")
        # 问题类型
        question_type = WebDriverWait(browser, 5).until(EC.visibility_of_element_located(wait_question_type))
        print(question_type.text)

        answer_ul = browser.find_element_by_class_name("answers")
        answer_li = answer_ul.find_elements_by_xpath('li')

        match = False
        for li in answer_li:
            key = li.find_element_by_class_name("answer-key")
            value = li.find_element_by_class_name("answer-content")
            answer_key = key.text[0]
            print(answer_key, value.text)
            if question_type.text == u"多选题":
                if answer_map is None:
                    break
                for answer in answer_map:
                    if answer_key == answer:
                        match = True
                        li.click()
                        break
            else:
                if answer_key == answer_map:
                    match = True
                    li.click()
                    break
        if not match:
            answer_li[0].click()
            print("没有匹配的答案，盲选A。题号：", num)

        if question_type.text == u"多选题":
            # 下一题
            next_question = browser.find_element_by_css_selector(
                "[class='btn next-btn zn-btn-default']")
            next_question.click()

        time.sleep(1)

    # 交卷
    commit_answer(browser)
    # 确认提交
    confirm_commit_answer(browser)
    # 继续提交
    confirm_commit_continue_answer(browser)
    # 添加错题
    add_error_question(browser, count)



if __name__ == '__main__':
    url = "https://www.zhi-niao.com/znWeb/exam/detail.html?examId=1220444&mode=F&data=JTdCJTIyaXNTaW5nbGVMb2dpbiUyMiUzQSU3QiU3RCUyQyUyMm1lc3NhZ2VJbmZvJTIyJTNBJTdCJTIycHVzaE1lc3NhZ2UlMjIlM0ElMjJOJTIyJTdEJTJDJTIyb3JpZ2luJTIyJTNBJTIyaHR0cCUzQSUyRiUyRnd3dy56aGktbmlhby5jb20lMjIlMkMlMjJzZXNzaW9uSW5mbyUyMiUzQSU3QiUyMmVudGVycHJpc2VJZCUyMiUzQSUyMjI2MzZFM0U4RDA4OTM4ODRFMDU0QTAzNjlGMTkzNEVDJTIyJTJDJTIyZW50ZXJwcmlzZU5hbWUlMjIlM0ElMjIlRTYlQjclQjElRTUlOUMlQjMlRTclOTklQkUlRTYlOUUlOUMlRTUlOUIlQUQlRTUlQUUlOUUlRTQlQjglOUElRTUlOEYlOTElRTUlQjElOTUlRTYlOUMlODklRTklOTklOTAlRTUlODUlQUMlRTUlOEYlQjglMjIlMkMlMjJzaWQlMjIlM0ElMjJEMTlBRUQzNTZFRjQ0MTY2QjlGRkYzN0MyNzRGQzgwRSUyMiUyQyUyMnVzZXJJZCUyMiUzQSUyMjkxMEUwRDE5MEIxNzQ1RUJBNkRCRDY5OEIxREREQUUxJTIyJTJDJTIyYXBwSWQlMjIlM0ElMjJjb20ucGluZ2FuLnpoaW5pYW8lMjIlN0QlMkMlMjJ1c2VySW5mbyUyMiUzQSU3QiUyMmlzQWdyZWVMaXZlJTIyJTNBJTIyMSUyMiUyQyUyMmlzRnJlZSUyMiUzQSUyMjAlMjIlMkMlMjJpc1dsdCUyMiUzQSUyMjAlMjIlMkMlMjJuaWNrTmFtZSUyMiUzQSUyMiVFOSVCOCU5RiVFNSVBRSU5RDcwMTc0MCUyMiUyQyUyMnNwZWNpYWxMYWJlbCUyMiUzQW51bGwlMkMlMjJ1c2VySW1nJTIyJTNBJTIyaHR0cHMlM0ElMkYlMkZtbGVhcm4ucGluZ2FuLmNvbS5jbiUyRmxlYXJuJTJGYXBwJTJGZGVmYXVsdDIlMjIlMkMlMjJ1c2VyTmFtZSUyMiUzQSUyMiVFNSU5MCVCNCVFNiVCMiU4MSVFOCU4QSVBRSUyMiU3RCUyQyUyMnRoZW1lJTIyJTNBJTdCJTIyaXNQY09wZW4lMjIlM0FmYWxzZSUyQyUyMnBsYXRmb3JtTmFtZSUyMiUzQSUyMiVFNyU5RiVBNSVFOSVCOCU5RiVFNSVCOSVCMyVFNSU4RiVCMCUyMiUyQyUyMmluZGl2aWR1YXRpb25LZXklMjIlM0ElMjIlMjIlMkMlMjJsb2dvVXJsJTIyJTNBJTIyJTIyJTJDJTIycHJpbWFyeSUyMiUzQSUyMiUyM0ZBNTM0QSUyMiU3RCU3RA=="
    # key_pref = "20200304:"
    key_pref = "20200312:"
    # 交白卷
    # init_answer()

    # 登录
    # username = "13247123079"
    # password = "wing4117"
    username = "13724030594"
    password = "lyq05942020"
    browser = checkCode.login(username, password)
    # 进入考试页面
    checkCode.jump_my_test(browser)
    checkCode.in_test(browser)

    # 正常考试
    start_exam(browser)
    time.sleep(1000)
