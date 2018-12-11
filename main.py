import sys
import requests
from bs4 import BeautifulSoup
import importlib
import json
import time

importlib.reload(sys)
pg_url = 'http://zhjw.scu.edu.cn/student/teachingEvaluation/teachingEvaluation'

def teach_evaluate(usr, psw, text):
	s = requests.Session()
	res = requests.get(url)
	
	cook = res.headers["Set-Cookie"][11:-8]
	
	login_data = {'j_username':usr, 'j_password':psw,'j_captcha1': "error", 'JSSESSIONID':cook}
	r = s.post('http://zhjw.scu.edu.cn/j_spring_security_check', login_data)
	
	if r.status_code == 200:
		print("login sucess")
	res = s.get(pg_url + '/search')
	r = json.loads(res.text)
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
	
	for item in r['data']:
		params_post = dict()
		get_token = dict()
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
			for item_in in bsObj.findAll('input',{'class' :'ace'}, {'type' : 'radio'}) :
				tmpstr_in = item_in.attrs["name"]
				if tmpstr_in not in params_post.keys():
					params_post[tmpstr_in] = item_in.attrs["value"]
			params_post['zgpj'] = text
			respon = s.post(pg_url + '/evaluation', params_post, headers)	
			if 'fail' in respon.text :
				print(get_token['evaluatedPeople'] + ' 评教失败')
			if 'sucess' in respon.text :
				print(get_token['evaluatedPeople'] +  ' 评教成功')
			
	return '评教结束'
	
usr = input("学号:")
psw = input("密码:")
text = input("评估内容(请用英文):")
print(teach_evaluate(usr, psw, text))
