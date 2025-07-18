from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from src.api.endpoints.chat import router as chat_router
import uvicorn

app = FastAPI(title="Colombia RAG Chatbot API", version="1.0.0")

app.include_router(chat_router)


# Endpoint para la documentación Scalar
@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
