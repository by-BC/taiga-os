<div align="center">

# 🌲 Taiga OS

**Um sistema operacional pessoal para produtividade e autodesenvolvimento**

![Python](https://img.shields.io/badge/Python-3.11+-3D6050?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-2F4F3E?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Local-4E6B50?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-7A9E7A?style=for-the-badge)

</div>

---

## ✨ Sobre o projeto

O **Taiga OS** é um app desktop pessoal construído com Python e CustomTkinter, inspirado no conceito de *Personal Operating System* — um painel centralizado para gerenciar tarefas, hábitos, estudos e foco no dia a dia.

O design segue um tema florestal escuro (`#1E201C`) com acentos em verde e laranja, criando uma interface que remete à serenidade das florestas boreais.

---

## 🖥️ Funcionalidades

| Módulo | Descrição |
|---|---|
| 📊 **Dashboard** | Visão geral do dia: métricas, tarefas pendentes e resumo semanal |
| 📝 **Daily Log** | Registro diário de humor, água, sono e horas de estudo |
| 📚 **Academic Hub** | Acompanhamento de cursos com barras de progresso e links externos |
| 📋 **Kanban** | Quadro de tarefas em colunas: A Fazer → Fazendo → Concluído |
| 🍅 **Pomodoro** | Timer integrado de 25/5 min com contagem de ciclos |

### 🎮 Sistema de Gamificação

Cada ação no sistema gera **XP** e avança seu nível:

| Ação | XP |
|---|---|
| Concluir tarefa | +20 XP |
| Hora de estudo (Daily Log) | +100 XP por hora |
| Rotina completa | +50 XP bônus |
| Hidratação ≥ 2L | +10 XP |
| Sono ≥ 7h | +10 XP |
| Concluir um curso | +500 XP |

**Níveis:** 🌱 Semente → 🌿 Broto → 🌳 Árvore → 🌲 Floresta → 🏔️ Montanha → ⭐ Guardião

---

## 🚀 Como rodar

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/taiga-os.git
cd taiga-os

# 2. (Opcional) Crie um ambiente virtual
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute
python main.py
```

O banco de dados `taiga_os.db` é criado automaticamente na primeira execução.

---

## 📁 Estrutura do projeto

```
taiga-os/
├── main.py                  # Ponto de entrada
├── database.py              # Conexão SQLite e criação de tabelas
├── requirements.txt
├── controllers/
│   ├── gamification.py      # XP, níveis e streak
│   ├── tasks.py             # CRUD de tarefas
│   ├── daily_log.py         # Registro de hábitos
│   └── courses.py           # Gestão de cursos
└── views/
    ├── theme.py             # Design tokens (cores, fontes, espaçamentos)
    ├── components.py        # Componentes reutilizáveis
    ├── main_window.py       # Janela principal + sidebar
    ├── dashboard_view.py
    ├── daily_view.py
    ├── academic_view.py
    ├── kanban_view.py
    └── pomodoro_view.py
```

---

## 🛠️ Tecnologias

- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** — UI moderna sobre Tkinter
- **SQLite3** — banco de dados local, nativo do Python
- **Python 3.11+** — sem dependências externas além do CustomTkinter

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
