import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from PIL import Image
from werkzeug.utils import secure_filename

# --- Configuração do App Flask ---
app = Flask(__name__)

# Define as pastas para upload e para as imagens processadas
UPLOAD_FOLDER = os.path.join('static', 'uploads')
PROCESSED_FOLDER = os.path.join('static', 'processadas')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Garante que as pastas existam
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# --- Função de Conversão (a mesma de antes) ---
def transformar_em_pixel_art(caminho_imagem_entrada, caminho_imagem_saida, tamanho_pixel):
    try:
        imagem = Image.open(caminho_imagem_entrada)
        largura, altura = imagem.size

        # Evitar divisão por zero e valores inválidos
        if tamanho_pixel <= 0:
            tamanho_pixel = 10 # valor padrão

        nova_largura = max(1, largura // tamanho_pixel)
        nova_altura = max(1, altura // tamanho_pixel)
        
        imagem_pequena = imagem.resize((nova_largura, nova_altura), Image.Resampling.BILINEAR)
        imagem_pixelada = imagem_pequena.resize((largura, altura), Image.Resampling.NEAREST)
        
        imagem_pixelada.save(caminho_imagem_saida)
        return True
    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return False

# --- Rotas do Site ---

# Rota para a página inicial (métodos GET e POST)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica se um arquivo foi enviado
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        tamanho_pixel = int(request.form.get('tamanho_pixel', 10))

        if file.filename == '':
            return redirect(request.url)

        if file:
            # Salva a imagem original
            filename = secure_filename(file.filename)
            caminho_upload = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho_upload)
            
            # Define o caminho para a imagem processada
            nome_base, extensao = os.path.splitext(filename)
            nome_processado = f"{nome_base}_pixelart.png"
            caminho_processado = os.path.join(app.config['PROCESSED_FOLDER'], nome_processado)

            # Executa a conversão
            sucesso = transformar_em_pixel_art(caminho_upload, caminho_processado, tamanho_pixel)
            
            if sucesso:
                # Redireciona para a página de resultado se a conversão foi bem-sucedida
                return redirect(url_for('exibir_resultado', filename=nome_processado))
            else:
                # Lidar com erro (poderia redirecionar para uma página de erro)
                return "Ocorreu um erro ao processar sua imagem."

    # Se for um GET, apenas mostra a página inicial
    return render_template('index.html')

# Rota para exibir o resultado
@app.route('/resultado/<filename>')
def exibir_resultado(filename):
    return render_template('resultado.html', imagem_processada=filename)

# Rota para permitir o download da imagem
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)


# --- Iniciar o Servidor ---
if __name__ == '__main__':
    app.run(debug=True) # debug=True é ótimo para desenvolvimento