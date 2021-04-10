from creds import url as URL
from creds import key as API_KEY
from activecampaign.client import Client
from threading import Thread
import time , pickle
import vram
from sel_start import init_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
driver = init_driver(headless=True)
driver.implicitly_wait(0.5)
client = Client(URL, API_KEY)

def get_all_contacts(client):
    print('started get contacts')
    def get_contacts(client,offset=vram.page*20):
        time.sleep(1)
        cnt = 0
        contacts  = client.contacts.list_all_contacts(offset=offset)['contacts']
        # print('len ',len(contacts))
        for contact in contacts:
            cnt +=1
            print(contact['id'])
            if contact['id'] not in vram.contact_ids and contact['id'] not in vram.intermediate_contact_ids:
#                print(not vram.just_started)
                if not vram.just_started:
#                    print(True)
                    vram.intermediate_bus.push({'fname':contact['firstName'],'lname':contact['lastName'],'email':contact['email'],'id':contact['id']})
                    vram.intermediate_contact_ids.append(contact['id'])
                else:
                    vram.contact_ids.append(contact['id'])
#            else:print('Already in Contacts')
        if cnt == 20:
            vram.page += 1
            get_contacts(client,offset=vram.page*20)
            vram.page -= 1
    while True:
        get_contacts(client,offset=vram.page*20)
        if vram.just_started:
            print('Captured Starting Contatcs',len(vram.contact_ids))
            with open('contact_ids.pickle','wb+') as fp:
                pickle.dump(vram.contact_ids,fp)
            vram.just_started = False
    

def get_company_names(client):
    print('started get company name')
    while True:
        time.sleep(1)
        while vram.intermediate_bus.count():
            # print(True)
            data = vram.intermediate_bus.pop()
            fields = client.contacts.retrieve_a_contact(data['id'])['fieldValues']
            for field in fields:
                # print(field['field'])
                if field['field'] == '2':
                    # print(1)
                    data['companyName'] = field['value']
                    vram.contact_bus.push(data)
                    break

    
get_contacts_thread = Thread(target=get_all_contacts,args=[client])
get_companies_thread = Thread(target=get_company_names,args=[client])
get_contacts_thread.setDaemon(True)
get_contacts_thread.start()
get_companies_thread.setDaemon(True)
get_companies_thread.start()

driver.get('https://app.marketingreports.io/clients/accounts/new')
def login(driver):
    email = 'info@marketingreports.io'
    password = 'MarketingReports2021*_*'
    em = driver.find_elements_by_class_name('email')
    for tg in em:
        try:
            tg.send_keys(email)
            break
        except:
            pass
    pswd = driver.find_elements_by_class_name('password')
    for tg in pswd:
        try:
            tg.send_keys(password)
            break
        except:
            pass
    driver.find_element_by_xpath('//*[@id="slide-ct"]/div[2]/form/button').click()

login(driver)
while True:
    def add_client(driver,data):
        try:
            elem = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH,'//a[@class="close"]')))
        except Exception as e:
            print('Cancel Buy More Not Found',e)
        driver.get('https://app.marketingreports.io/change/space/206237')
        driver.get('https://app.marketingreports.io/clients/accounts/new')
        try:
            elem = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//input[@name="companyName"]')))
        except Exception as e:
            print('In Add Client',e)

        #use explixit wait
        #add_boxes()
        driver.find_element_by_xpath('//input[@name="companyName"]').send_keys(data['companyName'])
        driver.find_element_by_xpath('//div[@class="controls"]/a[1]').click()
        #use explicit wait
        #driver.find_element_by_xpath('//div[@class="link-ct space-switch darker-bg ember-view"]').click()
    def add_user_in_client(driver,data):
        try:
            elem = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.TAG_NAME,'input')))
        except Exception as e:
            print('In Add User 1',e)
        driver.find_element_by_tag_name('input').send_keys(data['companyName'])
#reduce
        time.sleep(2)
        table = driver.find_element_by_xpath('//table[@id="clientsList"]')
        rows = table.find_elements_by_tag_name('tr')
        if len(rows) != 1:
            table = driver.find_element_by_xpath('//table[@id="clientsList"]')
            rows = table.find_elements_by_tag_name('tr')
        for i in rows[::-1]:
            if data['companyName'] in i.text:
                i.find_element_by_xpath('.//td[@class="c7 button-ct"]').click()
                time.sleep(0.1)
                break
        
        try:
            elem = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//div[@id="profile-toggler"]')))
        except Exception as e:
            print('In Add User 2',e)
            time.sleep(0.2)
        driver.find_element_by_xpath('//div[@id="profile-toggler"]').click()
        time.sleep(0.2)
        try:
            elem = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//a[@class="users"]')))
        except Exception as e:
            print('In Add User 3',e)
        driver.find_element_by_xpath('//a[@class="users"]').click()
        time.sleep(0.1)
        driver.find_element_by_xpath('//a[@class="button rippler-default theme-green size-normal plus   rippler"]').click()
        time.sleep(0.2)
        try:
            elem = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//input[@name="name"]')))
        except Exception as e:
            print('In Add User 4',e)
        driver.find_element_by_xpath('//input[@name="name"]').send_keys(data['fname'] + data['lname'])
        driver.find_element_by_xpath('//input[@name="email"]').send_keys(data['email'])
        time.sleep(0.1)
        driver.find_element_by_xpath('//a[@class="button rippler-default theme-green size-normal save   rippler"]').click()
        
    while vram.contact_bus.count() > 0:
        print(vram.contact_bus.seek())
        data = vram.contact_bus.pop()
        # if not data:continue
        for i , _id in enumerate(vram.intermediate_contact_ids):
            if _id ==  data['id']:
                add_client(driver,data)
                add_user_in_client(driver,data)
                del vram.intermediate_contact_ids[i]
                vram.contact_ids.append(data['id'])
                with open('contact_ids.pickle','wb+') as fp:
                    pickle.dump(vram.contact_ids,fp)
                print('Added Contact Successfully')
                    break
            

# response = client.contacts.list_all_contacts()
# get contacts ids
# if new id then get contact with id and get fieldValue
# print(type(response['contacts']))
# print(response['contacts'][0].keys())
# response = client.contacts.list_all_custom_fields()
# #print(response.keys())
# client.contacts.retrieve_a_contact("7")['fieldValues']