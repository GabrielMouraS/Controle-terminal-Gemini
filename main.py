import os
import subprocess
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurar a API do Gemini
GEMINI_API_KEY = "AIzaSyDds4nRYhvNRxteJpbohx6Bf35VQdoPcZc"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class MiniLLMSystem:
    def __init__(self):
        self.conversation_history = []
    
    def execute_command(self, command):
        """Executa um comando shell e retorna o resultado"""
        try:
            # Lista de comandos que afetam o sistema operacional e devem ser bloqueados
            system_affecting_commands = [
                "shutdown", "reboot", "halt", "poweroff",  # Comandos de desligamento
                "mkfs", "fdisk", "parted", "gparted",      # Formatação de disco
                "dd if=", "dd of=/dev",                    # Comandos dd perigosos
                "rm -rf /", "rm -rf /*", "rm -rf /usr", "rm -rf /etc", "rm -rf /var", "rm -rf /boot",  # Remoção de diretórios do sistema
                "chmod 000 /", "chown root:root /",        # Alterações de permissão perigosas
                "passwd root", "userdel", "usermod -s",    # Alterações de usuário do sistema
                "iptables -F", "ufw --force reset",        # Reset de firewall
                "systemctl stop", "systemctl disable",     # Parar serviços críticos
                "mount", "umount /",                       # Montagem/desmontagem perigosa
                "init 0", "init 6", "telinit",            # Mudança de runlevel
                "kill -9 1", "killall -9 init",           # Matar processo init
                "crontab -r", "> /etc/passwd",             # Comandos que podem quebrar o sistema
                "rm /etc/", "rm /usr/", "rm /var/",        # Remoção de diretórios críticos
            ]
            
            # Verificar se o comando contém algum padrão perigoso
            command_lower = command.lower().strip()
            for dangerous_pattern in system_affecting_commands:
                if dangerous_pattern in command_lower:
                    return {
                        "success": False,
                        "error": f"Comando '{dangerous_pattern}' afeta o sistema operacional e não será executado",
                        "response": "Por segurança, não posso executar comandos que afetem o sistema operacional."
                    }

            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Comando expirou (timeout de 30 segundos)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_file(self, filename, content):
        """Cria um arquivo com o conteúdo especificado"""
        try:
            import os
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Obter informações do arquivo para o download
            file_size = os.path.getsize(filename)
            return {
                "success": True, 
                "message": f"Arquivo {filename} criado com sucesso",
                "filename": filename,
                "file_size": file_size,
                "download_available": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, filename):
        """Lê o conteúdo de um arquivo"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_request(self, user_input):
        """Processa a solicitação do usuário usando o Gemini via HTTP"""
        
        # Prompt do sistema para orientar o comportamento do LLM
        system_prompt = """
        Você é um assistente AI que pode executar tarefas simples no sistema. 
        Você tem acesso às seguintes funções:
        - execute_command(command: str): Executa um comando shell. Retorna a saída do comando.
        - create_file(filename: str, content: str): Cria um arquivo com o conteúdo especificado. Retorna uma mensagem de sucesso ou erro.
        - read_file(filename: str): Lê o conteúdo de um arquivo. Retorna o conteúdo do arquivo ou uma mensagem de erro.
        
        Quando o usuário fizer uma solicitação, analise o que ele quer e chame a função apropriada.
        Se for apenas uma pergunta ou conversa, responda diretamente.
        
        Seja sempre seguro e não execute comandos perigosos.
        """
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": GEMINI_API_KEY
            }
            
            # Construir o corpo da requisição para o Gemini
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": system_prompt},
                            {"text": f"Usuário: {user_input}"}
                        ]
                    }
                ],
                "tools": [
                    {
                        "function_declarations": [
                            {
                                "name": "execute_command",
                                "description": "Executa um comando shell e retorna o resultado",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "command": {
                                            "type": "string",
                                            "description": "O comando shell a ser executado"
                                        }
                                    },
                                    "required": ["command"]
                                }
                            },
                            {
                                "name": "create_file",
                                "description": "Cria um arquivo com o conteúdo especificado",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "filename": {
                                            "type": "string",
                                            "description": "O nome do arquivo a ser criado"
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "O conteúdo a ser escrito no arquivo"
                                        }
                                    },
                                    "required": ["filename", "content"]
                                }
                            },
                            {
                                "name": "read_file",
                                "description": "Lê o conteúdo de um arquivo",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "filename": {
                                            "type": "string",
                                            "description": "O nome do arquivo a ser lido"
                                        }
                                    },
                                    "required": ["filename"]
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(GEMINI_API_URL, headers=headers, json=data)
            response.raise_for_status()
            
            ai_response_json = response.json()
            
            # Verificar se a resposta contém uma chamada de função
            if "candidates" in ai_response_json and len(ai_response_json["candidates"]) > 0:
                candidate = ai_response_json["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "functionCall" in part:
                            function_call = part["functionCall"]
                            function_name = function_call["name"]
                            function_args = function_call["args"]
                            
                            # Executar a função apropriada
                            if function_name == "execute_command":
                                command = function_args.get("command", "")
                                result = self.execute_command(command)
                                
                                if result.get("success"):
                                    if result.get("stdout") or result.get("stderr"):
                                        output = ""
                                        if result.get("stdout"):
                                            output += f"Saída do comando:\n{result.get('stdout')}"
                                        if result.get("stderr"):
                                            output += f"\nErros:\n{result.get('stderr')}"
                                        return {"success": True, "response": output}
                                    else:
                                        return {"success": True, "response": "Comando executado com sucesso (sem saída)."}
                                else:
                                    return {"success": False, "error": result.get("error", "Erro na execução do comando.")}
                            
                            elif function_name == "create_file":
                                filename = function_args.get("filename", "")
                                content = function_args.get("content", "")
                                result = self.create_file(filename, content)
                                
                                if result.get("success"):
                                    response_data = {
                                        "success": True, 
                                        "response": result.get("message")
                                    }
                                    # Adicionar informações de download se disponível
                                    if result.get("download_available"):
                                        response_data["download_info"] = {
                                            "filename": result.get("filename"),
                                            "file_size": result.get("file_size")
                                        }
                                    return response_data
                                else:
                                    return {"success": False, "error": result.get("error")}
                            
                            elif function_name == "read_file":
                                filename = function_args.get("filename", "")
                                result = self.read_file(filename)
                                
                                if result.get("success"):
                                    return {"success": True, "response": f"Conteúdo do arquivo {filename}:\n{result.get('content')}"}
                                else:
                                    return {"success": False, "error": result.get("error")}

                        elif "text" in part:
                            # Se for uma resposta de texto normal
                            response_text = part["text"].strip()
                            return {"success": True, "response": response_text}
            
            # Se não houver chamadas de função nem texto
            return {"success": False, "error": "Resposta inesperada da API do Gemini."}
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Erro na requisição HTTP para o Gemini: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar solicitação: {str(e)}"
            }

# Instância global do sistema
llm_system = MiniLLMSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Mensagem não fornecida"}), 400
    
    # Processar a mensagem
    result = llm_system.process_request(user_message)
    
    return jsonify(result)

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(llm_system.conversation_history)

@app.route('/download/<filename>')
def download_file(filename):
    """Endpoint para download de arquivos criados"""
    try:
        import os
        from flask import send_file, abort
        
        # Verificar se o arquivo existe no diretório de trabalho
        if not os.path.exists(filename):
            abort(404)
        
        # Verificar se é um arquivo (não diretório)
        if not os.path.isfile(filename):
            abort(404)
        
        # Enviar o arquivo para download
        return send_file(filename, as_attachment=True, download_name=filename)
        
    except Exception as e:
        abort(500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

