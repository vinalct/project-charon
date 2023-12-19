import requests
import os
import time

# Configuracao de constantes.
API_TOKEN = os.getenv("API_KEY")
if not API_TOKEN:
    print("API nao setada")
    exit()


ACCOUNT_MAIN_ID = "..."
SITE_ID = "..."

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}


def fetch_course_details(course_name):
    """
    Resgata as informacoes do curso via nome fornecido.
    
    Parametros:
        course_name: o nome do curso desejado.
    
    Retorna:
        Dict: um dicionario contendo as informacoes do curso, ou nada, se nao for
        encontrado.
    """
    
    API_URL = "https://.../channels/headers/..."
    params = {
        'nameSubstring': course_name,
        'accountId': ACCOUNT_MAIN_ID,
        'siteId': SITE_ID,
        'start': 0,
        'limit': 25,
        'type': 'COURSE'
    }
    
    response = requests.get(API_URL, headers=HEADERS, params=params)
    data = response.json()
    
    channels = data.get('channels', [])
    
    exact_course = next((channel for channel in channels if channel['properties']['name'] == course_name), None)

    if exact_course:
        return {
            "name": exact_course['properties']['name'],
            "status": exact_course['properties']['status'],
            "description": exact_course['properties'].get('description', ''),
            "externalId": exact_course['externalId'],
            "id": exact_course['id']            
        }
        
    return None

def fetch_instructor_details(instructor_company_ids, course_id):
    """
    Resgata as informacoes do instrutor a partir da matricula e do curso desejado.
    
    Parametros:
        instructor_comapny_id: matricula.
        course_id: o ID do curso que foi inputado.
        
    Retorno:
        List: lista com o ID dos instrutores.
    """
    
    instructor_ids = []
    for instructor_company_id in instructor_company_ids:
        API_URL = "https://.../users"
        params = {
            'usernameSubstring': instructor_company_id,
            'possibleRoles': 'INSTRUCTOR',
            'limit': 25,
            'start': 0,
            'accountId': ACCOUNT_MAIN_ID,
            'siteId': SITE_ID,
            'channelId': course_id
        }
        
        response = requests.get(API_URL, headers=HEADERS, params=params)
        data = response.json()
        users = data.get('users', [])
        instructor_id = users[0]['id'] if users else None
        if instructor_id:
            instructor_ids.append(instructor_id)
    
    return instructor_ids

def register_course(instructor_ids, course_details_list):
    """
    Matricula o instrutor em diversos cursos.
    
    Parametros:
        instructor_id: o ID do instrutor a ser matriculado.
        course_details_list: uma lista das informacoes dos cursos em formato Dict.
    
    Retorno:
        List: as respostas das APIs para cada curso matriculado.
    """
    
    API_URL = f"https://.../channels/"\
                f"save?accountId={ACCOUNT_MAIN_ID}&..."
    responses = []
    pause_time = 3 # Pausa entre as requisicoes das APIs
    
    course_counter = 0
    
    for course_details in course_details_list:
        if course_details is None:
            print(f"Curso não encontrado na posicao {course_counter}")
            continue
        
        course_counter += 1
        print(f"Processando registro: {course_details['name']} ({course_counter}/{len(course_details_list)})")
        members_to_add = [{"memberId": instructor_id,
                           "role": "INSTRUCTOR",
                           "instructorPermission": "FULL"} for instructor_id in instructor_ids]
        
        channel_payload = {
            "channel": {
                "accountId": ACCOUNT_MAIN_ID,
                "properties": {
                    "name": course_details["name"],
                    "status": course_details["status"],
                    "description": course_details["description"],
                },
                "externalId": course_details["externalId"],
                "id": course_details["id"],
            },
            "membersToAdd": members_to_add,
            "siteIds": [SITE_ID]
        }
        
        response = requests.post(API_URL, headers=HEADERS, json=channel_payload)
        if response.status_code == 200:
            responses.append(response.json())
        else:
            responses.append({"error": response.text})
        
        time.sleep(pause_time)
        
    return responses

if __name__ == "__main__":
    # Define a lista de cursos a ser processado
    course_names = ['']
    # Resgata as informacoes de cada curso
    course_details_list = [fetch_course_details(course_name) for course_name in course_names]

    # Resgata as informacoes do instrutor.
    instructor_company_id = ['']
    instructor_id = fetch_instructor_details(instructor_company_id, course_details_list[0]['id'])

    # Matricula o instrutor em cada curso e printa as respostas das APIs
    responses = register_course(instructor_id, course_details_list)
    for response in responses:
        print(response)
