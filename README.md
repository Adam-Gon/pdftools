# PDFTools 🛠️

Uma plataforma web de ferramentas para manipulação de PDFs. Construída com Flask e pypdf, com arquitetura modular que facilita a adição de novas ferramentas.

**[🌐 Acesse o projeto ao vivo](https://pdftools-wsq1.onrender.com)**

---

## Funcionalidades

| Ferramenta | Descrição |
|---|---|
| 🔗 Unir PDFs | Combine múltiplos PDFs em um único arquivo com reordenamento por arrastar |
| ✂️ Dividir PDF | Separe todas as páginas ou extraia um intervalo específico (ex: 1-3, 5) |
| 🔄 Girar PDF | Gire todas as páginas em 90°, 180° ou 270° |
| 📝 Extrair Texto | Extraia todo o texto de um PDF em formato .txt |
| 🖼️ Imagens para PDF | Converta JPG, PNG, WEBP e outros formatos em um único PDF com reordenamento |

---

## Tecnologias

- **Backend:** Python + Flask
- **Manipulação de PDF:** pypdf + reportlab
- **Processamento de imagens:** Pillow
- **Frontend:** HTML, CSS e JavaScript puro
- **Hospedagem:** Render (free tier) + UptimeRobot

---

## Arquitetura

O projeto foi construído com um padrão de **plugins** — cada ferramenta é um módulo independente que herda de uma classe base. Isso permite adicionar novas ferramentas sem modificar o código existente.

```
pdftools/
├── app.py                  # Servidor Flask e rotas da API
├── tools/
│   ├── __init__.py         # Registro de ferramentas ← adicione novas aqui
│   ├── base.py             # Classe base PDFTool
│   ├── merge.py            # Unir PDFs
│   ├── split.py            # Dividir PDF
│   ├── rotate.py           # Girar PDF
│   ├── extract_text.py     # Extrair Texto
│   └── images_to_pdf.py    # Imagens para PDF
└── templates/
    └── index.html          # Frontend completo
```

---

## Licença

Projeto acadêmico de uso livre.
