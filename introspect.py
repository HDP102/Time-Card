"""
introspect.py - read-only. Lists what the Tufin GraphQL API offers around tickets,
to find out whether a draft can be submitted by API. Changes nothing.
Run from RecertProcessor/:   py introspect.py
"""
import recert_processor as r

KEYWORDS = ("ticket", "draft", "submit", "request", "workflow", "advance", "step")


def q(s):
    return r._graphql(s, {})["data"]


def base(t):
    """Unwrap NON_NULL / LIST wrappers down to the named type."""
    while t and not t.get("name"):
        t = t.get("ofType")
    return t.get("name") if t else None


def fields(type_name):
    t = q('{__type(name:"%s"){fields{name args{name} type{name kind ofType{name kind '
          'ofType{name kind ofType{name}}}}}}}' % type_name)["__type"]
    return (t or {}).get("fields") or []


def show(title, flds, only_matching=False):
    print(f"\n== {title} ==")
    for f in flds:
        if only_matching and not any(k in f["name"].lower() for k in KEYWORDS):
            continue
        args = ", ".join(a["name"] for a in f["args"])
        print(f"  {f['name']}({args}) -> {base(f['type'])}")


try:
    roots = q("{__schema{queryType{name} mutationType{name}}}")["__schema"]
    query_root, mutation_root = roots["queryType"]["name"], roots["mutationType"]["name"]
except Exception:
    query_root, mutation_root = "Query", "Mutation"

mut = fields(mutation_root)
show(f"Mutation root ({mutation_root}) - all", mut)

rule_ops = next((f for f in mut if f["name"] == "ruleOperations"), None)
if rule_ops:
    ops_type = base(rule_ops["type"])
    ops = fields(ops_type)
    show(f"ruleOperations ({ops_type}) - all", ops)
    draft = next((f for f in ops if f["name"] == "createTicketDraft"), None)
    if draft:
        show(f"createTicketDraft returns ({base(draft['type'])})", fields(base(draft["type"])))

show(f"Query root ({query_root}) - ticket/draft related only", fields(query_root), True)
