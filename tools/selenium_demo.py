# encoding: utf-8

from selenium import webdriver
from scrapy.selector import Selector

# 加载chrome驱动
browser = webdriver.Chrome(executable_path="./chromedriver")

# 天猫价格获取
browser.get("https://detail.tmall.com/item.htm?spm=a230r.1.14.3.yYBVG6&id=538286972599&cm_id=140105335569ed55e27b&abbucket=15&sku_properties=10004:709990523;5919063:6536025")
# print(browser.page_source)
# 使用scrapy Selector进行元素获取
t_selector = Selector(text=browser.page_source)
print(t_selector.css(".tm-price::text").extract())
browser.quit()


# 知乎模拟登陆：点击再点击
# browser.get("https://www.zhihu.com/signup?next=%2F")
# browser.find_element_by_css_selector(".SignContainer-switch span").click()
# 页面值填充
# browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input[name='username']").send_keys("username")
# browser.find_element_by_css_selector(".SignFlow-password .SignFlowInput .Input-wrapper input[name='password']").send_keys("password")
# 点击事件
# browser.find_element_by_css_selector(".Button.SignFlow-submitButton.Button--primary.Button--blue").click()


# selenium 完成微博模拟登录
# browser.get("http://weibo.com/")
# import time
# time.sleep(5) # 页面有延迟，需要等一会
# browser.find_element_by_css_selector("#loginname").send_keys("username")
# browser.find_element_by_css_selector(".info_list.password input[node-type='password'] ").send_keys("password")
# browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()


# 开源中国博客:selenium执行JavaScript
# browser.get("https://www.oschina.net/blog")
# import time
# time.sleep(5)
# for i in range(3):
#     # 浏览器页面滑动，execute_script()可以直接写js代码
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
#     time.sleep(3)


# 设置chromedriver不加载图片
# chrome_opt = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images":2}
# chrome_opt.add_experimental_option("prefs", prefs)
#
# browser = webdriver.Chrome(executable_path="./chromedriver.exe",chrome_options=chrome_opt)
# browser.get("https://www.oschina.net/blog")


# phantomjs, 无界面的浏览器， 多进程情况下phantomjs性能会下降很严重
# browser = webdriver.PhantomJS(
#     executable_path="C:/spiderDriver/phantomjs-2.1.1-windows/bin/phantomjs.exe")
# browser.get("https://detail.tmall.com/item.htm?spm=a230r.1.14.3.yYBVG6&id=538286972599&cm_id=140105335569ed55e27b&abbucket=15&sku_properties=10004:709990523;5919063:6536025")
# t_selector = Selector(text=browser.page_source)
# print (t_selector.css(".tm-price::text").extract())
# # print (browser.page_source)
# browser.quit()