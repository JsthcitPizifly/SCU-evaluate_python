import sys
import requests
from bs4 import BeautifulSoup
import importlib
import json
import time
import getpass
import urllib

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

importlib.reload(sys)
pg_url = 'http://zhjw.scu.edu.cn/student/teachingEvaluation/teachingEvaluation'
url = 'http://zhjw.scu.edu.cn/login'
img_url = 'http://zhjw.scu.edu.cn/img/captcha.jpg'
login_url = 'http://zhjw.scu.edu.cn/j_spring_security_check'
local = 'now.jpg'
def teach_evaluate(usr, psw, text):
	
	s = requests.Session()
 	# res = requests.get(url)
	rsp = s.get(img_url)
	img = rsp.content
	with open(local, 'wb') as f:
		f.write(img)
	cook = rsp.headers["Set-Cookie"][11:-8] #获取cookies 从图片处获取
	# cook = res.headers["Set-Cookie"][11:-8]
	# print(cook)
	cap = input("验证码:") # 需要手动输入验证码
	login_data = {'j_username':usr, 'j_password':psw,'j_captcha': cap, 'JSSESSIONID':cook}
	r = s.post(login_url, login_data, headers = headers)
	if r.status_code == 200:
		print("login success")
	else :
		print("login failed")
		exit(0)
	
	res = s.get(pg_url + '/search')

	r = json.loads(res.text)
	for item in r['data']:
		params_post = dict()
		get_token = dict()
		msg = list()
		if item['isEvaluated'] == '否' :
			get_token['evaluatedPeople'] = item['evaluatedPeople']
			get_token['evaluatedPeopleNumber'] = item['id']['evaluatedPeople']
			get_token['questionnaireCode'] = item['id']['questionnaireCoding']
			get_token['questionnaireName'] = item['questionnaire']['questionnaireName']
			get_token['evaluationContentNumber'] = item['id']['evaluationContentNumber']
			res = s.post(pg_url +'/evaluationPage', get_token)
			
			bsObj = BeautifulSoup(res.text, "html.parser")
			token = bsObj.find('input', attrs = {'name' : 'tokenValue'})['value']
			
			params_post['tokenValue'] = token
			params_post['questionnaireCode'] = item['id']['questionnaireCoding']
			params_post['evaluationContentNumber'] = item['id']['evaluationContentNumber']
			params_post['evaluatedPeopleNumber'] = item['id']['evaluatedPeople']
			params_post['count'] = str(0)
			for item_in in bsObj.findAll('input',{'class' :'ace'}, {'type' : 'radio'}) :
				tmpstr_in = item_in.attrs["name"]
				if tmpstr_in not in params_post.keys():
					params_post[tmpstr_in] = item_in.attrs["value"]
			params_post['zgpj'] = text
			
			# print(params_post)
			# exit(0)
			remain = 122
			while remain != 0 :
				time.sleep(1)
				print("还剩下" + str(remain) +"s可进行下一轮评教")
				remain = remain - 1
			respon = s.post(pg_url + '/evaluation', params_post, headers)
			if 'success' in respon.text :
				st = get_token['evaluatedPeople'] + ' 评教成功'
				msg.append(st)
			else :
				st = get_token['evaluatedPeople'] + ' 评教失败'
				msg.append(st)
			
	for x in range(0, len(msg)) :
		print(msg[x])
	return '评教结束'
	
usr = input("学号:")
psw = getpass.getpass("密码:")
text = input("评估内容:")
print(teach_evaluate(usr, psw, text))