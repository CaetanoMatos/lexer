import ply.lex as lex
import ply.yacc as yacc
import sympy as sp
from sympy import Symbol, diff, integrate

# =====================
# ANALISADOR LÉXICO
# =====================
tokens = [
    'DERIVAR', 'INTEGRAR', 'ATRIBUIR', 'MOSTRAR',
    'ID', 'NUMBER',
    'OP', 'LPAREN', 'RPAREN', 'EQUALS'
]

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

# ============================
# ANALISADOR SINTÁTICO
# ============================

def p_comando_atribuir(p):
    'comando : ATRIBUIR ID EQUALS expressao'
    p[0] = ('atribuir', p[2], p[4])

def p_comando_mostrar(p):
    'comando : MOSTRAR expressao'
    p[0] = ('mostrar', p[2])

def p_comando_derivar(p):
    'comando : DERIVAR expressao'
    p[0] = ('derivar', p[2])

def p_comando_integrar(p):
    'comando : INTEGRAR expressao'
    p[0] = ('integrar', p[2])

def p_expressao_operacao(p):
    'expressao : expressao OP termo'
    p[0] = ('op', p[2], p[1], p[3])

def p_expressao_termo(p):
    'expressao : termo'
    p[0] = p[1]

def p_termo_id(p):
    'termo : ID'
    p[0] = ('id', p[1])

def p_termo_number(p):
    'termo : NUMBER'
    p[0] = ('num', p[1])

def p_termo_parenteses(p):
    'termo : LPAREN expressao RPAREN'
    p[0] = p[2]

def p_error(p):
    if p:
        print(f"Erro de sintaxe próximo a '{p.value}'")
    else:
        print("Erro de sintaxe: fim inesperado da entrada")

parser = yacc.yacc()

# ============================
# CONVERSÃO DA AST PARA SYMPY
# ============================

def ast_para_sympy(ast):
    # converte a árvore sintática para expressão 
    if ast[0] == 'num':
        return ast[1]
    elif ast[0] == 'id':
        return Symbol(ast[1])
    elif ast[0] == 'op':
        op, left, right = ast[1], ast[2], ast[3]
        left_expr = ast_para_sympy(left)
        right_expr = ast_para_sympy(right)
        if op == '+':
            return left_expr + right_expr
        elif op == '-':
            return left_expr - right_expr
        elif op == '*':
            return left_expr * right_expr
        elif op == '/':
            return left_expr / right_expr
        elif op == '^':
            return left_expr ** right_expr
    elif ast[0] == 'derivar':
        expr = ast_para_sympy(ast[1])
        return diff(expr, Symbol('x'))
    elif ast[0] == 'integrar':
        expr = ast_para_sympy(ast[1])
        return integrate(expr, Symbol('x'))
    elif ast[0] == 'atribuir':
        # retorna uma tupla para atribuição
        return (ast[1], ast_para_sympy(ast[2]))
    elif ast[0] == 'mostrar':
        return ast_para_sympy(ast[1])
    else:
        return None

# ============ 
# EXECUÇÃO 
# ============ 
print("Digite uma expressão para análise sintática e simbólica.")
print("Exemplo: derivar x^2 + 3*x")
entrada = input("Expressão: ")

resultado = parser.parse(entrada, lexer=lexer)
if resultado:
    print("Expressão sintaticamente CORRETA!")
    print("Árvore sintática:", resultado)
    expr_sympy = ast_para_sympy(resultado)
    print("Expressão SymPy:", expr_sympy)
    print("Resultado:", expr_sympy)
else:
    print("Expressão inválida.")