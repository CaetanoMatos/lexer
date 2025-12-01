
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

def p_comando_expressao(p):
    'comando : expressao'
    p[0] = p[1]

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
        return (ast[1], ast_para_sympy(ast[2]))
    elif ast[0] == 'mostrar':
        return ast_para_sympy(ast[1])
    else:
        return None

# ============================
# GERAÇÃO DE TAC
# ============================

def sympy_to_tac(expr, temp_vars=None, tac=None):
    if temp_vars is None:
        temp_vars = {}
    if tac is None:
        tac = []

    if expr in temp_vars:
        return temp_vars[expr], tac

    if isinstance(expr, sp.Symbol):
        return str(expr), tac
    if isinstance(expr, sp.Number):
        return str(expr), tac

    if isinstance(expr, sp.Add):
        temps = []
        for arg in expr.args:
            temp, tac = sympy_to_tac(arg, temp_vars, tac)
            temps.append(temp)
        temp_name = f"t{len(temp_vars)+1}"
        tac.append(f"{temp_name} = {' + '.join(temps)}")
        temp_vars[expr] = temp_name
        return temp_name, tac

    if isinstance(expr, sp.Mul):
        temps = []
        for arg in expr.args:
            temp, tac = sympy_to_tac(arg, temp_vars, tac)
            temps.append(temp)
        temp_name = f"t{len(temp_vars)+1}"
        tac.append(f"{temp_name} = {' * '.join(temps)}")
        temp_vars[expr] = temp_name
        return temp_name, tac

    if isinstance(expr, sp.Pow):
        base, tac = sympy_to_tac(expr.args[0], temp_vars, tac)
        exp, tac = sympy_to_tac(expr.args[1], temp_vars, tac)
        temp_name = f"t{len(temp_vars)+1}"
        tac.append(f"{temp_name} = {base} ** {exp}")
        temp_vars[expr] = temp_name
        return temp_name, tac

    temp_name = f"t{len(temp_vars)+1}"
    tac.append(f"{temp_name} = {expr}")
    temp_vars[expr] = temp_name
    return temp_name, tac

# ============================
# GERAÇÃO DE LLVM IR TEXTUAL
# ============================


def tac_to_llvm_ir(tac, arg_name="x", func_name="calc"):
    llvm_lines = []
    llvm_lines.append("declare double @llvm.pow.f64(double, double)")
    llvm_lines.append(f"define double @{func_name}(double %{arg_name}) {{")
    llvm_lines.append("entry:")

    temp_map = {}
    for instr in tac:
        left, expr = instr.split(" = ")
        left = left.strip()
        temp_map[left] = f"%{left}"

        # Potência
        if "**" in expr:
            base, exp = expr.split(" ** ")
            base = base.strip()
            exp = exp.strip()
            base_val = temp_map.get(base, f"%{base}" if base.isidentifier() else base)
            llvm_lines.append(f"  {temp_map[left]} = call double @llvm.pow.f64(double {base_val}, double {exp})")
        # Multiplicação por constante (ex: 1/4 * t1 ou 3/2 * t3)
        elif "*" in expr and "/" in expr:
            # Detecta padrão constante * temp
            parts = expr.split(" * ")
            const = parts[0].strip()
            temp = parts[1].strip()
            # Avalia constante (ex: '1/4' -> 0.25)
            try:
                const_val = float(eval(const))
            except:
                const_val = const
            temp_val = temp_map.get(temp, f"%{temp}" if temp.isidentifier() else temp)
            llvm_lines.append(f"  {temp_map[left]} = fmul double {const_val}, {temp_val}")
        # Multiplicação normal
        elif "*" in expr:
            parts = expr.split(" * ")
            op1 = parts[0].strip()
            op2 = parts[1].strip()
            op1_val = temp_map.get(op1, f"%{op1}" if op1.isidentifier() else op1)
            op2_val = temp_map.get(op2, f"%{op2}" if op2.isidentifier() else op2)
            llvm_lines.append(f"  {temp_map[left]} = fmul double {op1_val}, {op2_val}")
        # Divisão
        elif "/" in expr and "*" not in expr:
            op1, op2 = expr.split(" / ")
            op1 = op1.strip()
            op2 = op2.strip()
            op1_val = temp_map.get(op1, f"%{op1}" if op1.isidentifier() else op1)
            op2_val = temp_map.get(op2, f"%{op2}" if op2.isidentifier() else op2)
            llvm_lines.append(f"  {temp_map[left]} = fdiv double {op1_val}, {op2_val}")
        # Soma
        elif "+" in expr:
            parts = expr.split(" + ")
            op1 = parts[0].strip()
            op2 = parts[1].strip()
            op1_val = temp_map.get(op1, f"%{op1}" if op1.isidentifier() else op1)
            op2_val = temp_map.get(op2, f"%{op2}" if op2.isidentifier() else op2)
            llvm_lines.append(f"  {temp_map[left]} = fadd double {op1_val}, {op2_val}")
        # Subtração
        elif "-" in expr:
            parts = expr.split(" - ")
            op1 = parts[0].strip()
            op2 = parts[1].strip()
            op1_val = temp_map.get(op1, f"%{op1}" if op1.isidentifier() else op1)
            op2_val = temp_map.get(op2, f"%{op2}" if op2.isidentifier() else op2)
            llvm_lines.append(f"  {temp_map[left]} = fsub double {op1_val}, {op2_val}")
        else:
            # Caso base: atribuição direta
            llvm_lines.append(f"  {temp_map[left]} = fadd double 0.0, {expr}")

    # Retorno
    llvm_lines.append(f"  ret double {temp_map[left]}")
    llvm_lines.append("}")
    return "\n".join(llvm_lines)


# ============ 
# EXECUÇÃO 
# ============ 
print("Digite uma expressão para análise sintática e simbólica.")
print("Exemplo: integrar x^2 + 3*x")
entrada = input("Expressão: ")


resultado = parser.parse(entrada, lexer=lexer)
if resultado:
    print("Expressão sintaticamente CORRETA!")
    print("Árvore sintática:", resultado)
    expr_sympy = ast_para_sympy(resultado)
    print("Expressão SymPy:", expr_sympy)
    print("Resultado:", expr_sympy)
    # Geração de TAC
    temp, tac = sympy_to_tac(expr_sympy)
    print("\nCódigo TAC gerado:")
    for instr in tac:
        print(instr)
    print(f"return {temp}")

    # Geração e salvamento do LLVM IR
    llvm_ir = tac_to_llvm_ir(tac, arg_name="x", func_name="calc")
    with open("saida.ll", "w") as f:
        f.write(llvm_ir)
    print("Arquivo LLVM IR salvo como 'saida.ll'.")
else:
    print("Expressão inválida.")

