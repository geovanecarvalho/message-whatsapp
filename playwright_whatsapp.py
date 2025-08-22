from playwright.sync_api import sync_playwright
from tqdm import tqdm
import csv, traceback, sys, os, re
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
    status = False
    try:
        # Clicar no botão de nova conversa
        print("Clicando no botão de nova conversa...")
        page.click('span[data-icon="new-chat-outline"]')

        # Esperar o campo de busca aparecer
        print("Esperando o campo de busca aparecer...")
        page.wait_for_selector('p.selectable-text.copyable-text', timeout=10000)
        print("Campo de busca encontrado.")

        # Inserir o número no campo de busca
        print("Inserindo o número no campo de busca...")
        search_box = page.query_selector('p.selectable-text.copyable-text')
        search_box.fill(phone_number)
        search_box.press('Enter')
        sleep(2)

        # Verificar se o número não foi encontrado
        print("Verificando se o número foi encontrado...")
        try:
            sleep(3)
            no_result_locator = page.locator('//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div/span', has_text=f'Nenhum resultado encontrado para “{phone_number}”')
            print(no_result_locator)
            if no_result_locator.is_visible():
                print(f"Número {phone_number} não encontrado no WhatsApp.")
                page.click('//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/header/div/div[1]/div/span')
                sleep(2)
                print(f"Contato não encontrado no WhatsApp.")
                status = False
            else:
                
                contact_locators = page.locator('//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/div[2]/div[3]/div[2]/div/div/span').first  # Captura todos os elementos com a classe _ao3e
                if contact_locators.is_visible():   
                    contact_locators.click()
                    status = True
                    
                    # Enviar imagem e mensagem
                    # upload_and_send_image(page, "./img/jardimParaiso.png")
                    sleep(2)
                    page.fill('//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]/p', get_greeting_message(contact_name))
                    sleep(2)
                    page.click('//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/button')
                    sleep(2)

        except Exception as e:
            print(f"Erro ao verificar se o número foi encontrado: {e}")

        return status

    except Exception as e:
        print(f"Erro ao enviar mensagem para {contact_name}: {e}")
        return False  # Erro ao enviar mensagem
    
def upload_and_send_image(page, image_path):
    """Faz upload de uma imagem e envia."""
    print(f"Enviando imagem {image_path}...")
    # clica no botão de +
    sleep(3)
    plus_icon_locator = page.locator('span[data-icon="plus"]')
    plus_icon_locator.click()
    sleep(3)
    page.set_input_files('input[accept="image/*,video/mp4,video/3gpp,video/quicktime"][type="file"]', os.path.abspath(image_path))
    sleep(3)
    page.locator('span[data-icon="send"]').click()

    
    
    print(f"Imagem {image_path} enviada.")


def main():
    with sync_playwright() as playwright:
        page = setup_browser(playwright)
        contacts = read_contacts('contato.csv')

        # Verifica se o arquivo já existe
        file_exists = os.path.exists("relatorio.csv")

        # Abre o arquivo CSV no modo de adição
        with open("relatorio.csv", "a", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)

            # Escreve o cabeçalho apenas se o arquivo não existir
            if not file_exists:
                csv_writer.writerow(["Nome", "Telefone", "Status", "Data/Hora"])  # Cabeçalho do CSV

            for name, phone in tqdm(contacts):
                try:
                    result = send_message(page, name, phone)
                    
                    # Verifica se o contato foi encontrado
                    if result:
                        status = "Enviado"
                    else:
                        status = "Não encontrado no WhatsApp"

                    # Escreve no relatório CSV
                    data = datetime.today().strftime("%d/%m/%Y %H:%M")
                    csv_writer.writerow([name, phone, status, data])

                except Exception as e:
                    # Captura o erro e registra no log de erros
                    data = datetime.today().strftime("%d/%m/%Y %H:%M")
                    error_trace = traceback.format_exc()
                    print(f"Erro ao enviar mensagem para {name}: {e}")
                    with open("log_erros.txt", "a", encoding="utf-8") as log_file:
                        log_file.write(f"{name};{phone};{data}\nErro: {str(e)}\nTraceback:\n{error_trace}\n")

        page.context.browser.close()
        print("Processo concluído.")

if __name__ == "__main__":
    main()