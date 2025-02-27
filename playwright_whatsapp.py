from playwright.sync_api import sync_playwright
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


def setup_browser(playwright):
    """Inicializa o navegador Chrome."""
    print("Inicializando o navegador...")
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL)
    print("Navegador inicializado e página carregada.")
    return page


def wait_for_authentication(page):
    """Aguarda a autenticação do WhatsApp Web."""
    print("Aguardando autenticação do WhatsApp Web...")
    while not page.query_selector('#side'):
        sleep(1)
    print("Autenticação concluída.")


def read_contacts(file_path):
    """Lê os contatos de um arquivo CSV e retorna uma lista."""
    print(f"Lendo contatos do arquivo {file_path}...")
    contacts = []
    with open(file_path, 'r', encoding='latin1') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            contacts.append(row)
    print(f"{len(contacts)} contatos lidos.")
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


def send_message(page, contact_name, phone_number):
    """Envia uma mensagem para o contato especificado."""
    print(f"Enviando mensagem para {contact_name} ({phone_number})...")
    
    # clicar no botão de +
    sleep(2)
    page.click('//*[@id="app"]/div/div[3]/div/div[3]/header/header/div/span/div/div[1]/button/span')
    sleep(2)
    
    # capturar campo de input
    search_box = page.query_selector('//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div/p')
    sleep(1)
    
    # inserir mensagem
    search_box.fill(phone_number)
    sleep(3)

    # apertar enter
    search_box.press('Enter')
    sleep(2)
    
    # verificar se o numero é valido se nao existir uma imagem
    if not page.query_selector('//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div/div/div[2]/div/div/div[1]/div/div/img'): 
        print(f"Número {phone_number} inválido.")
        # voltar para pagina anterior
        sleep(2)    
        page.click('//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/header/div/div[1]/div/span')
    # enviar mensagem
    else:       
        # Escolher qual função de mensagem
        # clica no contato
        page.click('//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div/div/div[2]/div/div/div[1]/div/div/img')
        
        
        sleep(5)
        upload_and_send_image(page, './img/jardimParaiso.png')
        
        sleep(2)

        page.fill('//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/p', get_greeting_message(contact_name))
        sleep(2)
        
        page.click('//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div')
        
        sleep(5)
        print(f"Mensagem enviada para {contact_name} ({phone_number}).")


def upload_and_send_image(page, image_path):
    """Faz upload de uma imagem e envia."""
    print(f"Enviando imagem {image_path}...")

    sleep(2)
    page.click('//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div/button/span')
    sleep(3)
    page.set_input_files('//*[@id="app"]/div/span[5]/div/ul/div/div/div[2]/li/div/input', os.path.abspath(image_path))
    sleep(3)
    
    
    print(f"Imagem {image_path} enviada.")


def main():
    with sync_playwright() as playwright:
        page = setup_browser(playwright)
        wait_for_authentication(page)

        contacts = read_contacts('contato.csv')
        count = 0
        for name, phone in tqdm(contacts):
            name = name.strip().upper()
            phone = format_phone_number(phone)

            try:
                send_message(page, name, phone)
                data = datetime.today().strftime("%d/%m/%Y %H:%M")
                with open("log.txt", "a") as log_file:
                    log_file.write(f"{name};{phone};{data}\n")
            except Exception as e:
                data = datetime.today().strftime("%d/%m/%Y %H:%M")
                print(f"Erro ao enviar mensagem para {name}: {e}")
                with open("log.txt", "a") as log_file:
                    log_file.write(f"{name};{phone} {data}\nErro: {str(e)}\n")

        page.context.browser.close()
        print("Processo concluído.")

if __name__ == "__main__":
    main()