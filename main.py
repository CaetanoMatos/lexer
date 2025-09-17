import ply.lex as lex

# lista de tokens
tokens = [
    'DERIVAR', 'INTEGRAR', 'ATRIBUIR', 'MOSTRAR',
    'ID', 'NUMBER',
    'OP', 'LPAREN', 'RPAREN', 'EQUALS'
]
#palavras reservadas
t_DERIVAR = r'derivar'
t_INTEGRAR = r'integrar'
t_ATRIBUIR = r'atribuir'
t_MOSTRAR = r'mostrar'
t_OP = r'\+|\-|\*|\/|\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='

# variaveis / simbolos
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # ve se é palavra-chave
    if t.value == 'derivar':
        t.type = 'DERIVAR'
    elif t.value == 'integrar':
        t.type = 'INTEGRAR'
    elif t.value == 'atribuir':
        t.type = 'ATRIBUIR'
    elif t.value == 'mostrar':
        t.type = 'MOSTRAR'
    return t

# confere se é numero
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# ignorar os espaços e tabulações pra evitar confusão
t_ignore = ' \t'

# caso encontre algum caractere que nao corresponda a nenhuma regra gramatical, chama essa função
def t_error(t):
    print(f"Caracter ilegal: {t.value[0]}")
    t.lexer.skip(1)

# lexer
lexer = lex.lex()

# exemplo teste
entrada = "atribuir resultado = derivar x + 2 * integrar y"
lexer.input(entrada)

for tok in lexer:
    print(tok)
