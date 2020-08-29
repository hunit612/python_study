import os
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert

import urllib.request
from bs4 import BeautifulSoup
from time import sleep
import re
import configparser
import sys
from shutil import copyfile
from selenium.webdriver.chrome.options import Options

# 자동화프로그램의 설정을 로딩합니다.
class config_load:
    def __init__(self):
        try:
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.dirname(__file__), "자동화설정.ini"), encoding='utf-8')
            self.parsing_tabs = None
            self.output_directory = config["Paths"]["output_directory"]
            self.intranet_id = config["Intranet Account"]["intranet_id"]
            self.intranet_password = config["Intranet Account"]["intranet_password"]
            self.lecture_room_address = config["Lecture"]["lecture_room_address"]
            self.b2c_code = config["Lecture"]["b2c_code"]
            self.b2b_code = config["Lecture"]["b2b_code"]
            self.lecture_count = config["Lecture"]["lecture_count"]
            self.start_point = config["Lecture"]["start_point"]
            self.module_name = config["Mobile Manifest.xml"]['module_name']

            print("설정이 정상적으로 로딩되었습니다.")

        except:
            print("설정 파일을 확인해주세요.")
            sys.exit(1)

# 크롬 드라이버를 시작합니다.
class chrome_driver_load:
    def __init__(self, configurations):
        try:
            # 크롬에서 생성되는 오류, 경고를 컨솔에 뜨지 않도록 합니다.
            chrome_options = Options()
            chrome_options.add_argument("--log-level=3")

            # 인트라넷에 설정에서 지정된 아이디와 패스워드로 로그인합니다.
            self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.path.join(os.path.dirname(__file__), "chromedriver.exe"))
            self.driver.implicitly_wait(3)
            self.driver.get("http://jobworld.kr")
            self.driver.find_element_by_name("LOGINID").send_keys(configurations.intranet_id)
            self.driver.find_element_by_name("PASSWD").send_keys(configurations.intranet_password)
            self.driver.find_element_by_id("login_btn_area").click()

            try:
                # 만약에 쪽지 알림창이 뜨면 닫아버립니다.
                sleep(0.5)
                self.driver.switch_to.alert.dismiss()
                self.driver.find_element_by_partial_link_text("챔프강의").click()
            except NoAlertPresentException:
                # 쪽지가 온게 없으면 강의테스터를 실행합니다.
                self.driver.find_element_by_partial_link_text("챔프강의").click()

            # 인트라넷을 종료합니다.
            self.window_handle = self.driver.window_handles[1]
            self.driver.close()

            # 챔프스터디 강의실을 오픈합니다.
            self.driver.switch_to_window(self.window_handle)
            self.driver.get(configurations.lecture_room_address)

            # 강의실행 링크를 할당받습니다.
            self.lecture_links = self.get_lecture_link_list()

            # 각 차시의 제목을 저장합니다.
            self.lecture_title_list = self.get_lecture_title()

            print("크롬드라이버가 정상적으로 로딩되었습니다.")

        except Exception as Error:
            print("크롬드라이버 초기 세팅에 실패햐였습니다.")
            print("에러코드를 API 문서에서 확인 후 조치해주세요. " + str(Error))
            sys.exit(1)

    # 강의실에서 각 차시의 제목을 가져오도록 하는 프로그램입니다.
    # 강의 제목의 리스트를 반환합니다.
    def get_lecture_title(self):
        # 여기서 페이시 소스를 가져옵니다.
        page_source = BeautifulSoup(self.return_page_source(), 'html.parser')
        lecture_title_list = list()

        for sbj_list in page_source.find_all("td", class_="sbj"):
            lecture_title_list.append(sbj_list.a.string.strip())

        return lecture_title_list

    def get_lecture_link_list(self):
        lecture_links = self.driver.find_elements_by_css_selector("td.sbj")
        for idx in range(len(lecture_links)):
            lecture_links[idx] = lecture_links[idx].find_element_by_tag_name("a").get_attribute("onclick")

        return lecture_links

    def open_lecture(self, lecture_count):
        self.window_handle = self.driver.window_handles[0]
        self.driver.execute_script(self.lecture_links[lecture_count - 1])
        self.driver.switch_to_window(self.driver.window_handles[1])
        sleep(3)
        self.driver.execute_script("goLesson()")
        sleep(1.5)

    def close_lecture(self):
        self.driver.close()
        self.driver.switch_to_window(self.window_handle)

    def mark_question(self):
        self.driver.execute_script("goResultPage()")
        # 페이지가 로딩될 때까지 기다립니다.
        sleep(3.5)

    def show_model_answer(self): # 모범답안을 보여주도록 합니다.
        self.driver.execute_script("""$("a.btn_1").click()""")
        sleep(1.5)

    def return_page_source(self):
        # 페이지 소스를 돌려줍니다.
        return self.driver.page_source

    def move_to_specific_tab(self, tab_name):
        try:
            self.driver.find_element_by_partial_link_text(tab_name).click()
            sleep(2)
        except NoSuchElementException:
            print("웹페이지에서 해당 탭을 찾을 수 없습니다.\n설정파일의 parsing_tabs을 알맞게 설정해주세요.")
            sys.exit(2)

    def move_to_specific_step(self, step_location):
        self.driver.find_element_by_class_name("step"+str(step_location)).click()
        sleep(3)

    def move_to_next_tab(self, i):
        self.driver.find_element_by_css_selector("nav[class='gnb']").find_elements_by_tag_name("a")[i].click()
        sleep(3)

    def close_audio_check_page(self):
        self.driver.find_element_by_css_selector("span[class='btnIn']").click()
        #self.driver.find_element_by_css_selector("a[class='btn_1']").click()

