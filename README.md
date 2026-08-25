# Portal Publico

Portal desenvolvido em Streamlit para validação de arquivos em formato CSV referentes à prestação de contas (inserção, alteração e exclusão), destinados ao processo de desbloqueio do painel OSINFO, conforme o fluxo estabelecido.

## Pré-requisitos

- Python 3.11 ou superior
- Git
- (Opcional) [Conda](https://docs.conda.io/en/latest/miniconda.html) / Miniconda

## Instalação

Clone o repositório e entre na pasta do projeto:

```sh
cd portal-publico
```

### Opção 1 — pip (recomendada)

```sh
python -m venv .venv
```

Windows:

```sh
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux / macOS:

```sh
source .venv/bin/activate
pip install -r requirements.txt
```

### Opção 2 — Conda

O arquivo do ambiente está em `.conda/environment.yml` (nome do ambiente: `portal`).

```sh
conda env create -f .conda/environment.yml
conda activate portal
```

Atualizar o ambiente depois:

```sh
conda env update -f .conda/environment.yml
```

## Configuração de secrets

A aplicação usa `.streamlit/secrets.toml` para credenciais. Esse arquivo **não vai no Git**.

1. Copie o modelo:

Windows:

```sh
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Linux / macOS:

```sh
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

2. Preencha as chaves abaixo (ou deixe os placeholders se for só desenvolvimento).

| Seção | Chave | Obrigatório em produção | Para que serve |
| --- | --- | --- | --- |
| `[general]` | `environment` | Sim | `development` ou `production` |
| `[google]` | `type` | Sim | Sempre `service_account` |
| `[google]` | `project_id` | Sim | Projeto GCP do BigQuery |
| `[google]` | `private_key_id` | Sim | ID da chave da service account |
| `[google]` | `private_key` | Sim | Chave privada PEM (`\n` nas quebras de linha) |
| `[google]` | `client_email` | Sim | E-mail da service account |
| `[google]` | `client_id` | Sim | ID do cliente OAuth |
| `[google]` | `auth_uri` | Sim | `https://accounts.google.com/o/oauth2/auth` |
| `[google]` | `token_uri` | Sim | `https://oauth2.googleapis.com/token` |
| `[google]` | `auth_provider_x509_cert_url` | Sim | `https://www.googleapis.com/oauth2/v1/certs` |
| `[google]` | `client_x509_cert_url` | Sim | URL do certificado da service account |
| `[google]` | `universe_domain` | Sim | `googleapis.com` |
| `[connections.supabase]` | `SUPABASE_URL` | Sim | URL do projeto (`https://….supabase.co`) |
| `[connections.supabase]` | `SUPABASE_KEY` | Sim | Chave `anon` / `public` |
| `[connections.supabase]` | `SUPABASE_SERVICE_KEY` | Recomendado | Chave `service_role` (bypassa RLS nos logs) |

O JSON da service account sai do Google Cloud Console (IAM → Contas de serviço → Chaves).  
URL e chaves do Supabase saem de Project Settings → API.

No Streamlit Cloud, as mesmas chaves podem ser coladas em **App settings → Secrets** (mesmo formato TOML).

## Modo development (sem Supabase / BigQuery)

Se você não tem acesso ao Supabase nem à service account do BigQuery (ou não possui as permissões necessárias nos datasets), não se preocupe: é possível rodar o projeto em modo de desenvolvimento.

Basta seguir estes passos:

1. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml`
2. Certifique-se de que `environment = "development"` está definido (já é o valor padrão do modelo)
3. Mantenha as chaves com valores de placeholder, caso não possua credenciais reais

Como alternativa, você pode definir a variável de ambiente `ENVIRONMENT=development` antes de iniciar o Streamlit.

Nesse modo, a aplicação **inicia normalmente**, porém ficam desativados:

- logs de uso no Supabase
- validações extras contra o datalake (BigQuery)

Todas as validações locais dos arquivos (regras de formato, campos obrigatórios etc.) continuam funcionando normalmente. Listas de secretarias/instituições usam um fallback interno.

Para produção, altere para `environment = "production"` e preencha as credenciais reais.

## Executar

Com o ambiente ativado, na raiz do repositório:

```sh
streamlit run streamlit_app.py
```

A interface abre em `http://localhost:8501`.

## Comandos úteis (Conda)

```sh
conda info --envs
conda env remove -n portal
```
