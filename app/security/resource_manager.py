import json
from fastapi import Request, HTTPException

class ResourceManager:
    def __init__(self, resource_file="allowed_resources.json"):
        self.resource_file = resource_file
        self.resources = self.load_resources()

    def load_resources(self):
        try:
            with open(self.resource_file, "r") as f:
                data = json.load(f)
                return data.get("resources", [])
        except FileNotFoundError:
            print("[INFO] Archivo de recursos no encontrado, iniciando vacío.")
            return []

    def is_authorized(self, api_key):
        return any(r["api_key"] == api_key for r in self.resources)

    def add_resource(self, name, api_key):
        self.resources.append({"name": name, "api_key": api_key})
        self.save_resources()

    def save_resources(self):
        with open(self.resource_file, "w") as f:
            json.dump({"resources": self.resources}, f, indent=2)


resource_manager = ResourceManager()

async def resource_auth_middleware(request: Request, call_next):
    # Permitir automáticamente si viene de localhost
    client_host = request.client.host    
    if client_host in ("127.0.0.1", "localhost", "::1"):
        return await call_next(request)
    
    api_key = request.headers.get("X-Api-Key")
    if not api_key or not resource_manager.is_authorized(api_key):
        raise HTTPException(status_code=401, detail="Unauthorized resource")
    response = await call_next(request)
    return response
