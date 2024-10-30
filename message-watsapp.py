from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm
import csv
import os
import re
from datetime import datetime
from time import sleep

# Configurações
URL = "https://web.whatsapp.com/"
IMAGE_PATHS = {
    "plano_funerario": "plano_funerario.jpg",
    "dia_finados": "diaFinados.jpg"
}


def setup_browser():
    """Inicializa o navegador Chrome."""
    browser = webdriver.Chrome()
    browser.get(URL)
    return browser


def wait_for_authentication(browser):
    """Aguarda a autenticação do WhatsApp Web."""
    while len(browser.find_elements(By.ID, 'side')) < 1:
        sleep(1)


def read_contacts(file_path):
    """Lê os contatos de um arquivo CSV e retorna uma lista."""
    contacts = []
    with open(file_path, 'r', encoding='latin1') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            contacts.append(row)
    return contacts


def format_phone_number(phone):
    # Remove caracteres não numéricos
    digits = re.sub(r'\D', '', phone)
    # Inicializa a variável de retorno
    result = "Número inválido!"  # Valor padrão
    # Verifica se o número tem DDD
    if len(digits) >= 10:
        if len(digits) == 11 and digits[2] == '9':  # 11 dígitos e o 3º dígito deve ser 9  
            num = digits[:2] + digits[3:]
            if num[2] in ['8', '9']:
                result = num # Retorna DDD + 8 dígitos
        elif len(digits) == 10 and digits[2] in ['8', '9']:  # 10 dígitos, 3º dígito deve ser 8 ou 9
            result = digits  # Retorna o número original

    return result  # Retorna o resultado final


def get_greeting_message(name):
    """Retorna uma mensagem de saudação com base na hora atual."""
    current_hour = datetime.now().hour
    greeting = "Bom dia!" if current_hour < 12 else "Boa tarde!" if current_hour < 18 else "Boa noite!"
    data_atual = datetime.now().strftime('%d/%m/%Y')
    return f'{greeting} *{name}*, aqui é do Cemitério Jardim Paraiso. Em nosso sistema, foram encontrados débitos anteriores à *{data_atual}*. Por favor entre em contato conosco para regularização. Caso já tenha sido pago, por favor desconsiderar.'


def send_message(browser, contact_name, phone_number):
    """Envia uma mensagem para o contato especificado."""
    
    # clicar no botão de +
    browser.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[3]/header/header/div/span/div/span/div[1]/div/span').click()
    sleep(2)
    
    # capturar campo de input
    search_box = browser.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div/p')
    sleep(1)
    
    # inserir mensagem
    search_box.send_keys(phone_number)
    sleep(3)

    # apertar enter
    search_box.send_keys(Keys.ENTER)

    # verificar se o numero é valido
    if len(browser.find_elements(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[2]/div/div/span')) > 0: 
         # voltar para pagina anterior
        sleep(1)    
        browser.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/header/div/div[1]/div/span').click()
    # enviar mensagem
    else:       
        # Escolher qual função de mensagem
        sleep(5)
        upload_and_send_image(browser, 'plano_funerario.jpg')
        
        sleep(5)
        upload_and_send_image(browser, 'diaFinados.jpg')
        

    
    


def send_image_and_message(browser, message):
    """Envia uma mensagem de texto e duas imagens."""
    # Enviar mensagem

    #browser.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]/p').send_keys(message)
    # sleep(3)
    
    # Enviar a primeira imagem
    upload_and_send_image(browser, IMAGE_PATHS["plano_funerario"])
    # Enviar a segunda imagem
    upload_and_send_image(browser, IMAGE_PATHS["dia_finados"])


def upload_and_send_image(browser, image_path):
    """Faz upload de uma imagem e envia."""
    browser.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div[2]/div/div/div/span').click()
    sleep(3)
    browser.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div[2]/div/span/div/ul/div/div[2]/li/div/input').send_keys(os.path.abspath(image_path))
    sleep(3)
    browser.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div').click()
    sleep(5)


def main():
    browser = setup_browser()
    wait_for_authentication(browser)

    contacts = read_contacts('contato.csv')
    count = 0
    for name, phone in tqdm(contacts):
        name = name.strip().upper()
        phone = format_phone_number(phone)

        try:
            send_message(browser, name, phone)
            
            with open("log.txt", "a") as log_file:
                log_file.write(f"{name};{phone}\n")
        except Exception as e:
            print(f"Erro ao enviar mensagem para {name}: {e}")
            with open("log.txt", "a") as log_file:
                log_file.write(f"{name};{phone} Erro: {str(e)}\n")

    browser.quit()

if __name__ == "__main__":
    main()
