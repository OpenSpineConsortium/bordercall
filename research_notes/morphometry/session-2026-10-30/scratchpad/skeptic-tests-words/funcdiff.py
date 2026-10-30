import ast, sys
def funcs(path):
    tree = ast.parse(open(path).read())
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], 'value', None), ast.Constant) and isinstance(body[0].value.value, str):
                body = body[1:]
            out[node.name] = ast.dump(ast.Module(body=body, type_ignores=[]))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for t in (node.targets if isinstance(node, ast.Assign) else [node.target]):
                if isinstance(t, ast.Name):
                    out["=" + t.id] = ast.dump(node.value)
    return out
for name in sys.argv[3:]:
    a, b = funcs(f"{sys.argv[1]}/{name}.py"), funcs(f"{sys.argv[2]}/{name}.py")
    changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
    print(name, "changed:", changed)
    print(name, "added:", sorted(b.keys() - a.keys()))
    print(name, "removed:", sorted(a.keys() - b.keys()))
