from flask import Flask, request, render_template_string, send_from_directory, jsonify
import os
import subprocess

app = Flask(__name__)

# Diretórios
UPLOAD_FOLDER = 'uploads'
BUILD_FOLDERs = 'download'
BUILD_FOLDER = 'tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BUILD_FOLDER, exist_ok=True)
os.makedirs(BUILD_FOLDERs, exist_ok=True)

# Contador global para arquivos
file_counter = 0

# Página HTML
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>dissembler Server</title>
    <style>
        body {
            background-color: yellow;
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <h1>Upload a dissembler File</h1>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="cfile" accept=".o" required />
        <button type="submit">Upload and Compile</button>
    </form>
</body>
</html>
'''
HTML_Dowload = '''
<!DOCTYPE html>
<html>
<head>
    <title>dissembler Server</title>
    <style>
        body {
            background-color: yellow;
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <h1>Download a dissembler File</h1>
    <a href="$file">.S</a><br>
    
    stdio:<br>
    $stdio<br>
    sterror:<br>
    $sterror:<br>

</body>
</html>
'''
HTML_error = '''
<!DOCTYPE html>
<html>
<head>
    <title>dissembler Server</title>
    <style>
        body {
            background-color: yellow;
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <h1>error a CS File</h1>
    stdio:<br>
    $stdio<br>
    sterror:<br>
    $sterror:<br>
   
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_counter
    file_counters=file_counter
    # Verificar e salvar o arquivo enviado
    if 'cfile' not in request.files:
        return "No file part", 400

    file = request.files['cfile']
    if file.filename == '':
        return "No selected file", 400

    if not file.filename.endswith('.o'):
        return "Only .o files are allowed", 400

    # Salvar o arquivo
    c_file_path = os.path.join(UPLOAD_FOLDER, str(file_counters)+".o")
    file.save(c_file_path)

    # Nome do executável
    executable_name = f"{file_counters}.S"
    executable_path = os.path.join(BUILD_FOLDERs, executable_name)
    stdout=""
    stderr=""
    # Executar build.sh com o contador como argumento
    try:
        subprocess.run(['./starts.sh',str(file_counters)], check=True)  # Executa o script starts.sh

        result = subprocess.run(
            ['./build.sh', str(file_counters)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
       
        # Incrementar o contador
        

        # Gravar o executável temporário
        # Gravar o executável temporário
        if result.stdout.find("err")<0 and result.stderr.find("err")<0:
            s=HTML_Dowload.replace("$stdio",result.stdout.replace("\n","<br>"))
            s=s.replace("$sterror",result.stderr.replace("\n","<br>"))
            s=s.replace("$file", BUILD_FOLDERs+"/"+executable_name)
            
            file_counter += 1
            return s
        else:
            s=HTML_error.replace("$stdio",result.stdout.replace("\n","<br>"))
            s=s.replace("$sterror",result.stderr.replace("\n","<br>"))
            file_counter += 1
            file_counter += 1
            return s
        file_counter += 1
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Script execution failed', 'details': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    print(BUILD_FOLDERs+"/"+filename)
    return send_from_directory(BUILD_FOLDERs, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

