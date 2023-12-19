import requests
import csv
import os
import os.path
import datetime


#Headers necessario para realizar requisicao na API.
headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

def get_workspace_ids():
    
    """
    Retorna os IDs dos workspaces(repositorios).
    
    Retorno:
        lista: lista com os IDs.
    
    """
    
    WORKSPACE_STARTS = 0
    WORKSPACE_LIMIT = 50
    workspace_ids = []
    while True:
        response = requests.get(
            f'https://.../channelQuery/'
            f'section?limit={WORKSPACE_LIMIT}&orderBy=&s...'
            f'=ASC&start={WORKSPACE_STARTS}', headers=headers
            
        )
    
        data = response.json()
        
        workspace_ids.extend([id['id'] for id in data])
        
        WORKSPACE_STARTS += WORKSPACE_LIMIT
        
        
    return workspace_ids


def get_courses_workspace(workspace_id):
    """
    Retorna os conteudos que estao contidos nos workspaces(repositorios),
    a partir dos IDs recuperados na funcao anterior.
    
    Parametro:
        workspace_id (str): os IDs dos workspaces.
        
    Retorno:
        lista: lista de dicionarios, cada um contendo a informacao sobre
        um conteudo.
    """
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
    Escreve os dados recuperados em um arquivo CSV, usando um writer.
    
    Parametros:
        data (list): lista de dicionarios contendo informacoes dos conteudos.
        writer (csv.DictWriter): um CSV writer para escrita dos dados.
    
    """
    
    for row in data:
        writer.writerow(row)


def generate_workspaces_csv():
    """
    Funcao principal do script. Resgata os IDs do workspace, informacoes 
    de cada workspace (repositorio), e registra os dados no arquivo CSV.
    
    Retorno:
        str: o nome do csv gerado.
    """

    workspace_ids = get_workspace_ids()
    filename = "Charon_workspaces.csv"
    name, extension = os.path.splitext(filename)
    counter = 1
    
    #Garante que cada arquivo tera um nome exclusivo.
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
            
    return filename
        
        
if __name__ == "__main__":
    generate_workspaces_csv()
    
    
    


    

 