#-*- coding:utf-8  -*-

import requests
from lxml import etree
from collections import defaultdict
from setting import *
import pdb
import re
import string
import sys 

reload(sys) 


class Gen_Spider(object):
	def __init__(self,code_file = None):
		self.__outfile__ = None
		self.__code_file__ = None
		if code_file:
			self.__code_file__ = open(code_file,'r')
		self.loop_pos = 0
		self.end_pos = 0

		if text_save_file_name:
			try:
				self.__outfile__ = open(text_save_file_name,'w')
			except IOError,e:
				print e
				exit()
		print '使用前请先阅读Readme.如果想退出请输入quit'
		self._var_dict = defaultdict(str)
		self._var_dict['_start_url'] = [start_url,""]
		self._var_dict['_next_url'] = [next_url,""]
		#self._var_dict['_text_count'] = [text_count,""]

	def _source_file_handle(self):
		#stack_loop = [,]	#循环语句执行列表 一般为["指令",循环次数]
		com = []
		is_in_loop = False
		#pdb.set_trace()
		cm_list = self.__code_file__.readlines()
		temp_cm = ''
		for cm in cm_list:
			#pdb.set_trace()
			try:
				temp_cm = cm.strip().split()[0]
			except IndexError:
				pass
			if temp_cm == 'loop':				#这两句是为了处理循环语句
				is_in_loop = True
				num = string.atoi(cm.strip().split()[1])
				com.append(num)
				continue
			elif temp_cm == 'end':
				is_in_loop = False
				com.append('end')
				continue
			com.append(cm)
		if is_in_loop:
			print('未能寻找相关loop所对应的end')
			exit()
		self.__code_file__.close()
		return com

	def program_excel(self):
		com_list = self._source_file_handle()
		count = 1
		start_loop_point = 0
		end_point = 0
		com_len = len(com_list)

		for com_point in range(com_len):
			if isinstance(com_list[com_point] ,int):
				count = com_list[com_point]
				start_loop_point = com_point + 1
				temp = start_loop_point
				while count > 1:
					#pdb.set_trace()
					if com_list[temp] == 'end':	#如果执行到end.就对temp下标进行重新赋值，以便重复执行命令
						temp = start_loop_point
						end_point = temp
						count -= 1
						continue
					self._handle_cmd(com_list[temp])
					temp += 1
					
				
				com_point = end_point+1

			self._handle_cmd(com_list[com_point])

	def _handle_cmd(self,cmd):	#指令处理
		for val in self._var_dict.keys():
			#pdb.set_trace()
			if '(%s)'%val in cmd:
				cmd = re.sub('\(%s\)'%val,self._var_dict[val][0],cmd)
				
		try:
			fiter = cmd.split()
		except AttributeError:
			return
		#print fiter
		if len(fiter) < 1:
			return None
		cmd_name = fiter[0]

		if cmd_name == 'inc':
			if len(fiter) != 3:
				print('命令格式错误:请输入inc 变量名 想添加的值')
			self.__inc_var(fiter[1],fiter[2])


		elif cmd_name == 'add':
			if len(fiter) != 3:
				print ('命令格式错误:请输入add 想创建的变量名 xpath')
				return None
			self.__add_var(fiter[1],fiter[2])
		elif cmd_name == 'set':
			if len(fiter) != 3:
				print('命令格式错误:请输入set 想创建的变量名 new_xpath')
				return None
			self.__set_var(fiter[1],fiter[2])
		elif cmd_name == 'showvar':
			if len(fiter) > 1:
				print('命令格式错误:请只输入showvar')
				return None
			self.show_var()


		elif cmd_name == 'quit':
			if len(fiter) > 1:
				print ('命令格式错误:请只输入quit')
				self.write_in_vardict
				return None
			print ('Good bye')
			exit()

		elif cmd_name == "start":
			self.start_get_spider()
		else:
			print ('无法识别指令')


	def start_get_spider(self):
		url = self._var_dict['_start_url'][0]
		var_name_list = self._var_dict.keys()

		if not url:
			print('爬取的URL是空的!')
			return None

		with requests.get(url,headers = Headers) as web:
#			print web.text.decode("GBK")
			if web.status_code != 200:
				print ('打开页面失败!')
				return None
			node_list = etree.HTML(web.text.encode('UTF-8'))
			for var in var_name_list:
				if var[0] == '_':	#将自带的变量排除
					continue
				try:
					self._var_dict[var][1] = node_list.xpath(self._var_dict[var][0])
				except etree.XPathEvalError:
					print ('变量%s的xpath语法错误!'%var)


	def show_var(self):
		for key in self._var_dict.keys():
			print ('''
			--------------------------------------
			%s:%s
			value:%s
			--------------------------------------''')%(key,self._var_dict[key][0],self._var_dict[key][1])

	def __add_var(self,var_name,xpath):
		val_name_list = self._var_dict.keys()
		if var_name not in val_name_list:
			self._var_dict[var_name] = [xpath,"None"]
		else:
			print ('该变量已经存在！如果要重新设置请用set 变量名 xpath值')

	def __set_var(self,var_name,new_xpath_value):
		val_name_list = self._var_dict.keys()

		if var_name in val_name_list:
			if new_xpath_value[0] == '$':		#判断是否为变量
				valname = new_xpath_value.strip('$')
				if valname not in val_name_list:
					print ('不存在等于号后面的变量!')
					return None
				new_xpath_value = self._var_dict[valname][0]
			self._var_dict[var_name][0] = new_xpath_value
		else:
			print('该变量不存在！！')

	def __inc_var(self,var_name,inc_value):
		val_name_list = self._var_dict.keys()

		if var_name in val_name_list:
			value = string.atoi(inc_value)
			if inc_value[0] == '$':		#判断是否为变量,我是几个月后写的这个程序。有点看不懂这里了
				valname = inc_value.strip('$')
				if valname not in val_name_list:
					print ('不存在等于号后面的变量!')
					return None
				value = string.atoi(self._var_dict[valname][0])

			temp_var_ = string.atoi(self._var_dict[var_name][0])								#取该变量值的int
			temp_var_ += value
			self._var_dict[var_name][0] = str(temp_var_)

		else:
			print('该变量不存在！！')


	def write_in_vardict(self):
		if not self.__outfile__:
			return None
		for var in self._var_dict.keys():
			if var[0] == '_':
				continue
			value = self._var_dict[var][1]
			name = var
			in_text = "%s:%s"%(name,value)
			self.__outfile__.write(in_text)
		self.__outfile__.close()

def main():
	spider = Gen_Spider()

	if len(sys.argv) > 1:
		spider = Gen_Spider(sys.argv[1])
		spider.program_excel()
		exit()

	while True:
		comd = raw_input('>>')
		spider._handle_cmd(comd)



if __name__ == '__main__':
	main()


