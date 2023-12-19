import requests
import json
import csv
import os


headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json',
}

COURSES_ID_API = 'https://.../channels'
REPORTS_API = 'https://.../participants/export/get'


def get_report_id(report_names):
    """
    Captura os IDs de relatórios específicos.
    
    Retorna:
        A lista dos IDs solicitados pelo usuário.
    
    """
    courses_response = requests.get(COURSES_ID_API, headers=headers, timeout=10)
    courses = courses_response.json()
    return [course['id'] for course in courses if course['properties']['name'] in report_names]


def get_report_data(channel_id, csv_writer, csv_file):
    """
    Retorna e escreve as informações dos relatórios dos cursos resgatados na função anterior.
    
    Args:
        channel_id: o ID do curso/relatorio a ser resgatado.
        csv_writer: variável que escreve as informacoes em csv.
        csv_file: a funcao que cria o arquivo csv.
        
    Retorna:
        O csv.
    """
    
    report_api = 'https://.../participants/export/get'
    report_data = {
        "channelId": channel_id,
        "locale": "pt_br",
    }

    response = requests.post(report_api, headers=headers, data=json.dumps(report_data), timeout= 10)
    response_content = response.text.split("\n")

    for row in response_content:
        csv_writer.writerow(row.split(","))
        print(row)

    return csv_writer, csv_file


def open_csv(base_filename, extension=".csv"):
    """
    Abre um novo arquivo csv com identificador único.
    
    Args:
        base_filename: a base do nome do arquivo.
        extension: a extensao para o arquivo.
        
    Retorna:
        O csv.
    """
    counter = 1
    filename = base_filename + extension
    while os.path.exists(filename):
        filename = f"{base_filename}{(counter)}{extension}"
        counter += 1
        
    csv_file = open(filename, 'w')
    csv_writer = csv.writer(csv_file)
    
    return csv_writer, csv_file


def generate_reports_csv(report_names_input):
    """
    A funcao principal do script.
    Captura o ID dos cursos/relatorios, retorna e escreve no csv as informacoes de cada relatorio.
    """
    report_names = [name.strip() for name in report_names_input]
    
    if len(report_names) > 10:
        logging.error("Attempt to fetch more than 10 reports.")
        raise ValueError("Não é possível baixar mais que 10 relatorios por vez.")
    
    courses_ids = get_report_id(report_names_input)
    total_ids = len(courses_ids)

    csv_writer, csv_file = open_csv("Charon-Relatorios")

    for i, channel_id in enumerate(courses_ids):
        print(f"Processing report {i+1} of {total_ids}")
        csv_writer, csv_file = get_report_data(channel_id, csv_writer, csv_file)

    csv_file.close()
    return csv_file.name

if __name__ == "__main__":
    generate_reports_csv()