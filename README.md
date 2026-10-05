# 📊 Painel Estatístico & Mapeamento Eleitoral - Mauriti/CE
> **76ª Zona Eleitoral | Eleição Ordinária Federal**

Sistema completo de extração, estruturação e visualização tático-estatística dos dados de urnas eletrônicas para todas as seções eleitorais do município de **Mauriti/CE**.

---

## 📌 Visão Geral do Projeto

Este projeto realiza a raspagem automatizada dos dados de boletins de urna do Tribunal Superior Eleitoral (TSE) para as **161 seções eleitorais** de Mauriti/CE (sendo 140 seções ativas e 21 seções agregadas devidamente tratadas). 

Os dados de votação foram cruzados com a relação oficial de locais de votação, escolas e endereços extraídos do documento `LOCAIS DE VOTAÇÃO - SEÇÕES E APTOS.pdf`, agrupando a cidade em **14 distritos e bairros** para análise de desempenho e tomada de decisão de campo.

---

## 📈 Resumo Estatístico da Cidade (140 Seções Ativas)

| Métrica | Total | Percentual / Detalhes |
| :--- | :---: | :---: |
| **Eleitores Aptos** | **36.549** | 100,00% |
| **Comparecimento** | **30.378** | 83,12% |
| **Abstenção / Faltosos** | **6.174** | 16,89% |
| **Votos Válidos** | **28.917** | 95,19% dos votos apurados |
| **Votos Brancos** | **604** | 1,99% |
| **Votos Nulos** | **1.710** | 5,63% |

### 🗳️ Votação para Presidente
* 🔴 **13 - LULA**: **20.987 votos** (**72,58%** dos votos válidos)
* 🔵 **22 - FLÁVIO BOLSONARO**: **7.084 votos** (**24,50%**)
* 🟡 **70 - AUGUSTO CURY**: **369 votos** (**1,28%**)
* 🟣 **14 - RENAN SANTOS**: **368 votos** (**1,27%**)
* 🟠 **55 - RONALDO CAIADO**: **109 votos** (**0,38%**)
* ⚙️ **Total Oposição**: **7.930 votos** (**27,42%**)

---

## 📍 Diagnóstico por Distrito / Bairro (14 Regiões)

| Distrito / Bairro | Seções | Aptos | Faltosos | Lula (13) | Oposição Total | % Lula | Classificação Estatística |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Bairro Serrinha** | 9 | 2.126 | 350 | 1.053 | 619 | **62,98%** | 🎯 Margem Moderada (Menor % Lula) |
| **Bairro Bela Vista** | 10 | 3.147 | 550 | 1.586 | 884 | **64,21%** | 🎯 Margem Moderada (Alta Oposição) |
| **Bairro Populares** | 1 | 346 | 55 | 183 | 95 | **65,83%** | ⚠️ Margem Moderada |
| **Centro** | 23 | 5.918 | 847 | 3.249 | 1.625 | **66,66%** | ⚡ Maioria Absoluta |
| **Sede / Outros** | 7 | 1.742 | 363 | 949 | 361 | **72,44%** | ⚡ Maioria Absoluta |
| **Distrito de São Miguel** | 8 | 2.121 | 387 | 1.192 | 442 | **72,95%** | ⚡ Maioria Absoluta |
| **Distrito de São Félix** | 5 | 1.221 | 263 | 674 | 232 | **74,39%** | ⚡ Maioria Absoluta |
| **Distrito de Palestina do Cariri** | 19 | 5.110 | 866 | 3.029 | 1.042 | **74,40%** | ⚡ Maioria Absoluta |
| **Distrito de Anauá** | 5 | 1.506 | 364 | 825 | 276 | **74,93%** | ⚡ Maioria Absoluta |
| **Zona Rural / Sítios** | 13 | 2.885 | 418 | 1.774 | 590 | **75,04%** | 📊 Ampla Maioria (≥75%) |
| **Distrito de Umburanas** | 12 | 3.353 | 537 | 2.020 | 607 | **76,89%** | 📊 Ampla Maioria (≥75%) |
| **Distrito de Buritizinho** | 15 | 3.700 | 614 | 2.267 | 655 | **77,58%** | 📊 Ampla Maioria (≥75%) |
| **Distrito de Coité** | 11 | 2.916 | 463 | 1.884 | 460 | **80,38%** | 📊 Ampla Maioria (≥75%) |
| **Distrito de Nova Santa Cruz** | 2 | 457 | 97 | 302 | 42 | **87,79%** | 📊 Ampla Maioria (≥75%) |

---

## 📂 Estrutura de Arquivos

```
Eleicoes-mauriti/
├── scraper_eleicoes_mauriti.py       # Script principal de raspagem e cruzamento de dados
├── dados_eleicoes_mauriti.json       # Dataset completo estruturado (seções + distritos + metadata)
├── index.html                        # Painel web interativo (Dark Mode + 100% Mobile Responsive)
├── painel_tatico.html                # Espelho do painel de visualização tática
├── LOCAIS DE VOTAÇÃO - SEÇÕES E APTOS.pdf # Documento original de locais e endereços do TSE
├── rota.txt                          # Script de seções e modelo de URL das urnas
└── README.md                         # Documentação do projeto
```

---

## 🚀 Como Executar o Scraper & Visualizar o Painel

### 1. Executar o Script de Raspagem (Python)
Para reexecutar a raspagem completa e atualizar os dados diretamente das APIs do TSE e do PDF:
```bash
python scraper_eleicoes_mauriti.py
```

### 2. Visualização do Painel Web
Abra o arquivo [`index.html`](file:///c:/Users/eric0/OneDrive/%C3%81rea%20de%20Trabalho/Eleicoes-mauriti/index.html) diretamente no seu navegador de preferência (Chrome, Edge, Firefox, Safari ou navegadores mobile).

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.14**: Raspagem de APIs do TSE, parsing de PDF (`pypdf`), estruturação de dados.
* **Selenium / Chrome Headless**: Extração automatizada de boletins de urna.
* **HTML5, Vanilla CSS3 & Modern JavaScript (ES6+)**: Interface do painel web.
* **Google Fonts (Plus Jakarta Sans & Space Grotesk)**: Tipografia.

---

## 📄 Licença
Dados públicos obtidos a partir dos repositórios oficiais do **Tribunal Superior Eleitoral (TSE)**.
