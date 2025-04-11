# Manual da Aplicação

Este guia descreve como preparar o ambiente da aplicação até a sua execução.

## 📌 Pré-requisitos

- 🔹 Ter o [Conda](https://docs.conda.io/en/latest/miniconda.html) ou [Miniconda](https://docs.conda.io/en/latest/miniconda.html) instalado em seu sistema.
- 🔹 Acesso ao terminal ou prompt de comando.

## 🚀 Passos para ativar o ambiente

### 1️⃣ Navegue até a pasta onde o arquivo `environment.yml` está localizado
```sh
cd ~/.conda
```
Se estiver no Windows, use:
```sh
cd %USERPROFILE%\.conda
```

### 2️⃣ Crie o ambiente Conda a partir do arquivo `environment.yml`
```sh
conda env create -f environment.yml
```

### 3️⃣ Ative o ambiente criado
```sh
conda activate nome_do_ambiente
```
📝 *Substitua `nome_do_ambiente` pelo nome do ambiente especificado dentro do arquivo `environment.yml`.*

### 4️⃣ Verifique se o ambiente está ativado
```sh
conda info --envs
```
O ambiente ativo será indicado com um `*` ao lado do nome.

### 5️⃣ Execute o aplicativo Streamlit
Se o ambiente estiver corretamente ativado, execute o seguinte comando para iniciar o aplicativo Streamlit:
```sh
streamlit run .\streamlit_app.py
```

## 🔧 Outros Comandos Úteis

- **Atualizar o ambiente com base no arquivo `environment.yml`**:
  ```sh
  conda env update -f environment.yml
  ```

- **Remover o ambiente caso não seja mais necessário**:
  ```sh
  conda env remove -n nome_do_ambiente
  ```

