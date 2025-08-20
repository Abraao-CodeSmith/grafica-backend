from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = 'servicos.db'

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

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT codigo, categoria, descricao, cores, peso, qtde, tam, prazo, preco FROM servicos WHERE 1=1"
    params = []

    if nome:
        query += " AND LOWER(descricao) LIKE ?"
        params.append(f"%{nome}%")
    if categoria and categoria != "Todos":
        query += " AND categoria = ?"
        params.append(categoria)
    if descricao and descricao != "Todos":
        query += " AND descricao = ?"
        params.append(descricao)
    if tam and tam != "Todos":
        query += " AND tam = ?"
        params.append(tam)
    if cores and cores != "Todos":
        query += " AND cores = ?"
        params.append(cores)
    if qtde and qtde != "Todos":
        query += " AND qtde = ?"
        params.append(int(qtde))

    query += " ORDER BY categoria, descricao, qtde"

    results = cursor.execute(query, params).fetchall()
    conn.close()

    servicos = []
    for row in results:
        preco_base = row["preco"]
        if preco_base is None:
            continue  # pula esse item
        preco_final = preco_base * (1 + comissao / 100)
        servicos.append({
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

    return jsonify(servicos)

if __name__ == '__main__':
    app.run(debug=True)