# 말하기 강의의 경우, 오디오 녹음을 사용하는 페이지를 지원하지 않습니다.
# 여기서 지원되는 페이지의 리스트를 반환합니다.
# 파일로 지원하지 않는 페이지의 로그를 남깁니다.
def check_unsupported_page_type(configurations, chrome_driver, lecture_count):
    #open file to save result which page is not supported type
    output_path = configurations.output_directory + '/' + configurations.b2b_code + '/' + configurations.b2c_code + '_unsupported_page.txt'
    with open(output_path, 'a+', encoding='utf-8') as file:
        chrome_driver.open_lecture(lecture_count)
        tab_length = len(chrome_driver.driver.find_element_by_css_selector("nav[class='gnb'] ul").find_elements_by_tag_name("a"))
        file.write("Lecture " + str(lecture_count) + ' has ' + str(tab_length) + ' tabs\n')
        supported_tabs = list()

        for idx in range(0, tab_length):

            # 다음 탭으로 이동합니다.
            if idx != 0:
                chrome_driver.move_to_next_tab(idx)

            # 페이지 소스를 가져옵니다.
            page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')

            # 만약에 오디오 작동테스트 페이지가 나온 경우
            if page_source.find("section", class_="mediatest_wrap") is not None:
                chrome_driver.close_audio_check_page()
                page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')
                file.write("Tab " + page_source.find("a", class_='on').string + ' in lecture '+ str(lecture_count) + ' is not supported' + '\n')
            elif page_source.find("a", class_="btn_record") is not None:
                page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')
                file.write("Tab " + page_source.find("a", class_='on').string + ' in lecture '+ str(lecture_count) + ' is not supported' + '\n')
            else:
                supported_tabs.append(page_source.find("a", class_='on').string)

        file.write('\n\n')

    chrome_driver.close_lecture()
    return supported_tabs

