from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# URL para o ambiente Vercel
VERCEL_URL = os.environ.get('VERCEL_URL', '')
is_production = VERCEL_URL != ''

# Diretório base onde estão os relatórios (só usado em desenvolvimento local)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REPORTS_DIR = os.path.join(BASE_DIR, 'vercel-reports')

# Em produção, usamos a memória global para armazenar as aprovações temporariamente
# Em um ambiente serverless real, isso seria substituído por Redis ou outro serviço KV
# Esta é uma solução temporária para evitar erros
APPROVALS_MEMORY = {}

# Arquivo onde serão armazenadas as aprovações (só usado em desenvolvimento local)
APPROVALS_FILE = os.path.join(REPORTS_DIR, 'approvals.json')

def get_approvals():
    """Carrega as aprovações"""
    if is_production:
        # Em produção (Vercel), usamos a memória global
        return APPROVALS_MEMORY
    else:
        # Em desenvolvimento local, usamos o arquivo
        try:
            with open(APPROVALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existir ou estiver vazio, retorna um dicionário vazio
            return {}

def save_approvals(approvals):
    """Salva as aprovações"""
    if is_production:
        # Em produção (Vercel), atualizamos a memória global
        global APPROVALS_MEMORY
        APPROVALS_MEMORY = approvals
    else:
        # Em desenvolvimento local, usamos o arquivo
        os.makedirs(os.path.dirname(APPROVALS_FILE), exist_ok=True)
        with open(APPROVALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(approvals, f, indent=2)

@app.route('/api/approvals', methods=['GET'])
def get_all_approvals():
    """Retorna todas as aprovações"""
    return jsonify(get_approvals())

@app.route('/api/approvals/<report_id>', methods=['GET'])
def get_report_approvals(report_id):
    """Retorna as aprovações de um relatório específico"""
    approvals = get_approvals()
    report_approvals = approvals.get(report_id, {})
    return jsonify(report_approvals)

@app.route('/api/approvals/<report_id>/<page_id>', methods=['GET'])
def get_page_approval(report_id, page_id):
    """Retorna a aprovação de uma página específica"""
    approvals = get_approvals()
    report_approvals = approvals.get(report_id, {})
    page_approval = report_approvals.get(page_id, {})
    return jsonify(page_approval)

@app.route('/api/approvals/<report_id>/<page_id>', methods=['POST'])
def set_page_approval(report_id, page_id):
    """Define a aprovação de uma página"""
    data = request.json
    
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Dados inválidos"}), 400
    
    status = data.get('status')
    if status not in ['approved', 'rejected']:
        return jsonify({"error": "Status deve ser 'approved' ou 'rejected'"}), 400
    
    user = data.get('user', 'anônimo')
    
    # Carrega as aprovações existentes
    approvals = get_approvals()
    
    # Inicializa o dicionário para o relatório se não existir
    if report_id not in approvals:
        approvals[report_id] = {}
    
    # Atualiza a aprovação da página
    approvals[report_id][page_id] = {
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'user': user
    }
    
    # Salva as aprovações
    save_approvals(approvals)
    
    return jsonify({"success": True, "message": f"Página {status} por {user}"})

@app.route('/')
def index():
    return jsonify({"message": "API de Aprovações - GDF Migrador"})

# Configuração para Vercel
if __name__ == '__main__':
    app.run(debug=True) 