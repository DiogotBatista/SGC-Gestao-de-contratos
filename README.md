# 📑 SGC - Sistema de Gestão de Contratos

Sistema web desenvolvido em Django para gestão de contratos, obras, atas de reunião e anotações internas. Ideal para empresas que desejam centralizar e monitorar o andamento dos seus contratos de forma prática e visual.

---

## 🚀 Funcionalidades

- 🔐 **Autenticação de usuários com controle de acesso por cargo**
- 📁 **CRUD completo para:**
  - Contratos
  - Contratantes
  - Obras
  - Atas de reunião
  - Anotações gerais por contrato
- 📊 **Dashboard resumo nos detalhes do contrato:**
  - Quantidade de atas
  - Total de itens
  - Itens pendentes vs concluídos
  - Última ata registrada
- 📌 **Itens das atas com categorias personalizáveis**
- 📋 **Ordenação dinâmica dos itens via drag-and-drop**
- 📝 **Sistema de anotações internas por contrato**
- 📂 **Agrupamento de atas por contrato**
- 🎨 Interface moderna, responsiva e intuitiva

---

## 💻 Tecnologias Utilizadas

- **Backend:** Django 4+
- **Frontend:** HTML, Bootstrap 5, JavaScript (SortableJS para reordenamento)
- **Banco de dados:** SQLite (em produção, pode ser alterado para PostgreSQL)
- **Autenticação:** Sistema de login com permissão por grupo/cargo

---

## 📸 Prints (em breve)



---

## ⚙️ Instalação e Execução Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/SGC-Gestao-de-contratos.git
cd nome-do-repositorio

# Crie o ambiente virtual
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

# Instale as dependências
pip install -r requirements.txt

# Aplique as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# Inicie o servidor
python manage.py runserver
```

---

## 🧠 Organização do Projeto

```bash
sgc/
├── contratos/         # App principal de contratos, obras e contratantes
├── reunioes/          # App para gerenciamento de atas e itens
├── core/              # App com mixins, filtros personalizados, autenticação
├── templates/         # Templates organizados por app
├── static/            # Arquivos estáticos (CSS, JS, ícones)
└── manage.py
```

---

## 🛠️ To-Do Futuro

- Integração com dashboards externos via iframe
- Upload de arquivos por ata
- Filtros avançados nas listagens
- Notificações por e-mail (status pendentes)
- Internacionalização

---

## 📃 Licença

Este projeto está sob a licença [MIT](https://choosealicense.com/licenses/mit/).

---

## 🤝 Contribuindo

Sinta-se à vontade para abrir issues ou PRs. Sugestões são muito bem-vindas!

---

## 🙋‍♂️ Autor

Desenvolvido por **Diogo Tadeu Batista**  
📧 diogo.batista@dbsistemas.com.br