# CMS 상에 업로드 하는 목차를 생성하는 함수입니다.
def cms_excel_text(configurations, lecture_title_list, lecture_count):
    # 파일을 생성합니다
    with open("{}/{}/목차.txt".format(configurations.output_directory, configurations.b2b_code), 'a+', encoding='utf-8') as excel_text:
        excel_text.write("{}\t{}\t1001.html\tmanifest.xml\t{}\n".format(configurations.module_name, lecture_title_list[lecture_count-1], len(configurations.parsing_tabs) + 1))

def crawl_and_save(configurations, chrome_driver):

    # 강의페이지 내비게이션 태그를 만듭니다.
    def div_gnb_creator(tab_location):
        div_gnb = """<div class="gnb"><ul>"""
        for i in range(0, len(configurations.parsing_tabs)):
            div_gnb = div_gnb + """<li><a id="menu5982" href="javascript:hackersPage(""" + str(i + 2) + """);"  >""" + configurations.parsing_tabs[i] + """</a></li>"""
        div_gnb = div_gnb + """</ul></div>"""
        div_gnb = BeautifulSoup(div_gnb, 'html.parser').find("div")
        div_gnb.find_all('a')[int(tab_location) - 1]['class'] = 'on'
        return div_gnb

    def create_intro(lecture_count):
        copyfile(os.path.join(os.path.dirname(__file__), "template/인트로.html"), configurations.output_directory + '/' + configurations.b2b_code + '/docs/' + "%02d" % (lecture_count) + '/' + "1001.html")
        print("Filename: " + configurations.output_directory + '/' + configurations.b2b_code + "/docs/" + "%02d" % (lecture_count) + '/1001.html')

    def create_folder(lecture_count):
        #os_path = configurations.output_directory + '/' + configurations.b2b_code + '/docs/' + "%02d" % (lecture_count - int(configurations.start_point) + 1) + '/'
        print(str(lecture_count))
        os_path = configurations.output_directory + '/' + configurations.b2b_code + '/docs/' + "%02d" % (lecture_count) + '/'
        if not os.path.exists(os.path.dirname(os_path)):
            os.makedirs(os.path.dirname(os_path))

    def save_target(target_source, lecture_count, tab_count, step_count=1, is_drag_and_drop=0):
        if step_count == 1 and is_drag_and_drop != 1: # 1번째 Step 를 저장할 경우
            file_name = configurations.output_directory + '/' + configurations.b2b_code + '/docs/' + "%02d" % (lecture_count) + '/' + "100" + str(tab_count + 1) + ".html"
        elif step_count== 1 and is_drag_and_drop == 1: # 1번째 탭인 동시에 드래그 & 드랍인 경우
            file_name = configurations.output_directory + '/' + configurations.b2b_code + '/docs/' + "%02d" % (lecture_count) + '/' + "100" + str(tab_count + 1) + "_r.html"
        elif not is_drag_and_drop: # 드래그 & 드랍이 아닐 경우에 실행합니다.
            file_name = configurations.output_directory + '/' + configurations.b2b_code + '/docs/' + "%02d" % (lecture_count) + '/' + "100" + str(tab_count + 1) + "_s" + str(step_count)  + ".html"
        elif is_drag_and_drop: # 드래그 & 드랍일 경우 파일명을 조정합니다.
            file_name = configurations.output_directory + '/' + configurations.b2b_code + '/docs/' + "%02d" % (lecture_count) + '/' + "100" + str(tab_count + 1) + "_s" + str(step_count)  + "_r.html"

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(target_source.encode(encoding='utf-8', formatter='html').decode("utf-8"))

        print("Filename: " + file_name)

    def lecture(page_source, lecture_count, tab_count):
        target_source = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "template/동영상.html"), encoding="utf-8"), 'html.parser')

        # div_gnb 를 교체하도록 합니다.
        div_gnb = div_gnb_creator(tab_count)
        target_source.find("div", class_="gnb").replace_with(div_gnb)

        # topTitle_M 을 바꿉니다.
        topTitle_M = page_source.find("hgroup", id="topTitle_M")
        if topTitle_M is not None:
            target_source.find("div", id="topTitle_M").replace_with(topTitle_M)

        # 동영상 차시 조정
        target_source.find('input', id="m_idx")['value'] = lecture_count

        # 동영상 B2C 코드 조정
        target_source.find("input", id="b2c")['value'] = configurations.b2c_code

        # 동영상 B2B 코드 조정
        target_source.find("input", id="b2b")['value'] = configurations.b2b_code

        # 결과물을 저장합니다
        save_target(target_source, lecture_count, tab_count)

    def voca(lecture_count, tab_location, page_source):
        # 탬플릿을 로딩하고 히든값을 알맞게 조정합니다.
        target_source = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "template/voca.html"), encoding="utf-8"), 'html.parser')
        target_source.find("input", id="index")['value'] = lecture_count

        # div_gnb 를 알맞게 수정합니다.
        div_gnb = div_gnb_creator(tab_location)
        target_source.find('div', class_='gnb').replace_with(div_gnb)

        # 결과물을 저장합니다.
        save_target(target_source, lecture_count, tab_location)

    # 좌, 우 이동 버튼, 스텝 버튼을 알맞게 설정합니다.
    def set_step_and_navigation(target_source, page_source, step_location, tab_location, step_amount):

        #좌, 우 이동 버튼 설정
        if page_source.find("a", class_="nextpage") is not None:
            target_source.find("a", class_="nextpage")['style'] = "display:block;";
            target_source.find("a", class_="nextpage")['href'] = "./100" + str(int(tab_location) + 1) +"_s" + str(step_location + 1) + ".html"
        if page_source.find("a", class_="prevpage") is not None:
            target_source.find("a", class_="prevpage")['style'] = "display:block;";
            if step_location is 2:
                target_source.find('a', class_="prevpage")['href'] = "./100"+ str(int(tab_location) + 1) +".html"
            else:
                target_source.find('a', class_="prevpage")['href'] = "./100" + str(int(tab_location) + 1) + "_s" + str(step_location - 1) + ".html"

        #스텝 버튼 설정
        for idx in range(1, step_amount + 1):
            #스타일 수정.
            if step_amount == 1:
                target_source.find("ul", class_="tab_step").find_all('a')[idx - 1]['style'] = "display:none;"
            else:
                target_source.find("ul", class_="tab_step").find_all('a')[idx - 1]['style'] = "display:block;"

            #href 링크 수정
            if idx == 1:
                target_source.find("ul", class_="tab_step").find_all('a')[idx - 1]['href'] = "./100" + str(int(tab_location) + 1) + ".html"
            else:
                target_source.find("ul", class_='tab_step').find_all('a')[idx - 1]['href'] = "./100" + str(int(tab_location) + 1) + "_s" + str(idx) + ".html"
        #on 클래스를 부여.
        target_source.find("ul", class_="tab_step").find_all('a')[step_location - 1]['class'] = "on"

        return target_source

    def problem_solving(page_source, lecture_count, tab_location):

        # 스탭이 몇개나 있는지 체크합니다.
        step_amount = len(page_source.find_all("li", class_=re.compile("step")))
        if step_amount == 0:
            step_amount = 1

        for current_step in range(1, step_amount + 1):
            target_source = None;
            # 객관식일 경우
            if page_source.find("article", class_=re.compile("opt_")) is not None:

                target_source = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "template/객관식.html"), encoding="utf-8"), 'html.parser')

                # 객관식일 경우 채점을 해버립니다
                chrome_driver.mark_question()

                # 자바스크립트 코드를 실행하여 답안 마킹을 숨깁니다.
                chrome_driver.driver.execute_script("""

                //만능스크립트 추가
                // 페이지가 로딩되면 답안, 마킹 숨기기
                function initializeExam(){

                    //가위 표시 숨기기
                    mark_fields = document.getElementsByClassName("mark_incorrect")
                    for(var i = 0; i < mark_fields.length; i++)
                    {
                        mark_fields[i].style.display = "none";
                    }

                    //라디오 활성화 하기
                    labels = document.getElementsByTagName("label");
                    for (var i = 0;i < labels.length; i++)
                    {
                        //라디오 버튼 활성화
                        labels[i].getElementsByTagName("input")[0].disabled = false;
                        labels[i].getElementsByTagName("input")[0].checked = false;
                    }

                    //오답 스타일 숨기기
                    //숨기고 동시에 아이디 추가
                    //채점 후에 클래스를 돌려주기 위해서
                    incorrect_class = document.getElementsByClassName("incorrect")
                    incorrect_class_length = incorrect_class.length;
                    for (var i = 0;i < incorrect_class_length ; i++)
                    {
                        incorrect_class[0].setAttribute("id", "incorrect_class_" + i);
                        incorrect_class[0].setAttribute("class", "")
                    }

                    //정답 표시 숨기기 (빨간색 정답박스)
                    ico_correct_class = document.getElementsByClassName("ico_correct")
                    for(var i = 0; i < ico_correct_class.length; i++)
                    {
                        ico_correct_class[i].style.display = "none";
                    }

                    //답안 표 숨기기
                    for (var i = 0;i < document.getElementsByTagName('table').length ; i++)
                    {
                        document.getElementsByTagName("table")[i].style.display = 'none';
                    }

                    //버튼 스크립트 변경
                    document.getElementsByClassName("btn_1")[0].innerHTML = "정답확인";
                    document.getElementsByClassName("btn_1")[0].href = "javascript:checkAnswer()";

                    $("article.box_example").find('table').css("display", "block");

                }

                initializeExam();

                """)

                sleep(2)

            # 주관식일 경우
            elif page_source.find("span", class_="field") is not None:
                target_source = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "template/주관식.html"), encoding="utf-8"), 'html.parser')
            # 서술형일 경우
            elif page_source.find("textarea", type="text") is not None:
                target_source = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "template/모범답안.html"), encoding="utf-8"), 'html.parser')
            # 사진 하나 나오는 문제일 경우
            elif page_source.find("p", class_="img") is not None:
                target_source = BeautifulSoup(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "template/주관식.html"), encoding="utf-8"), 'html.parser')
            # 드래그 & 드랍 방식일 경우
            elif page_source.find("div", class_="drag_wrap") is not None:
                target_source = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "template/드래그드랍.html"), encoding="utf-8"), 'html.parser')
            # 선 그리기 방식일 경우
            elif page_source.find("div", class_="drag_wrap5") is not None:
                target_source = BeautifulSoup(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "template/선그리기.html"), encoding="utf-8"), 'html.parser')

            # 만약에 오디오 작동테스트 페이지가 나온 경우
            elif page_source.find("section", class_="mediatest_wrap") is not None:
                chrome_driver.close_audio_check_page()
                page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')
                file.write("Tab " + page_source.find("a", class_='on').string + ' in lecture '+ str(lecture_count) + ' is not supported' + '\n')
            elif page_source.find("a", class_="btn_record") is not None:
                page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')
                file.write("Tab " + page_source.find("a", class_='on').string + ' in lecture '+ str(lecture_count) + ' is not supported' + '\n')

            # page_source 를 다시 로딩하도록 합니다.
            page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')

            # Step, 그리고 좌/우 내비게이션 등을 알맞게 설정합니다.
            target_source = set_step_and_navigation(target_source, page_source, current_step, tab_location, step_amount)

            # tit을 변경하도록 합니다.
            tit = page_source.find("strong", class_="tit").string
            if tit is not None:
                target_source.find("strong", class_="tit").string.replace_with(tit)

        # 만약에 오디오 링크를 자바스크립트에서 처리하는 경우
            # 버튼을 클릭하고 jPlayer의 오디오 링크를 알아내어
            # 버튼 아래에 히든태그로 오디오 경로를 넣어줍니다.
            #           if page_source.find("input", type="radio") is not None:
            if page_source.find("a", class_='btn_spk') is not None:
                if page_source.find("a", class_='btn_spk').input is None:
                    # 자바스크립트를 이용하여 오디오 링크를 얻어서 오디오 값을 넣어줍니다.
                    # 오디오 링크를 추출하여 Javascript 에 변수로 저장합니다.
                    # 그 후, 오디오 링크를 a.btn_spk 밑에 히든값으로 넣어줍니다.

                    tmp = 0
                    tmp_eng = 0
                    tmp_kor = 0
                    tmp_else = 0
                    #while tmp < len(page_source.find_all("a", class_="btn_spk")):
                    for select_a in page_source.find_all("a", class_="btn_spk"):

                        print("tmp : "+str(tmp)+" tmp_eng : "+str(tmp_eng)+" tmp_kor : "+str(tmp_kor)+" tmp_else : "+str(tmp_else))

                        if "eng" in str(select_a) :
                            chrome_driver.driver.execute_script("examPlaying1("+str(tmp_eng)+")")
                            chrome_driver.driver.execute_script("""var audio_url = $('#exam_player1').data().jPlayer.status.media.mp3;$('a.btn_spk:eq("""+str(tmp)+""")').attr('name','make_name"""+str(tmp)+"""'); $("a.eng:eq("""+str(tmp_eng)+""")").append("<input name='make_audio"""+str(tmp)+"""' type='hidden' value='" + audio_url + "'>")""")
                            tmp_eng = tmp_eng+1
                            tmp_else = tmp_else+1

                        elif "kor" in str(select_a) :
                            chrome_driver.driver.execute_script("examPlaying2("+str(tmp_kor)+")")
                            chrome_driver.driver.execute_script("""var audio_url = $('#exam_player2').data().jPlayer.status.media.mp3;$('a.btn_spk:eq("""+str(tmp)+""")').attr('name','make_name"""+str(tmp)+"""'); $("a.kor:eq("""+str(tmp_kor)+""")").append("<input name='make_audio"""+str(tmp)+"""' type='hidden' value='" + audio_url + "'>")""")
                            tmp_kor = tmp_kor+1
                            tmp_else = tmp_else+1

                        else :
                            if page_source.find("div",id="answer_player") is not None:
                                print(1)
                            elif page_source.find("div",id="exam_player")  is not None:
                                print(2)

                            if page_source.find("div",id="answer_player") is not None:

                                chrome_driver.driver.execute_script("answerPlaying("+str(tmp_else)+")")
                                chrome_driver.driver.execute_script("""var audio_url = $('#answer_player').data().jPlayer.status.media.mp3;$('a.btn_spk:eq("""+str(tmp)+""")').attr('name','make_name"""+str(tmp)+"""'); $("a.btn_spk:eq("""+str(tmp_else)+""")").append("<input name='make_audio"""+str(tmp)+"""' type='hidden' value='" + audio_url + "'>")""")
                                tmp_else = tmp_else+1

                            elif page_source.find("div", id="exam_player") is not None:

                                chrome_driver.driver.execute_script("examPlaying("+str(tmp_else)+")")
                                chrome_driver.driver.execute_script("""var audio_url = $('#exam_player').data().jPlayer.status.media.mp3;$('a.btn_spk:eq("""+str(tmp)+""")').attr('name','make_name"""+str(tmp)+"""'); $("a.btn_spk:eq("""+str(tmp_else)+""")").append("<input name='make_audio"""+str(tmp)+"""' type='hidden' value='" + audio_url + "'>")""")
                                tmp_else = tmp_else+1


                        sleep(3.5)
                        # 오디오 링크를 가져옵니다.
                        audio_url = chrome_driver.driver.find_element_by_name("make_audio"+str(tmp)).get_attribute('value')
                        new_tag = page_source.new_tag("input", type="hidden", value=audio_url)
                        page_source.find_all("a", class_='btn_spk')[tmp].append(new_tag)
                        tmp = tmp+1



            # cont_full 을 변경하도록 합니다.
            cont_full = page_source.find("div", class_="cont_full")
            target_source.find("div", class_="cont_full").replace_with(cont_full)

            # hgroup 을 변경하도록 합니다.
            hgroup = page_source.find("hgroup")
            if hgroup is not None:
                target_source.find("div", id="topTitle_C").replace_with(hgroup)

            # div_gnb을 설정하도록 합니다.
            div_gnb = div_gnb_creator(tab_location)
            target_source.find("div", class_="gnb").replace_with(div_gnb)

            # 오디오 링크를 로컬로 바꿉니다.
            for link_url in target_source.select("input[value^='http://class.champstudy.com']"):
                new_url = "../common/lec_data/Lesson" + link_url['value'].split('Lesson')[1]
                link_url['value'] = new_url
            for link_url in target_source.select("audio[src^='http://class.champstudy.com']"):
                new_url = "../common/lec_data/Lesson" + link_url['src'].split('Lesson')[1]
                link_url['src'] = new_url

            # 이미지 링크를 로컬로 바꾸고 저장합니다.
            for image_url in target_source.select("img[src^='http://class.champstudy.com']"):
                # Contents 폴더를 생성합니다.
                contents_path = configurations.output_directory + '/' + configurations.b2b_code + '/docs/contents/'
                if not os.path.exists(os.path.dirname(contents_path)):
                    os.makedirs(os.path.dirname(contents_path))

                # 이미지를 로컬로 저장합니다.
                urllib.request.urlretrieve(image_url['src'], contents_path + image_url['src'].split("contents/")[1])

                # 이미지 링크를 로컬로 바꿉니다.
                new_url = "../contents/" + image_url['src'].split("contents/")[1]
                image_url['src'] = new_url

            # 드래그 & 드랍 형태의 문제일 경우 정답을 저장하도록 합니다.
            if target_source.find("div", class_="drag_wrap") is not None:
                # 모범답안을 로딩합니다.
                chrome_driver.show_model_answer()
                # 페이지 소스를 다시 로딩합니다.
                page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')
                # ul_items 를 알맞게 저장하도록 합니다.
                li_tag_elements = page_source.find("ul", class_="items").find_all('li')
                ul_items = str()
                for li_tag_element in li_tag_elements:
                    ul_items = ul_items + li_tag_element.encode('utf-8', formatter='html').decode("utf-8")
                # 드래그 & 드랍의 답안을 저장하도록 합니다.
                save_target(BeautifulSoup(ul_items, 'html.parser'), lecture_count, tab_count, step_count=current_step, is_drag_and_drop=1)

            # target_source 를 저장하도록 합니다.
            save_target(target_source, lecture_count, tab_location, step_count=current_step)

            # 다음 스탭으로 이동하도록 합니다. Step2, step2, etc....
            if current_step != step_amount:
                chrome_driver.move_to_specific_step(current_step + 1)

            # page_source 를 다시 로딩합니다...
            page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')

    # today_goal 또는 tdoay's point 를 크롤링하고 저장하도록 합니다.
    def today_goal_or_point(page_source, lecture_count, current_tab):

        #탬플릿을 로딩하도록 합니다.
        target_source = BeautifulSoup(open(os.path.join(os.path.dirname(__file__), "template/핵심정리.html"), encoding="utf-8"), 'html.parser')

        #div_gnb 를 알맞게 변경합니다.
        div_gnb = div_gnb_creator(current_tab)
        target_source.find("div", class_="gnb").replace_with(div_gnb)

        # hgroup 을 변경합니다.
        hgroup = page_source.find("hgroup")
        target_source.find("hgroup").replace_with(hgroup)

        # tit1을 변경합니다.
        tit1 = page_source.find("h1", class_="tit1").string
        if tit1 is not None:
            target_source.find("h1", class_="tit1").string.replace_with(tit1)

        # 오른쪽 아래의 < > 버튼을 알맞게 변경합니다.
        curr = page_source.find("span", class_="curr")
        target_source.find("span", class_="curr").replace_with(curr)

        # mCSB_container 를 변경합니다.
        mCSB_container = page_source.find("div", class_="mCSB_container")
        target_source.find("article").div.div.div.div.replace_with(mCSB_container)

        # audio_url 을 알맞게 변경합니다.
        # 학습목표에는 audio_url이 존재하지 않으므로 웹에서 audio_url이 존재하는지부터 먼저 확인합니다.
        audio_url = page_source.find(value=re.compile("http://class.champstudy.com/upDATA/"))
        if audio_url is not None:
            audio_url = audio_url['value']
        if audio_url is not None:
            audio_url = "../common/lec_data/Lesson" + audio_url.split("Lesson")[1]
            target_source.find(id="ques_url_1502")['value'] = audio_url
        else:
            target_source.find("div", class_="audioInner")['style'] = "display:none;"
            target_source.find(id="ques_url_1502")['value'] = ""

        # 완성된 강의를 저장합니다.
        save_target(target_source, lecture_count, tab_count=current_tab)

    # 여기서 강의를 열고 닫거나 탬플릿을 저장하도록 합니다.
    #for lecture_count in range(int(configurations.start_point), int(configurations.lecture_count) + 1):
    for lecture_count in range(int(configurations.start_point), int(configurations.start_point) + int(configurations.lecture_count)):

        create_folder(lecture_count)

        # 지원되지 않는 페이지를 찾습니다.
        configurations.parsing_tabs = check_unsupported_page_type(configurations, chrome_driver, lecture_count)

        # CMS 업로드할때 필요한 목차를 만들도록 합니다.
        cms_excel_text(configurations, chrome_driver.lecture_title_list, lecture_count)

        create_intro(lecture_count)
        chrome_driver.open_lecture(lecture_count)

        for tab_count in range(1, len(configurations.parsing_tabs) + 1):

            page_source = BeautifulSoup(chrome_driver.return_page_source(), 'html.parser')

            # 페이지의 종류를 여기서 판단합니다.
            # 문제풀이의 경우 (주관식, 서술형, 객관식. 드래그&드랍 등)
            if page_source.find("div", class_="cont_full") is not None:
                problem_solving(page_source, lecture_count, tab_count)
            # 오늘의목표, 핵심정리일 경우
            elif page_source.find("h1", class_="tit1") is not None:
                today_goal_or_point(page_source, lecture_count, tab_count)
            # 강의창일 경우
            elif page_source.find("div", class_="multimedia") is not None:
                lecture(page_source, lecture_count, tab_count)
            # 보카일 경우
            elif page_source.find("a", class_="btn_study") is not None:
                voca(lecture_count, tab_count, page_source)

            if tab_count != len(configurations.parsing_tabs):
                chrome_driver.move_to_specific_tab(configurations.parsing_tabs[tab_count])

        print("Lecture " + str(lecture_count) + " crawling is done")
        chrome_driver.close_lecture()

def main():
    configurations = config_load()
    chrome_driver = chrome_driver_load(configurations)

    #크롤링을 여기서 시작합니다.
    input("크롬드라이버가 로딩되었습니다. 크롤링을 시작하려면 Enter 키로 시작하세요.")
    #try:
    crawl_and_save(configurations, chrome_driver)
    #except UnexpectedAlertPresentException:
    #   print("Unexpected alert closed")
        #chrome_driver.driver.switch_to.alert.dismiss()

#   chrome_driver.driver.quit()

    input("프로그램이 정상 종료되었습니다. Enter 키로 종료하세요.")

if __name__ == "__main__":
    main()