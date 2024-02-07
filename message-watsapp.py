from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from datetime import datetime
from urllib.parse import quote
from time import sleep
from tqdm import tqdm
import csv, os


# configurações
servico = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=servico)
url = "https://web.whatsapp.com/"

# acessar site
browser.get(url)

# aguardando autenticação.
while len(browser.find_elements(By.ID, 'side')) < 1:
    pass

lista = []

with open('contato.csv', 'r') as file:
    file_csv = csv.reader(file, delimiter=';')
    for linha in file_csv:    
        lista.append(linha)

           
for nome, telefone in tqdm(lista):
    try:
        # pesquisar número
        sleep(2)
        browser.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/header/div[2]/div/span/div[5]/div').click()

        # inserir número
        sleep(2)
        browser.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div[1]/p').send_keys(telefone)
                      
        # Se o número existir enviar mensagem
        sleep(5)
        while len(browser.find_elements(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div[2]/div/div/span')) > 0:
                
            # clicar no contato
            sleep(2)
            browser.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[2]/div[2]').click()

            # mensagem 
            data = datetime.now()
            data_atual = data.strftime('%d/%m/%Y')
            horas = str(datetime.now())
            horas = int(horas[11:-13])

            if horas >= 6 and horas < 12:
                mensagem = f'Bom dia! *{nome}*, aqui é do Cemitério Jardim Paraiso. Em nosso sistema, foram encontrados débitos anteriores à *{data_atual}*. Por favor entre em contato conosco para regularização. Caso já tenha sido pago, por favor desconsiderar.'

            elif horas >= 12 and horas < 18:
                mensagem = f'Boa tarde! *{nome}*, aqui é do Cemitério Jardim Paraiso. Em nosso sistema, foram encontrados débitos anteriores à *{data_atual}*. Por favor entre em contato conosco para regularização. Caso já tenha sido pago, por favor desconsiderar.'

            elif horas >= 18:
                mensagem = f'Boa noite! *{nome}*, aqui é do Cemitério Jardim Paraiso. Em nosso sistema, foram encontrados débitos anteriores à *{data_atual}*. Por favor entre em contato conosco para regularização. Caso já tenha sido pago, por favor desconsiderar.'

            sleep(5)
                
            browser.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p').send_keys(mensagem)
            sleep(3)

            # Click no link add arquivo                   
            browser.find_element(By.XPATH,'//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div/div/div/div/span',).click()
            sleep(3)

            # Click no link para uploud de imagem
            browser.find_element(By.XPATH,'//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/ul/div/div[2]/li/div/input',).send_keys(os.path.abspath('jardimParaiso.png'))
            sleep(3)

            # Click em enviar mensagem
            browser.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div').click()
            sleep(5)
        
        # se a aba de pesquisa de numero estiver aberta fechar
        while len(browser.find_elements(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/header/div/div[1]/div/span')) > 0:
            browser.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/header/div/div[1]/div/span').click()
            sleep(2)
   
    # se houver erro mostrar erro        
    except ArithmeticError as Erro:
        pass
        




# carregamento
# //*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/span/div/span