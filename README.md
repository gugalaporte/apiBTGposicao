# API Webhook BTG Positions

API para receber e processar dados de posições do BTG via webhook.

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando a aplicação

1. Inicie o servidor:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. A API estará disponível em `http://localhost:8000`

## Endpoints

### POST /webhook/positions
Recebe os dados da webhook do BTG e salva em arquivo JSON.

Headers necessários:
- `X-API-Key: finacap2025`

Body (JSON):
```json
{
  "errors": [
    {
      "code": null,
      "message": null
    }
  ],
  "response": {
    "accountNumber": null,
    "fileSize": 12,
    "startDate": null,
    "endDate": null,
    "url": "https://invest-reports-dev.s3.amazonaws.com/iaas-aws-position-api/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  }
}
```

Os dados são salvos em arquivos JSON na pasta `data/` com o formato:
- Nome do arquivo: `position_YYYYMMDD_HHMMSS.json`
- Cada arquivo contém os dados recebidos mais um timestamp de quando foram recebidos

## Documentação da API

A documentação interativa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 