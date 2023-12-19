import requests
import csv
import time
import os

#Headers necessario para realizar a requisicao na API.
headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

#Um delay para evitar flood de requisicao na API.
SLEEP_TIME = 1

def get_catalog_items(input_trail_names):
    """
    Procura, pela API do catalogo, o ID das trilhas solicitadas pelo usuário. 
    Retorna:
        uma lista com tuplas contendo ID da trilha e o ID da estrutura da trilha. 
    """
    catalog_items = []
    CATALOG_LIMIT = 20
    
    for trail_name in input_trail_names:
        response = requests.get(
           f"https://.../catalogItems/...",
           params={
               'nameSubstring': trail_name,
               'orderBy': 'created',
               'sortOrder': 'DESC',
               'start': 0,
               'limit': CATALOG_LIMIT,
               'catalogItemRequestType': 'MANAGE_CATALOG'
           },
            headers=headers
        )

        print(response.status_code)
        data = response.json()
        if not data:
            break

        
        for item in data:
            print(f"Item name: {item['name']}")
            if item['name'] == trail_name:
                catalog_items.append((item.get('channelId'), item.get('contentStructureId')))
                
            
        print(f'Processed {len(catalog_items)} items.')

        time.sleep(SLEEP_TIME)

    return catalog_items


def get_course_names(course_id):
    """
    A partir da lista de IDs das trilhas, essa funcao busca os conteudos de cada uma delas.
    
    Retorna:
        course_name: o nome de cada um dos cursos contidos na trilha.
        trail_name: o nome da trilha que esta interando.
        courses_status: o status de cada um dos cursos contidos na trilha.
        id_conteudo: o ID de cada um dos cursos.
    """
    response = requests.get(f'https://.../channels/'
                            f'{course_id}/...=publishExtraData.serverPu'
                            f'...&contentSortOrder=DESC', headers=headers)
    data = response.json()
    trail_name = data.get('name', '')
    course_names = {course['id']: course['name'] for course in data['libraryItems']}
    courses_status = {course['id']: course['isPublished'] for course in data['libraryItems']}
    return course_names, trail_name, courses_status




def get_course_structure(structure_id, course_id, course_names, courses_status):
    """
    Essa funcao, a partir dos IDs das estruturas das trilhas, ordena os conteudos conforme
    é visto no site. Ou seja, organiza as informacoes adquiridas na funcao anterior.
    """
    
    response = requests.get(f'https://.../contentStructure/'
                            f'{structure_id}/...channelId={course_id}', headers=headers)
    data = response.json()
    root_items = data.get('rootLevel', {}).get('items', [])
    organized_items = []
    
    for item in root_items:
        if item['itemType'] == 'Level':
            day_name = item.get('level', {}).get('name', '')
            day_courses = [(course_names[sub_item['itemId']], courses_status[sub_item['itemId']])
                           for sub_item in item.get('level', {}).get('items', [])
                           if sub_item['itemType'] == 'ContentItem' and sub_item['itemId'] in course_names]
            organized_items.append({day_name: day_courses})
        else:
            day_name = ''
            course_name = course_names.get(item['itemId'], '')
            course_status = courses_status.get(item['itemId'], '')
            organized_items.append({day_name: [(course_name, course_status)]})
            

        
    return organized_items


def get_unique_filename(base_filename):
    """
    Retorna um único nome do arquivo csv.
    """
    counter = 1
    filename, file_extension = os.path.splitext(base_filename)
    
    while os.path.exists(base_filename):
        base_filename = f"{filename}_{counter}{file_extension}"
        counter += 1
        
    return base_filename


def write_to_csv(course_structure, trail_name, course_names, filename):
    """
    Escreve as informacoes coletadas e organizadas em um csv.
    course_id retorna o ID de cada conteudo e escreve no csv.
    """
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Nome da Trilha","Dia", "ID do Conteúdo","Conteúdo", "Status"])

        for day in course_structure:
            for day_name, courses in day.items():
                for course, status in courses:
                    course_id = list(course_names.keys())[list(course_names.values()).index(course)]
                    writer.writerow([trail_name, day_name, course_id, course, status])


def generate_cursos_csv(course_names_input):
    """
    Captura os itens do catalogo, retorna e processa os cursos, escreve no CSV as informacoes
    de cada conteudo e trilha.
    """
    
    if not course_names_input:
        return "É preciso fornecer o nome do curso desejado."
    
    if len(course_names_input) > 10:
        return "Erro: o máximo de cursos a ser baixado é de até 10"
    
    unique_filename = get_unique_filename("Charon_Cursos.csv")
    catalog_items = get_catalog_items(course_names_input)
    print(f"Retrieved {len(catalog_items)} catalog items.")

    for index, (course_id, structure_id) in enumerate(catalog_items, 1):
        try:
            course_names, trail_name, courses_status = get_course_names(course_id)
            print(f"Processing trail {index}/{len(catalog_items)}: {trail_name}")
            course_structure = get_course_structure(structure_id, course_id, course_names, courses_status)
            write_to_csv(course_structure, trail_name, course_names, unique_filename)
        except Exception as e:
            print(f"Error processing trail {trail_name}: {str(e)}")
            
        time.sleep(SLEEP_TIME)
        
    return unique_filename


if __name__ == "__main__":
    generate_cursos_csv()
