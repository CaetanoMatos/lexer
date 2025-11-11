def tipo_variavel(entrada):
    try:
        valor = float(entrada)
        if valor % 1 == 0:
            return "int"
        else:
            return "float"
    except:
        if len(entrada) == 1:
            return "char"
        else:
            return "string"


v1 = input("Digite o primeiro valor: ")
v2 = input("Digite o segundo valor: ")

t1 = tipo_variavel(v1)
t2 = tipo_variavel(v2)

print(f"Tipo do primeiro valor: {t1}")
print(f"Tipo do segundo valor: {t2}")

if (t1 == "int" and t2 == "int") or (t1 == "float" and t2 == "float"):
    print("Compativel")
else:
    print("Nao compativel")