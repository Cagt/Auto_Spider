set _start_url http://blog.csdn.net/tao_627/article/details/42297443
add test //*[@id="article_details"]/div[11]/div/div[2]/ul[1]/li[1]/a/text()
set _start_url http://tieba.baidu.com/p/5295629957?red_tag=f2962311457
add test2 //img[@class="BDE_Image"]/@src[1]
add count 1
start

loop 4
	set _start_url http://tieba.baidu.com/p/5295629957?red_tag=f296231145(count)
	start
	showvar
	inc count 1
	
end
