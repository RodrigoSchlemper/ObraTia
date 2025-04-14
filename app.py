from flask import Flask, request, jsonify, send_file, render_template
import psycopg2
import os
from dotenv import load_dotenv
import io

load_dotenv()
app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route("/custos", methods=["POST"])
def adicionar_custo():
    tipo = request.form.get("tipo")
    descricao = request.form.get("descricao")
    valor = request.form.get("valor")
    data_compra = request.form.get("data_compra")
    observacao = request.form.get("observacao")

    anexo = request.files.get("anexo")
    nome_arquivo = anexo.filename if anexo else None
    conteudo_arquivo = anexo.read() if anexo else None

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO custos (tipo, descricao, valor, data_compra, observacao, anexo, nome_arquivo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        tipo, descricao, valor, data_compra, observacao, conteudo_arquivo, nome_arquivo
    ))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"mensagem": "Custo adicionado com anexo!"})

@app.route("/custos", methods=["GET"])
def listar_custos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tipo, descricao, valor, data_compra, observacao, nome_arquivo
        FROM custos
        ORDER BY data_compra DESC
    """)
    registros = cur.fetchall()
    cur.close()
    conn.close()

    lista = []
    for row in registros:
        lista.append({
            "id": row[0],
            "tipo": row[1],
            "descricao": row[2],
            "valor": float(row[3]),
            "data_compra": row[4].isoformat(),
            "observacao": row[5],
            "nome_arquivo": row[6]
        })
    return jsonify(lista)

@app.route("/custos/<int:id>", methods=["PUT"])
def editar_custo(id):
    if request.content_type.startswith('multipart/form-data'):
        tipo = request.form.get("tipo")
        descricao = request.form.get("descricao")
        valor = request.form.get("valor")
        data_compra = request.form.get("data_compra")
        observacao = request.form.get("observacao")
        remover_anexo = request.form.get("remover_anexo") == "true"

        anexo = request.files.get("anexo")
        nome_arquivo = anexo.filename if anexo else None
        conteudo_arquivo = anexo.read() if anexo else None

        conn = get_conn()
        cur = conn.cursor()

        if remover_anexo:
            cur.execute("""
                UPDATE custos
                SET tipo=%s, descricao=%s, valor=%s, data_compra=%s, observacao=%s, anexo=NULL, nome_arquivo=NULL
                WHERE id=%s
            """, (tipo, descricao, valor, data_compra, observacao, id))
        elif anexo:
            cur.execute("""
                UPDATE custos
                SET tipo=%s, descricao=%s, valor=%s, data_compra=%s, observacao=%s, anexo=%s, nome_arquivo=%s
                WHERE id=%s
            """, (tipo, descricao, valor, data_compra, observacao, conteudo_arquivo, nome_arquivo, id))
        else:
            cur.execute("""
                UPDATE custos
                SET tipo=%s, descricao=%s, valor=%s, data_compra=%s, observacao=%s
                WHERE id=%s
            """, (tipo, descricao, valor, data_compra, observacao, id))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensagem": "Custo atualizado com sucesso!"})
    else:
        return jsonify({"erro": "Requisição inválida"}), 400

@app.route("/custos/<int:id>", methods=["DELETE"])
def excluir_custo(id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM custos WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensagem": "Custo excluído com sucesso!"})

@app.route("/anexo/<int:id>")
def baixar_anexo(id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT nome_arquivo, anexo FROM custos WHERE id = %s", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and row[1]:
        return send_file(
            io.BytesIO(row[1]),
            as_attachment=True,
            download_name=row[0]
        )
    else:
        return jsonify({"erro": "Arquivo não encontrado"}), 404

@app.route("/listar")
def listar_interface():
    return render_template("listar.html")

@app.route("/editar")
def editar_interface():
    return render_template("editar.html")

@app.route("/")
def home():
    return render_template("listar.html")

# Deixe vazio, ou só:
# if __name__ == "__main__":
#     app.run(debug=True)

