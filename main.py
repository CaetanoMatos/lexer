import ply.lex as lex

# lista de tokens
tokens = [
    'DERIVAR', 'INTEGRAR', 'ATRIBUIR', 'MOSTRAR',
    'ID', 'NUMBER',
    'OP', 'LPAREN', 'RPAREN', 'EQUALS'
]

# palavras reservadas
t_DERIVAR = r'derivar'
t_INTEGRAR = r'integrar'
t_ATRIBUIR = r'atribuir'
t_MOSTRAR = r'mostrar'
t_OP = r'\+|\-|\*|\/|\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value == 'derivar':
        t.type = 'DERIVAR'
    elif t.value == 'integrar':
        t.type = 'INTEGRAR'
    elif t.value == 'atribuir':
        t.type = 'ATRIBUIR'
    elif t.value == 'mostrar':
        t.type = 'MOSTRAR'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Caracter ilegal: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()

print("Digite uma expressão para análise léxica.")
print("Exemplo de entrada: atribuir resultado = derivar x + 2 * integrar y")
entrada = input("Expressão: ")

lexer.input(entrada)

print(f"{'Tipo':12} {'Valor':15} {'Linha':5} {'Coluna':6}")
print("-" * 40)
for tok in lexer:
    print(f"{tok.type:12} {str(tok.value):15} {tok.lineno:<5} {tok.lexpos:<6}")
