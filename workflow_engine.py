handlers = {}
  # Set to False for real HTTP requests
def register(node_id):
    """Decorator to register a handler for a given node id"""
    def decorator(fn):
        handlers[node_id] = fn
        return fn
    return decorator

def execute_workflow(workflow_config, initial_context=None):
    context = initial_context.copy() if initial_context else {}
    nodes = {n['id']: n for n in workflow_config.get('nodes', [])}
    edges = workflow_config.get('edges', [])

    # Map sources to list of (target, edge_label)
    next_map = {}
    for e in edges:
        src = e['source']; tgt = e['target']
        label = e.get('label')  # 'true'/'false' for if, else None
        next_map.setdefault(src, []).append((tgt, label))

    # Find start node(s): nodes not a target
    targets = {e['target'] for e in edges}
    start = [nid for nid in nodes if nid not in targets]
    if not start:
        raise ValueError("No start node found")
    queue = start.copy()

    while queue:
        nid = queue.pop(0)
        node = nodes[nid]
        ntype = node.get('data', {}).get('type') or node.get('type')
        handler = handlers.get(ntype)
        if not handler:
            raise ValueError(f"No handler for node type '{ntype}'")

        cfg = node.get('data', {}).get('config', {})
        inp = node.get('data', {}).get('input', {})
        print(f"Executing {ntype} (id={nid})...")
        res = handler(cfg, inp, context)
        context[nid] = res

        # Determine next based on if/branch
        for tgt, lbl in next_map.get(nid, []):
            # If this is an if-node, only enqueue matching branch
            if ntype == 'if':
                out = res.get('output')
                # label may be 'true'/'false'
                if lbl == str(out).lower():
                    queue.append(tgt)
            else:
                queue.append(tgt)

    return context

