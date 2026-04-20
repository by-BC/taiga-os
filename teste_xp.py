from controllers.gamification import adicionar_xp, obter_status_usuario

print("🌲 STATUS INICIAL DO TAIGA OS 🌲")
print(obter_status_usuario())

print("\n------------------------------------")
print("Simulando 1 hora de estudo de Auditoria de Sistemas...")
mensagem = adicionar_xp(100)
print(f"Sistema diz: {mensagem}")

print("\n------------------------------------")
print("Simulando conclusão do curso de Python Backend...")
# Vamos dar 900 XP de uma vez para forçar a passagem de nível (1000 XP = Júnior)
mensagem_level_up = adicionar_xp(900)
print(f"Sistema diz: {mensagem_level_up}")

print("\n------------------------------------")
print("🔥 STATUS FINAL DO TAIGA OS 🔥")
print(obter_status_usuario())
