from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

#Importa as funcoes dos scripts.
from get_cursos import generate_cursos_csv
from get_relatorios import generate_reports_csv
from get_workspaces import generate_workspaces_csv

app = Flask(__name__)

#Configuracao de rate limits para cada route.
app.config['COURSE_RATE_LIMIT'] = "1 per 90 seconds"
app.config['REPORT_RATE_LIMIT'] = "1 per 180 seconds"
app.config['WORKSPACE_RATE_LIMIT'] = "1 per 300 seconds"

#Seta o rate limiter usando o IP do usuario como chave.
limiter = Limiter(
    app=app,
    key_func=get_remote_address
)

@app.route('/')
def index():
    """ Renderiza a pagina princiapl. """
    return render_template('index.html')

@app.route('/download-cursos', methods=['GET', 'POST'])
@limiter.limit(app.config['COURSE_RATE_LIMIT'])
def download_cursos_csv():
    """ Fica responsavel pelas requisicoes de download de cursos.
    
    GET requests para renderizar a pagina principal.
    POST requests para processar o nome do curso inputado pelo usuario e 
    acionar o gerador de CSV.
    
    """
    
    if request.method == 'POST':
        data = request.form
        course_names_string = data.get('course_names', '').strip()
        course_names_input = [name.strip() for name in course_names_string.\
                                split(',')] if course_names_string else []
        
        if not course_names_input or not isinstance(course_names_input, list):
            return jsonify({"error": "nomes de cursos invalidos"}), 400
        
        
        csv_path = generate_cursos_csv(course_names_input)
        return send_csv_file(csv_path)
        
    return render_template('index.html')
    
@app.route('/download-relatorios', methods=['POST'])
@limiter.limit(app.config['REPORT_RATE_LIMIT'])
def download_relatorios_csv():
    """ Fica responsavel pelas requisicoes de download dos csv de relatorios.
    
    Processa o nome do relatorio inputado pelo usuario e aciona o gerador 
    de csv.
    
    """
    report_name_string = request.form.get('report_name', '').strip()
    report_names_input = [name.strip() for name in report_name_string.split(',')] if report_name_string else []
    
    if not report_names_input:
        return "Por favor, insira o nome do relatório desejado", 400
        
    csv_path = generate_reports_csv(report_names_input)
    
    return send_csv_file(csv_path)
    
    
@app.route('/download-workspaces', methods=['GET'])
@limiter.limit(app.config['WORKSPACE_RATE_LIMIT'])
def download_workspaces_csv():
    """ Fica responsavel pelo download dos CSV do workspace (repositorios).
    
    Aciona o gerador de CSV para a funcao workspace.
    
    """
    csv_path = generate_workspaces_csv()
    return send_csv_file(csv_path)


def send_csv_file(csv_path):
    """Fica responsavel por enviar o arquivo CSV gerado como anexo para download.
    
    Parametro:
        csv_path (str): o caminho do caminho do arquivo CSV a ser enviado.
        
    Retorno:
        Resposta flask: o arquivo CSV como anexo.
    
    """
    return send_from_directory(directory=os.path.dirname(csv_path),
                               path=os.path.basename(csv_path),
                               as_attachment=True)
    
@app.errorhandler(429)
def ratelimit_error(e):
    """ Responsavel pela mensagem de erro dos rate limits. """
    return jsonify(error= "limite foi excedido.", message=str(e.description)), 429

@app.errorhandler(500)
def internal_server_error(e):
    """ Responsavel por encmainhar mensagem quando acontecer erros internos """
    return jsonify(error="erro interno", message="Um erro ocorreu. Tente novamente mais tarde."), 500


if __name__ == "__main__":
    app.run(debug=True)
    