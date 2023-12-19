import requests
import csv
import os
import os.path
import datetime


headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

def get_workspace_ids():
    """
    Resgata os IDs de cada workspace (repositorios).
    
    Retorna:
        lista dos IDs.
    
    """
    WORKSPACE_STARTS = 0
    WORKSPACE_LIMIT = 50
    workspace_ids = []
    while True:
        #Faz uma requisicao para resgatar os detalhes de cada workspace
        response = requests.get(
            f'https://.../'
            f'section?limit={WORKSPACE_LIMIT}&orderBy=&section=C...&sortOrder'
            f'=ASC&start={WORKSPACE_STARTS}', headers=headers
            
        )
    
        data = response.json()
        
        #Extrai os IDs da resposta
        workspace_ids.extend([id['id'] for id in data])
        
        WORKSPACE_STARTS += WORKSPACE_LIMIT
        
        break
        
    return workspace_ids


def get_courses_workspace(workspace_id):
    """
    Resgata os conteudos especificos de cada workspace usando o ID 
    recuperado na funcao anterior.
    
    Args:
        workspace_id (str): o ID dos workspaces (repositorios)
        
    Retorno:
        lista: uma lista com os detalhes dos conteudos
    
    """
    #Faz a requisicao para o resgate dos detalhes dos conteudos.
    response = requests.get(
        f'https://.../channels/'
        f'{workspace_id}/content?contentOrderBy='
        f'...&contentSortOrder=DESC', headers=headers
    )
    
    data = response.json()
    workspace_name = data.get('name')
    library_items = data.get('libraryItems', [])
    extracted_data = []
    for item in library_items:
        #Extrai as informacoes relevantes dos conteudos.
        extracted_data.append(
            {
            'Estante': workspace_name,
            'ID do Curso': item.get('id'),
            'Nome do curso': item.get('name'),
            'Status': item.get('isPublished'),
            'Modificado': datetime.datetime.fromisoformat\
                        (item.get('modified').replace("Z", "+00:00")).date()\
                        if item.get('modified') else None    
            })
        print(f'Estante: {workspace_name}\n Conteudo: {extracted_data}\n')
 
    return extracted_data

def write_to_csv(data, writer):
    """
    Registra as informacoes em CSV.
    
    Args: 
        data (list): as informacoes extraidas das APIs.
        writer (csv.DictWriter): o registrador de CSV.
    
    """
    for row in data:
        writer.writerow(row)


def main():
    """
    A funcao principal que captura os detalhes dos workspaces e dos conteudos
    e registra no arquivo CSV.
    
    """
    workspace_ids = get_workspace_ids()
    filename = "Charon_workspaces.csv"
    name, extension = os.path.splitext(filename)
    counter = 1
    
    #Garante que cada nome de arquivo seja unico.
    while os.path.isfile(filename):
        filename = f"{name}_{counter}{extension}"
        counter += 1
        
    fieldnames = ['Estante', 'ID do Curso', 'Nome do curso', 'Status', 'Modificado']
    
    with open(filename, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for id in workspace_ids:
            data_courses = get_courses_workspace(id)
            write_to_csv(data_courses, writer)
    
        
        
if __name__ == "__main__":
    main()
    
    
    


    

 