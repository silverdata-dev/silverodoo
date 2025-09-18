
import graphviz

# --- Creación del grafo ---
dot = graphviz.Digraph('Herencia de Modelos', comment='Diagrama de Herencia para silver_isp')
dot.attr(rankdir='LR', splines='ortho', concentrate='true', nodesep='1', ranksep='1.5')
dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightgrey')
dot.attr('edge', arrowhead='empty')

# --- Nodos Padre (con estilo especial) ---
with dot.subgraph(name='cluster_parents') as c:
    c.attr(style='filled', color='lightyellow')
    c.attr(label='Modelos Base Abstractos')
    c.node('silver.asset', 'silver.asset\n(Activo Físico)', shape='Mdiamond', fillcolor='lightblue')
    c.node('silver.netdev', 'silver.netdev\n(Dispositivo de Red)', shape='Mdiamond', fillcolor='lightgreen')

# --- Nodos Hijos ---

# Heredan solo de silver.asset
with dot.subgraph(name='cluster_assets') as c:
    c.attr(label='Activos Físicos Pasivos')
    c.attr(style='dotted')
    c.node('silver.node', 'silver.node (Nodo)')
    c.node('silver.post', 'silver.post (Poste)')
    c.node('silver.cable', 'silver.cable (Cable)')
    c.node('silver.splice_closure', 'silver.splice_closure (Manga)')
    c.node('silver.box', 'silver.box (Caja Nap)')
    c.node('silver.splitter', 'silver.splitter (Spliter)')

# Heredan solo de silver.netdev
with dot.subgraph(name='cluster_netdevs') as c:
    c.attr(label='Dispositivos de Red Lógicos')
    c.attr(style='dotted')
    c.node('silver.olt.card.port', 'silver.olt.card.port (Pon)')
    c.node('silver.radius', 'silver.radius (Radius)')

# Heredan de ambos
with dot.subgraph(name='cluster_both') as c:
    c.attr(label='Activos Físicos y de Red (Equipos Activos)')
    c.attr(style='dotted')
    c.node('silver.core', 'silver.core (Router)')
    c.node('silver.olt', 'silver.olt (OLT)')
    c.node('silver.ap', 'silver.ap (AP)')


# --- Definición de las Relaciones de Herencia ---

# Hijos de silver.asset
dot.edge('silver.node', 'silver.asset')
dot.edge('silver.post', 'silver.asset')
dot.edge('silver.post', 'silver.asset')
dot.edge('silver.cable', 'silver.asset')
dot.edge('silver.splice_closure', 'silver.asset')
dot.edge('silver.box', 'silver.asset')
dot.edge('silver.splitter', 'silver.asset')

# Hijos de silver.netdev
dot.edge('silver.olt.card.port', 'silver.netdev')
dot.edge('silver.radius', 'silver.netdev')

# Hijos de ambos
dot.edge('silver.core', 'silver.asset')
dot.edge('silver.core', 'silver.netdev')
dot.edge('silver.olt', 'silver.asset')
dot.edge('silver.olt', 'silver.netdev')
dot.edge('silver.ap', 'silver.asset')
dot.edge('silver.ap', 'silver.netdev')


# --- Renderizado del archivo PNG ---
try:
    dot.render('herencia_modelos', format='png', view=False, cleanup=True)
    print("¡Éxito! Se ha generado el archivo 'herencia_modelos.png'")
except Exception as e:
    print(f"Error al generar el diagrama: {e}")
    print("Asegúrate de tener Graphviz instalado en tu sistema (ej: 'sudo apt-get install graphviz')")
