from app.short_term_memory import ShortTermMemory

memory = ShortTermMemory(max_items=5)

test_data = [
    ("Hola, ¿cómo estás?", "Estoy bien, gracias."),
    ("¿Cuál es tu nombre?", "Soy tu asistente personal."),
    ("Recuérdame comprar leche.", "Ok, lo recordaré."),
    ("¿Qué hora es?", "Son las 10 AM."),
    ("Cuéntame un chiste.", "¿Por qué cruzó el pollo la calle? Para llegar al otro lado."),
    ("¿Cuál es la capital de Francia?", "París es la capital de Francia."),
]

for user, assistant in test_data:
    print(f"Agregando: {user} | {assistant}")
    memory.add_interaction(user, assistant)

memory.save()

query = "¿Cómo te llamas?"
print(f"\nBuscando contexto similar a: '{query}'")
results = memory.query(query, top_k=3)
print("Resultados recuperados:")
for res in results:
    print(" -", res)
