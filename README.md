# Alexandria
A Biblioteca de Alexandria (em latim: Bibliotheca Alexandrina) foi uma das mais significativas e célebres bibliotecas e um dos maiores centros de produção do conhecimento na Antiguidade. [[Wikipedia](https://pt.wikipedia.org/wiki/Biblioteca_de_Alexandria)]

Esta biblioteca, no entanto, refere-se ao código criado para facilitar a manipulação com conexões de banco de dados na nuvem e com ferramentas comumente usadas na manipulação e análise de dados.

## Pré-Requisitos
- Possuir uma versão [Python 3.6 ou superior](https://www.python.org/downloads/) instalada;
- Configurar a Variável de Ambiente para a pasta onde estão as Credenciais.

Para fazer a configuração da variável de ambiente siga os passos abaixo, de acordo com as instruções a seguir dependendo do seu sistema operacional.

#### Windows
1. Crie uma pasta no local que julgue mais adequado;
2. Na pesquisa do Windows, digite `Variáveis de Ambiente` e clique no resultado do Painel de Controle;
3. Clique no botão `Variáveis de Ambiente...`;
4. Nas **Variáveis de usuário**, clique no botão `Novo`;
5. Em **Nome da variável** digite `CREDENTIALS_HOME` e em **Valor da variável** coloque o caminho para a pasta recém criada;
6. Dê **Ok** nas 3 janelas abertas.

#### Linux/MacOS
1. Crie uma pasta no local que julgue mais adequado;
2. Abra o arquivo `.bashrc`. Se ele não existir, crie um no diretório `HOME`. Se não souber chegar nele, abra o Terminal, digite `cd` e dê **ENTER**;
3. Dentro do arquivo, digite em uma nova linha o comando: `export CREDENTIALS_HOME="/path/to/directory"`, substituindo o conteúdo dentro das aspas pelo caminho para a pasta recém criada;
4. Salve o arquivo e reinicie todas as janelas do Terminal que estiverem abertas.

> **Nota:** Para que esta biblioteca funcione corretamente, é estritamente necessário que o nome da variável de ambiente seja exatamente `CREDENTIALS_HOME`.

## Instalação
*To be defined...*

## Documentação
### S3_Library
*To be defined...*

### RedShift_Library
*To be defined...*

### GCP_Library
*To be defined...*
