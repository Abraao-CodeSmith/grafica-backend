from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
from functools import lru_cache
import time

app = Flask(__name__)
CORS(app)

DB_PATH = 'servicos.db'

# Cache para evitar ler o banco a cada requisição
@lru_cache(maxsize=1)
def get_all_servicos():
    """Carrega todos os serviços em cache por 5 minutos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT codigo, categoria, descricao, cores, peso, qtde, tam, prazo, preco FROM servicos")
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint leve para keep-alive - SEM banco de dados"""
    return jsonify({"status": "ok", "timestamp": time.time()}), 200

@app.route('/api/servicos')
def buscar_servicos():
    args = request.args
    nome = args.get("nome", "").lower()
    categoria = args.get("categoria", "")
    descricao = args.get("descricao", "")
    tam = args.get("tam", "")
    cores = args.get("cores", "")
    qtde = args.get("qtde", "")
    comissao = float(args.get("comissao", "0").replace(",", "."))
    
    # Carrega do cache (apenas uma vez a cada 5 minutos)
    servicos_raw = get_all_servicos()
    
    # Filtra em memória (mais rápido que SQL com muitos parâmetros)
    resultados = []
    for row in servicos_raw:
        if nome and nome not in row["descricao"].lower():
            continue
        if categoria and categoria != "Todos" and row["categoria"] != categoria:
            continue
        if descricao and descricao != "Todos" and row["descricao"] != descricao:
            continue
        if tam and tam != "Todos" and row["tam"] != tam:
            continue
        if cores and cores != "Todos" and row["cores"] != cores:
            continue
        if qtde and qtde != "Todos" and str(row["qtde"]) != qtde:
            continue
            
        preco_base = row["preco"]
        if preco_base is None:
            continue
            
        preco_final = preco_base * (1 + comissao / 100)
        resultados.append({
            "codigo": row["codigo"],
            "categoria": row["categoria"],
            "descricao": row["descricao"],
            "cores": row["cores"],
            "peso": row["peso"],
            "qtde": row["qtde"],
            "tam": row["tam"],
            "prazo": row["prazo"],
            "preco": round(preco_final, 2)
        })
    
    return jsonify(resultados)

# Opcional: limpar o cache a cada 5 minutos
def clear_cache():
    get_all_servicos.cache_clear()

# Se quiser, agende a limpeza (mas não é obrigatório)
# from apscheduler.schedulers.background import BackgroundScheduler
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=clear_cache, trigger="interval", minutes=5)
# scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)