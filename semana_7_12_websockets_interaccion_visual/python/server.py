import asyncio
import websockets
import json
import random

async def handler(websocket):
    print("Cliente conectado!")
    try:
        while True:
            # Generar datos simulados
            data = {
                "x": random.uniform(-5, 5),
                "y": random.uniform(-5, 5),
                "color": random.choice(["red", "green", "blue", "yellow", "purple"])
            }
            # Enviar los datos serializados en JSON
            await websocket.send(json.dumps(data))
            
            # Esperar medio segundo antes de enviar el siguiente mensaje
            await asyncio.sleep(0.5)
    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado.")

async def main():
    # Iniciar el servidor WebSocket en localhost y el puerto 8765
    print("Iniciando servidor WebSocket en ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Mantiene el servidor corriendo infinitamente

if __name__ == "__main__":
    asyncio.run(main())
