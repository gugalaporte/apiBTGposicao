from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import json
import os
from pathlib import Path
import httpx
import asyncio

app = FastAPI(title="BTG Positions Webhook")

# Criar diretório para armazenar os arquivos JSON
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Configurações da API BTG
BTG_API_URL = "https://api.btgpactual.com/iaas-api-position/api/v1/position/partner"
API_KEY = "finacap2025"

class Error(BaseModel):
    code: Optional[str] = None
    message: Optional[str] = None

class PositionData(BaseModel):
    accountNumber: Optional[str] = None
    fileSize: int
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    url: str

class WebhookPayload(BaseModel):
    errors: List[Error]
    response: PositionData

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")
    return x_api_key

def save_to_json(data: dict):
    # Criar nome do arquivo baseado no timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = DATA_DIR / f"position_{timestamp}.json"
    
    # Adicionar timestamp de recebimento
    data["received_at"] = datetime.now().isoformat()
    
    # Salvar dados em arquivo JSON
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

@app.get("/positions/partner")
async def get_partner_positions(
    api_key: str = Depends(verify_api_key)
):
    """
    Endpoint para buscar posições do parceiro.
    Faz uma chamada para a API do BTG e retorna os dados.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BTG_API_URL,
                headers={"X-API-Key": api_key}
            )
            response.raise_for_status()
            data = response.json()
            
            # Salvar resposta em arquivo
            filename = save_to_json(data)
            
            return {
                "status": "success",
                "data": data,
                "file": str(filename)
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar posições: {str(e)}")

@app.post("/positions/partner/refresh")
async def refresh_partner_positions(
    api_key: str = Depends(verify_api_key)
):
    """
    Endpoint para atualizar as posições do parceiro.
    Faz uma chamada POST para atualizar os dados antes de buscar.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Primeiro, atualiza os dados
            refresh_response = await client.post(
                f"{BTG_API_URL}/refresh",
                headers={"X-API-Key": api_key}
            )
            refresh_response.raise_for_status()
            
            # Aguarda um momento para garantir que os dados foram atualizados
            await asyncio.sleep(2)
            
            # Depois, busca os dados atualizados
            return await get_partner_positions(api_key)
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar posições: {str(e)}")

@app.post("/webhook/positions")
async def receive_positions(
    data: WebhookPayload,
    api_key: str = Depends(verify_api_key)
):
    """
    Endpoint da webhook para receber atualizações de posições.
    
    Exemplo de payload:
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
    """
    try:
        # Converter os dados para dicionário
        data_dict = data.dict()
        
        # Salvar em arquivo JSON
        filename = save_to_json(data_dict)
        
        return {
            "status": "success", 
            "message": "Dados recebidos e salvos com sucesso",
            "file": str(filename)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 