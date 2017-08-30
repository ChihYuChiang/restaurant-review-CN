from selenium import webdriver

browser = webdriver.Chrome() #replace with .Firefox(), or with the browser of your choice

url = "https://www.dianping.com/beijing/food"
browser.get(url) #navigate to the page
webdriver.ActionChains(browser).move_to_element(browser.find_element_by_css_selector('#J_nc_landmark > div.nc_item.list_landmark')).perform()

innerHTML = browser.execute_script("return document.body.innerHTML") #returns the inner HTML as a string


browser = webdriver.PhantomJS() #replace with .Firefox(), or with the browser of your choice

url = "http://www.dianping.com/shop/6088238"
browser.get(url)  #navigate to the page


webdriver.ActionChains(browser
    ).click(on_element=browser.find_element_by_css_selector('.basic-info > a.J-unfold')
    ).click(on_element=browser.find_element_by_css_selector('.recommend-name+ .J-more')
    ).perform()

innerHTML_main = browser.execute_script('return document.documentElement.outerHTML')



webdriver.ActionChains(browser
    ).click(on_element=browser.find_element_by_css_selector('.brief-info > a.icon')
    ).perform()

innerHTML_generalScore = browser.execute_script('return document.getElementById("shop-score").innerHTML')