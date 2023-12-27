import ast
from typing import Any


class _Namespace_(dict):
    def __getitem__(self, item):
        if item not in self:
            raise PermissionError
        return super().__getitem__(item)


class Astrun(ast.NodeVisitor):
    def __init__(self, namespace: dict[str, Any] = None):
        self.namespace = _Namespace_(namespace) if namespace is not None else _Namespace_(
            {
                "abs": abs,
                "all": all,
                "any": any,
                "dict": dict,
                "enumerate": enumerate,
                "filter": filter,
                "float": float,
                "hash": hash,
                "hex": hex,
                "int": int,
                "iter": iter,
                "len": len,
                "list": list,
                "map": map,
                "max": max,
                "min": min,
                "next": next,
                "pow": pow,
                "range": range,
                "reversed": reversed,
                "round": round,
                "set": set,
                "sorted": sorted,
                "str": str,
                "sum": sum,
                "tuple": tuple,
                "zip": zip,
            }
        )

    def __call__(self, ast_tree: ast.Module):
        res = None
        for item in ast_tree.body:
            res = self.visit(item)
        return res

    @classmethod
    def eval(cls, expr: str):
        tree = ast.parse(expr)
        return cls()(tree)

    def visit(self, node: Any):
        return super().visit(node)

    def generic_visit(self, node):
        raise PermissionError

    ###########
    # Literals
    def visit_Constant(self, node):
        return node.value

    # no string formatting, no f-strings

    def visit_List(self, node):
        if isinstance(node.ctx, ast.Load):
            res = []
            for elt in node.elts:
                if isinstance(elt, ast.Starred):
                    res.extend(self.visit(elt))
                else:
                    res.append(self.visit(elt))
            return res
        elif isinstance(node.ctx, ast.Store):
            # return the variable name tuple; will be stored in Assign
            return tuple(self.visit(elt) for elt in node.elts)
        else:
            raise PermissionError

    def visit_Tuple(self, node):
        if isinstance(node.ctx, ast.Load):
            res = []
            for elt in node.elts:
                if isinstance(elt, ast.Starred):
                    res.extend(self.visit(elt))
                else:
                    res.append(self.visit(elt))
            return tuple(res)
        elif isinstance(node.ctx, ast.Store):
            # return the variable name tuple; will be stored in Assign
            return tuple(self.visit(elt) for elt in node.elts)
        else:
            raise PermissionError

    def visit_Set(self, node):
        # Set has no ctx; always load
        res = set()
        for elt in node.elts:
            if isinstance(elt, ast.Starred):
                res.update(self.visit(elt))
            else:
                res.add(self.visit(elt))
        return res

    def visit_Dict(self, node):
        # Dict has no ctx; always load
        res = dict()
        for key, value in zip(node.keys, node.values):
            k = None if key is None else self.visit(key)
            v = self.visit(value)
            if k is None:
                res.update(v)
            else:
                res[k] = v
        return res

    #######################
    # Variables
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            return self.namespace[node.id]
        elif isinstance(node.ctx, ast.Store):
            return node.id  # return the variable name; will be stored in Assign
        elif isinstance(node.ctx, ast.Del):
            self.namespace.pop(node.id)
        else:
            raise PermissionError

    def visit_Starred(self, node):
        if isinstance(node.ctx, ast.Load):
            for item in self.visit(node.value):
                yield item
        elif isinstance(node.ctx, ast.Store):
            return node  # return the Starred node directly
        else:
            raise PermissionError

    #################
    # Expressions
    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_UnaryOp(self, node):
        return self.visit(node.op)(self.visit(node.operand))

    def visit_UAdd(self, node):
        return lambda a: +a

    def visit_USub(self, node):
        return lambda a: -a

    def visit_Not(self, node):
        return lambda a: not a

    def visit_Invert(self, node):
        return lambda a: ~a

    def visit_BinOp(self, node):
        return self.visit(node.op)(self.visit(node.left), self.visit(node.right))

    def visit_Add(self, node):
        return lambda a, b: a + b

    def visit_Sub(self, node):
        return lambda a, b: a - b

    def visit_Mult(self, node):
        return lambda a, b: a * b

    def visit_Div(self, node):
        return lambda a, b: a / b

    def visit_FloorDiv(self, node):
        return lambda a, b: a // b

    def visit_Mod(self, node):
        return lambda a, b: a % b

    def visit_Pow(self, node):
        return lambda a, b: a ** b

    def visit_LShift(self, node):
        return lambda a, b: a << b

    def visit_RShift(self, node):
        return lambda a, b: a >> b

    def visit_BitOr(self, node):
        return lambda a, b: a | b

    def visit_BitXor(self, node):
        return lambda a, b: a ^ b

    def visit_BitAnd(self, node):
        return lambda a, b: a & b

    def visit_MatMult(self, node):
        return lambda a, b: a @ b

    def visit_BoolOp(self, node):
        res = self.visit(node.values[0])
        for value in node.values[1:]:
            res = self.visit(node.op)(res, self.visit(value))
        return res

    def visit_And(self, node):
        return lambda a, b: a and b

    def visit_Or(self, node):
        return lambda a, b: a or b

    def visit_Compare(self, node):
        res = self.visit(node.left)
        for op, cp in zip(node.ops, node.comparators):
            res = self.visit(op)(res, self.visit(cp))

        return res

    def visit_Eq(self, node: ast.Eq):
        return lambda a, b: a == b

    def visit_NotEq(self, node: ast.Eq):
        return lambda a, b: a != b

    def visit_Lt(self, node):
        return lambda a, b: a < b

    def visit_LtE(self, node):
        return lambda a, b: a <= b

    def visit_Gt(self, node):
        return lambda a, b: a > b

    def visit_GtE(self, node):
        return lambda a, b: a >= b

    def visit_Is(self, node):
        return lambda a, b: a is b

    def visit_IsNot(self, node):
        return lambda a, b: a is not b

    def visit_In(self, node):
        return lambda a, b: a in b

    def visit_NotIn(self, node):
        return lambda a, b: a not in b

    def visit_Call(self, node):
        func = self.visit(node.func)
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                args.extend(self.visit(arg))
            else:
                args.append(self.visit(arg))

        kwargs = dict()
        for kwarg in node.keywords:
            kwargs.update(self.visit(kwarg))

        return func(*args, **kwargs)

    def visit_keyword(self, node):
        if node.arg is None:
            return self.visit(node.value)
        else:
            return {node.arg: self.visit(node.value)}

    def visit_IfExp(self, node):
        return self.visit(node.body) if self.visit(node.test) else self.visit(node.orelse)

    def visit_Attribute(self, node):
        if node.attr.startswith("_"):
            # no messing up with private or dunder attributes
            raise PermissionError

        value = self.visit(node.value)
        if isinstance(node.ctx, ast.Load):
            return getattr(value, node.attr)
        elif isinstance(node.ctx, ast.Store):
            return node
        elif isinstance(node.ctx, ast.Del):
            delattr(value, node.attr)
        else:
            raise PermissionError

    def visit_NamedExpr(self, node):
        res = self.visit(node.value)
        self.namespace[self.visit(node.target)] = res
        return res

    ####################
    # Subscripting
    def visit_Subscript(self, node):
        slice_param = self.visit(node.slice)
        value = self.visit(node.value)
        if isinstance(slice_param, tuple):
            return value[*slice_param]
        else:
            return value[slice_param]

    def visit_Slice(self, node):
        return slice(self.visit(node.lower), self.visit(node.upper), self.visit(node.step))

    #######################
    # Comprehensions
    def visit_ListComp(self, node):
        res = []

        def dfs(generators, idx):
            if idx >= len(generators):
                res.append(self.visit(node.elt))
            else:
                for _ in self.visit(generators[idx]):
                    dfs(generators, idx + 1)

        dfs(node.generators, 0)

        return res

    def visit_SetComp(self, node):
        res = set()

        def dfs(generators, idx):
            if idx >= len(generators):
                res.add(self.visit(node.elt))
            else:
                for _ in self.visit(generators[idx]):
                    dfs(generators, idx + 1)

        dfs(node.generators, 0)
        return res

    def visit_DictComp(self, node):
        res = dict()

        def dfs(generators, idx):
            if idx >= len(generators):
                res[self.visit(node.key)] = self.visit(node.value)
            else:
                for _ in self.visit(generators[idx]):
                    dfs(generators, idx + 1)

        dfs(node.generators, 0)
        return res

    def visit_GeneratorExp(self, node):
        def dfs(generators, idx):
            if idx >= len(generators):
                yield self.visit(node.elt)
            else:
                for _ in self.visit(generators[idx]):
                    yield from dfs(generators, idx + 1)

        yield from dfs(node.generators, 0)

    def visit_comprehension(self, node):
        for item in self.visit(node.iter):
            self.namespace[self.visit(node.target)] = item
            if all(self.visit(if_) for if_ in node.ifs):
                yield item

    ##############
    # Statements
    def visit_Assign(self, node):
        value = self.visit(node.value)

        if len(node.targets) and isinstance(name := self.visit(node.targets[0]), tuple):
            cur = 0

            def traverse_assignment(n, v):
                nonlocal cur
                if isinstance(n, tuple):
                    # dealing with all kinds of assignment craziness
                    # a, b = (1,2); a, *b = (1, 2, 3); (a, b), c = (1, 2), 3, 4, 5
                    for sub_n in n:
                        traverse_assignment(sub_n, v)

                elif isinstance(n, ast.Starred):
                    self.namespace[self.visit(n)] = list(v[cur:])
                    cur = None
                elif isinstance(n, ast.Attribute):
                    setattr(self.visit(n.value), n.attr, v[cur])
                    cur += 1
                else:
                    self.namespace[n] = v[cur]
                    cur += 1

            traverse_assignment(name, value)
        else:
            for target in node.targets:
                name = self.visit(target)
                if isinstance(name, ast.Attribute):
                    setattr(self.visit(name.value), name.attr, value)
                else:
                    self.namespace[name] = value

    def visit_Delete(self, node):
        for target in node.targets:
            self.visit(target)

    #####################
    # Functions
    def visit_Lambda(self, node):
        """
        ATTENTION: the returned lambda function use the namespace of an Astrun object.
        To use a lambda function that returned from one Astrun object multiple times, make sure the function is pure.
        """
        arguments = self.visit(node.args)  # a list of args

        def res(*args):
            if len(args) != len(arguments):
                raise Exception(f"Required {len(arguments)} arguments but {len(args)} are given")

            for arg, v in zip(arguments, args):
                self.namespace[self.visit(arg)] = v

            return self.visit(node.body)

        return res

    def visit_arguments(self, node):
        return node.args

    def visit_arg(self, node):
        return node.arg
    # class and function def not allowed
