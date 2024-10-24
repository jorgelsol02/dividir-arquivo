import os
from flask import Flask, request, render_template, send_from_directory, jsonify
import pandas as pd

app = Flask(__name__)

# Pasta onde os arquivos CSV divididos serão armazenados
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para limpar a pasta 'uploads'
def limpar_uploads():
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Erro ao deletar o arquivo {file_path}: {e}')

# Função para dividir o CSV
def dividir_csv(input_file, tamanho_lote):
    # Lê o arquivo CSV
    df = pd.read_csv(input_file, delimiter=';')
    num_partes = len(df) // tamanho_lote + (1 if len(df) % tamanho_lote != 0 else 0)

    arquivos_gerados = []

    # Dividir o arquivo CSV em partes
    for i in range(num_partes):
        inicio = i * tamanho_lote
        fim = min((i + 1) * tamanho_lote, len(df))
        df_part = df.iloc[inicio:fim].reset_index(drop=True)
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], f'arquivo_teste_parte_{i + 1}.csv')
        df_part.to_csv(output_file, sep=';', index=False)
        arquivos_gerados.append(f'arquivo_teste_parte_{i + 1}.csv')

    return arquivos_gerados

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Obtém o arquivo CSV
        file = request.files['file']
        if file.filename == '':
            return 'Nenhum arquivo foi enviado.', 400

        # Salva o arquivo CSV na pasta 'uploads'
        input_file = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_file)

        # Obtém o tamanho do lote
        tamanho_lote = int(request.form['tamanho_lote'])

        # Chama a função para dividir o CSV
        arquivos_gerados = dividir_csv(input_file, tamanho_lote)

        # Gera links para download dos arquivos gerados
        links_download = [f"/download/{arquivo}" for arquivo in arquivos_gerados]

        # Retorna os links para download
        return jsonify(links_download)

    # Chama a função para limpar a pasta 'uploads' antes de carregar a página
    limpar_uploads()
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
