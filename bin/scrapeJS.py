from selenium import webdriver

browser = webdriver.Chrome() #replace with .Firefox(), or with the browser of your choice
url = "http://example.com/login.php"
url = "https://www.dianping.com/beijing/food"
browser.get(url) #navigate to the page
webdriver.ActionChains(browser).move_to_element(browser.find_element_by_css_selector('#J_nc_landmark > div.nc_item.list_landmark')).perform()

innerHTML = browser.execute_script("return document.body.innerHTML") #returns the inner HTML as a string