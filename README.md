Mini LLM System com Gemini API

Este projeto é um assistente de IA simples, construído com Flask e Python, que utiliza a API do Google Gemini para interpretar as solicitações do usuário e interagir com o sistema local. O assistente pode executar comandos de shell, criar e ler arquivos, além de manter conversas normais.

✨ Funcionalidades

Inteligência Artificial Conversacional: Utiliza o modelo gemini-2.0-flash para entender e responder às solicitações do usuário.

Execução de Comandos: Pode executar comandos de shell (como ls, pwd, echo) diretamente no servidor onde a aplicação está rodando.

Manipulação de Arquivos: Capaz de criar novos arquivos com conteúdo específico e ler o conteúdo de arquivos existentes.

Download de Arquivos: Oferece um endpoint para que o usuário possa baixar os arquivos criados pelo assistente.

Filtro de Segurança: Inclui uma camada de segurança básica que bloqueia a execução de comandos potencialmente perigosos que poderiam afetar o sistema operacional.

Interface Web: Fornecido com um backend Flask pronto para ser integrado a um frontend de chat.

⚙️ Como Funciona

O fluxo da aplicação é o seguinte:

O usuário envia uma mensagem através de uma interface web (frontend).

O backend Flask recebe a mensagem no endpoint /chat.

A mensagem é enviada para a API do Gemini, juntamente com um "prompt de sistema" que instrui o modelo sobre suas capacidades e as ferramentas (execute_command, create_file, read_file) que ele pode usar.

O Gemini analisa a solicitação:

Se for uma pergunta ou conversa, ele gera uma resposta em texto.

Se for uma tarefa (ex: "liste os arquivos"), ele retorna uma "chamada de função" (functionCall) com o nome da ferramenta e os argumentos necessários.

O backend Python executa a função solicitada pelo Gemini (se houver), captura o resultado e o retorna ao usuário.

A resposta final é exibida na interface do usuário.

🚀 Instalação e Configuração

Siga os passos abaixo para executar o projeto em seu ambiente local.

Pré-requisitos

Python 3.7 ou superior

Pip (gerenciador de pacotes do Python)

Uma chave de API do Google Gemini (obtenha em Google AI Studio)

Passos

Clone o repositório:

git clone https://seu-repositorio/mini-llm-system.git
cd mini-llm-system


Crie e ative um ambiente virtual (recomendado):

python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate


Instale as dependências:
Crie um arquivo requirements.txt com o seguinte conteúdo:

Flask
Flask-Cors
requests


E instale-o com o pip:

pip install -r requirements.txt


Configure a sua Chave de API:
Abra o arquivo principal Python (app.py ou similar) e substitua o placeholder "CHAVE DE API" pela sua chave de API do Google Gemini.

# Altere esta linha
GEMINI_API_KEY = "SUA_CHAVE_DE_API_VEM_AQUI"


▶️ Como Executar

Inicie o servidor Flask:

python seu_arquivo.py


Acesse a aplicação:
Abra seu navegador e acesse http://127.0.0.1:5000. Você deverá ver a interface de chat (index.html).

Interaja com o assistente:
Você pode experimentar diferentes tipos de comandos:

Comando de Shell: "Liste os arquivos e pastas no diretório atual."

Criação de Arquivo: "Crie um arquivo chamado 'lista.txt' com o conteúdo: Maçã, Banana, Laranja"

Leitura de Arquivo: "Leia o conteúdo do arquivo 'lista.txt'"

Conversa: "Qual é a capital do Brasil?"

Endpoints da API

GET /: Renderiza a página principal de chat (index.html).

POST /chat: Recebe a mensagem do usuário em formato JSON ({"message": "sua mensagem"}) e retorna a resposta do assistente.

GET /download/<filename>: Permite o download de um arquivo que foi criado na sessão.

⚠️ Nota de Segurança

Este projeto permite a execução de comandos de shell remotamente, o que é uma funcionalidade inerentemente perigosa. Embora exista uma lista de bloqueio para comandos críticos (rm -rf, shutdown, etc.), ela pode não ser exaustiva.

Execute este projeto em um ambiente controlado e isolado. Não o exponha publicamente na internet sem implementar camadas robustas de segurança e autenticação.

Este README foi gerado para auxiliar na documentação e uso do projeto Mini LLM System.
