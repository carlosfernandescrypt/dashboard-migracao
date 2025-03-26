from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Armazenamento em memória (será reiniciado a cada execução)
APPROVALS = {}

# Rota para API raiz
@app.route('/api', methods=['GET'])
def index():
    return jsonify({
        "message": "API de Aprovações - GDF Migrador",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    })

# Rota para listagem de todas as aprovações
@app.route('/api/approvals', methods=['GET'])
def list_approvals():
    return jsonify(APPROVALS)

# Rota para listagem de aprovações de um relatório específico
@app.route('/api/approvals/<report_id>', methods=['GET'])
def get_report_approvals(report_id):
    return jsonify(APPROVALS.get(report_id, {}))

# Rota para obter/definir a aprovação de uma página específica
@app.route('/api/approvals/<report_id>/<page_id>', methods=['GET', 'POST'])
def manage_page_approval(report_id, page_id):
    if request.method == 'GET':
        report_approvals = APPROVALS.get(report_id, {})
        return jsonify(report_approvals.get(page_id, {}))
    
    # Método POST - definir a aprovação
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados ausentes"}), 400
        
        status = data.get('status')
        if status not in ['approved', 'rejected']:
            return jsonify({"error": "Status deve ser 'approved' ou 'rejected'"}), 400
        
        user = data.get('user', 'anônimo')
        
        # Inicializa o dicionário para o relatório se não existir
        if report_id not in APPROVALS:
            APPROVALS[report_id] = {}
        
        # Atualiza a aprovação da página
        APPROVALS[report_id][page_id] = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'user': user
        }
        
        return jsonify({
            "success": True, 
            "message": f"Página {status} por {user}",
            "data": APPROVALS[report_id][page_id]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500 