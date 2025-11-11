entrada = input("Digite algo: ")

try:
    valor = float(entrada)

    if valor % 1 == 0:
        print("int")
    else:
        print("float")

except:
    if len(entrada) == 1:
        print("char")
    else:
        print("string")