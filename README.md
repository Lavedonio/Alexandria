# Alexandria
A Biblioteca de Alexandria (em latim: Bibliotheca Alexandrina) foi uma das mais significativas e célebres bibliotecas e um dos maiores centros de produção do conhecimento na Antiguidade. [[Wikipedia](https://pt.wikipedia.org/wiki/Biblioteca_de_Alexandria)]

Esta biblioteca, no entanto, refere-se ao código criado para facilitar a manipulação com conexões de banco de dados na nuvem e com ferramentas comumente usadas na manipulação e análise de dados.

## Sumário

- [Pré-Requisitos](https://github.com/Lavedonio/alexandria#pr%C3%A9-requisitos)
- [Instalação](https://github.com/Lavedonio/alexandria#instala%C3%A7%C3%A3o)
- [Documentação](https://github.com/Lavedonio/alexandria#documenta%C3%A7%C3%A3o)
	- [BigQuery_Library](https://github.com/Lavedonio/alexandria#bigquery_library)
	- [GCloudStorage_Library](https://github.com/Lavedonio/alexandria#gcloudstorage_library)
	- [RedShift_Library](https://github.com/Lavedonio/alexandria#redshift_library)
	- [S3_Library](https://github.com/Lavedonio/alexandria#s3_library)

## Pré-Requisitos
1. Possuir uma versão [Python 3.6 ou superior](https://www.python.org/downloads/) instalada;
2. Criar um arquivo YAML com as credenciais;
3. Configurar a Variável de Ambiente para o arquivo onde estão as Credenciais.

### 1. Possuir uma versão Python 3.6 ou superior instalada
Entre no [link](https://www.python.org/downloads/) e baixe a versão mais atual que seja compatível com o pacote.

### 2. Criar um arquivo YAML com as credenciais

Utilize os arquivos [secret_template.yml](https://github.com/Lavedonio/alexandria/blob/master/credentials/secret_template.yml) ou [secret_blank.yml](https://github.com/Lavedonio/alexandria/blob/master/credentials/secret_blank.yml) como base ou copie e cole o código abaixo como base e modifique os valores para os das suas credenciais e projetos:

```
#################################################################
#                                                               #
#        ACCOUNTS CREDENTIALS. DO NOT SHARE THIS FILE.          #
#                                                               #
# Specifications:                                               #
# - For the credentials you don't have, leave it blank.         #
# - Keep Google's secret file in the same folder as this file.  #
# - BigQuery project_ids must be strings, i.e., inside quotes.  #
#                                                               #
# Recommendations:                                              #
# - YAML specification: https://yaml.org/spec/1.2/spec.html     #
# - Keep this file in a static path like a folder within the    #
# Desktop. Ex.: C:\Users\USER\Desktop\Credentials\secret.yml    #
#                                                               #
#################################################################


Google:
  secret_filename: file.json

BigQuery:
  project_id:
    project_name: "000000000000"

AWS:
  access_key: AWSAWSAWSAWSAWSAWSAWS
  secret_key: ÇçasldUYkfsadçSDadskfDSDAsdUYalf

RedShift:
  cluster_credentials:
    dbname: db
    user: masteruser
    host: blablabla.random.us-east-2.redshift.amazonaws.com
    cluster_id: cluster
    port: 5439
  master_password:
    dbname: db
    user: masteruser
    host: blablabla.random.us-east-2.redshift.amazonaws.com
    password: masterpassword
    port: 5439
```
Salve este arquivo com a extensão `.yml` em um local que o caminho não será modificado, como uma pasta no Desktop (Exemplo: `C:\Users\USER\Desktop\Credentials\secret.yml`).

Para fazer a configuração da variável de ambiente siga os passos abaixo, de acordo com as instruções a seguir dependendo do seu sistema operacional.

#### Windows
1. Coloque o arquivo YAML numa pasta no local que julgar mais adequado;
2. Na pesquisa do Windows, digite `Variáveis de Ambiente` e clique no resultado do Painel de Controle;
3. Clique no botão `Variáveis de Ambiente...`;
4. Nas **Variáveis de usuário**, clique no botão `Novo`;
5. Em **Nome da variável** digite `CREDENTIALS_HOME` e em **Valor da variável** coloque o caminho para o arquivo YAML na pasta recém criada;
6. Dê **Ok** nas 3 janelas abertas.

#### Linux/MacOS
1. Coloque o arquivo YAML numa pasta no local que julgar mais adequado;
2. Abra o arquivo `.bashrc`. Se ele não existir, crie um no diretório `HOME`. Se não souber chegar nele, abra o Terminal, digite `cd` e dê **ENTER**;
3. Dentro do arquivo, digite em uma nova linha o comando: `export CREDENTIALS_HOME="/path/to/file"`, substituindo o conteúdo dentro das aspas pelo caminho para o arquivo YAML na pasta recém criada;
4. Salve o arquivo e reinicie todas as janelas do Terminal que estiverem abertas.

> **Nota:** Para que esta biblioteca funcione corretamente, é estritamente necessário que o nome da variável de ambiente seja exatamente `CREDENTIALS_HOME`.

## Instalação
Vá ao terminal e digite:

    pip install -i https://test.pypi.org/simple/ alexandria-lavedonio

## Documentação
### BigQuery_Library
*To be defined...*

### GCloudStorage_Library
*To be defined...*

### RedShift_Library
*To be defined...*

### S3_Library
*To be defined...*

