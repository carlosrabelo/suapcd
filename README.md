# SUAP Coletador de Dados (SUAP-CD)

O **SUAP Coletador de Dados (SUAP-CD)** é uma aplicação standalone desenvolvida em Python para otimizar a conferência de patrimônio no Sistema Unificado de Administração Pública (SUAP). A ferramenta supre a ausência de uma funcionalidade nativa no SUAP para verificação eficiente de bens patrimoniais, utilizando arquivos CSV exportados pelo sistema e uma pistola de leitura de código de barras sem fio. O SUAP-CD é executado em um notebook, com uma interface gráfica intuitiva, e possui perspectiva de integração futura com tecnologia NFC para leitura por proximidade.

## Funcionalidades

- **Importação de Dados**: Carrega arquivos CSV gerados pelo SUAP, contendo informações como número do patrimônio, descrição, sala e estado de conservação.
- **Escaneamento de Patrimônios**: Utiliza uma pistola de leitura de código de barras sem fio para marcar bens como encontrados ou registrar itens não cadastrados em tempo real.
- **Interface Gráfica**: Interface amigável desenvolvida com PyQt5, com tabelas filtráveis para salas e patrimônios, campos de busca e botões para escaneamento e geração de relatórios.
- **Geração de Relatórios**: Produz relatórios CSV detalhados, organizados por sala e geral, incluindo patrimônios encontrados, não encontrados, divergentes e não cadastrados.
- **Gerenciamento de Banco de Dados**: Armazena dados em um banco SQLite, com módulos para gerenciamento de salas, patrimônios e itens não cadastrados.
- **Modularidade**: Arquitetura dividida em módulos (`DatabaseManager`, `MainWindow`, `ScanWindow`, `ReportGenerator`) para facilitar manutenção e evolução.
- **Perspectiva de NFC**: Planejamento para integração futura com tecnologia NFC, permitindo leitura de patrimônios por proximidade.

## Requisitos

### Software
- Python 3.7 ou superior
- Bibliotecas Python:
  - PyQt5==5.15.9
  - PyInstaller==6.10.0 (opcional, para gerar executáveis)
- Sistema operacional: Windows ou Linux

### Hardware
- Notebook com Windows ou Linux
- Pistola de leitura de código de barras sem fio (compatível como dispositivo de entrada de texto)

## Instalação

1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/carlosrabelo/suap-cd.git
   cd suap-cd
   ```

2. **Crie um Ambiente Virtual** (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux
   venv\Scripts\activate     # Windows
   ```

3. **Instale as Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a Aplicação**:
   ```bash
   python app.py
   ```

5. **(Opcional) Gere um Executável**:
   Para criar um executável standalone com PyInstaller:
   ```bash
   pyinstaller --onefile --windowed app.py
   ```
   O executável será gerado na pasta `dist/`.

## Uso

1. **Iniciar a Aplicação**:
   Execute `python app.py` ou o executável gerado. A interface gráfica será aberta maximizada.

2. **Importar Arquivo CSV**:
   Para carregar dados do SUAP, execute:
   ```bash
   python app.py -load caminho/para/arquivo.csv
   ```
   Isso importa os dados e encerra a aplicação. Para uso interativo, inicie sem o argumento `-load`.

3. **Filtrar Salas**:
   Na interface principal, use o campo de filtro para buscar salas por nome. Selecione uma sala na tabela para visualizar os patrimônios associados.

4. **Escanear Patrimônios**:
   Clique em "Escanear Patrimônios" com uma sala selecionada. Na janela de escaneamento, use a pistola de leitura para escanear códigos de barras. O sistema marca os itens como encontrados ou registra itens não cadastrados.

5. **Gerar Relatórios**:
   Clique em "Gerar Relatório" para criar arquivos CSV com informações detalhadas, salvos em um diretório específico (`%APPDATA%\SUAP-CD\report` no Windows ou `/var/lib/suapcd/report` no Linux).

6. **Filtrar Patrimônios**:
   Use o menu dropdown para filtrar patrimônios por status ("Todos", "Encontrados", "Não Encontrados").

## Estrutura do Projeto

- `app.py`: Ponto de entrada da aplicação, inicializa a interface gráfica e gerencia argumentos de linha de comando.
- `main_window.py`: Define a janela principal da interface gráfica, com tabelas e controles.
- `scan_window.py`: Implementa a janela de escaneamento de códigos de barras.
- `database.py`: Contém a classe `DatabaseManager` para gerenciamento do banco SQLite e importação de CSV.
- `report_generator.py`: Gera relatórios CSV com base nos dados do banco.
- `requirements.txt`: Lista de dependências do projeto.

## Contribuição

Este projeto foi desenvolvido por **Carlos Roberto Rabelo Machado** como programador principal, com a colaboração de:

- **Leonardo Teofilo Pignati**
- **Marcella Silva dos Santos Guimarães**

Contribuições são bem-vindas! Para contribuir:
1. Fork o repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`).
3. Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`).
4. Push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um Pull Request.

Por favor, siga as diretrizes de código e inclua testes para novas funcionalidades.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE). Veja o arquivo `LICENSE` para mais detalhes.

## Contato

Para dúvidas ou sugestões, entre em contato com o desenvolvedor principal:

- **Carlos Roberto Rabelo Machado**  
  Email: contato@carlosrabelo.com.br  
  GitHub: [carlosrabelo](https://github.com/carlosrabelo)

---

Desenvolvido no âmbito do Instituto Federal de Educação, Ciência e Tecnologia de Mato Grosso (IFMT), Campus Cuiabá - Bela Vista, como parte de um projeto de estágio supervisionado.