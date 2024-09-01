from bs4 import BeautifulSoup
import datetime
import time
import random
from selenium import webdriver
from paho.mqtt import client as mqtt_client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-search-engine-choice-screen')

url = "https://gispx.sofiyskavoda.bg/WebApp.InfoCenter/"
broker = 'MQTT BROKER IP'
port = PORT
username = 'USERNAME'
password = 'PASSWORD'
client_id = f'mqttsofiyskavodarepairs'
topic0 = "homeassistant/sensor/sofiyskavodarepairs/availability"
topic1 = "homeassistant/sensor/sofiyskavodarepairs/location"
topic2 = "homeassistant/sensor/sofiyskavodarepairs/typeofevent"
topic3 = "homeassistant/sensor/sofiyskavodarepairs/description"
topic4 = "homeassistant/sensor/sofiyskavodarepairs/start"
topic5 = "homeassistant/sensor/sofiyskavodarepairs/end"
availability = 0
location = 'unknown'
typeofevent = 'unknown'
description = 'unknown'
start = 'unknown'
end = 'unknown'

while True:
    print('Starting new cycle! '+str(datetime.datetime.now())[0:-7]+'\n')
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)
    time.sleep(3)
    html = browser.page_source
    soup = BeautifulSoup(html.encode('utf-8'), 'html.parser')
    #print(soup)

    for td in soup.find_all('td', {'class': 'tdBottomRowSeperator'},limit = 100):
        td = str(td).replace('<br/>', '&').replace('<td class="tdBottomRowSeperator" style="max-width: 365px;"><b>Местоположение:</b> ','').replace('<b>','').replace('</b>','').replace('</td>','')
        print(str(td)+'\n\n')
        if 'Младост 4' in td:
            availability = 1
            location = str((td).split("&")[0].split(":")[1]).strip()
            typeofevent = str((td).split("&")[1].split(":")[1]).strip()
            description = str((td).split("&")[2].split(":")[1]).strip()
            start = str((td).split("&")[3].split(":")[1]+':'+(td).split("&")[3].split(":")[2]).strip()
            end = str((td).split("&")[4].split(":")[1]+':'+(td).split("&")[4].split(":")[2]).strip()
            print('Location: '+location)
            print('Type: '+typeofevent)
            print('Description: '+description)
            print('Start: '+start)
            print('End: '+end+'\n\n')
        else:
            availability = 0
            location = 'unknown'
            typeofevent = 'unknown'
            description = 'unknown'
            start = 'unknown'
            end = 'unknown'
            print('Location: '+location)
            print('Type: '+typeofevent)
            print('Description: '+description)
            print('Start: '+start)
            print('End: '+end+'\n\n')
            
    # Generate a Client ID with the publish prefix.
    msg0 = availability
    msg1 = location
    msg2 = typeofevent
    msg3 = description
    msg4 = start
    msg5 = end

    browser.close()
    browser.quit()

    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def publish(client):
        client.publish(topic0, msg0, retain=False)
        client.publish(topic1, msg1)
        client.publish(topic2, msg2)
        client.publish(topic3, msg3)
        client.publish(topic4, msg4)
        client.publish(topic5, msg5)

    def on_disconnect(client, userdata, rc):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
        global FLAG_EXIT
        FLAG_EXIT = True

    def run():
        client = connect_mqtt()
        publish(client)
        client.on_disconnect = on_disconnect

    if __name__ == '__main__':
        run()


    print('Cycle done! '+str(datetime.datetime.now())[0:-7]+'\n\n\n')
    for i in range(120):
        time.sleep(1)