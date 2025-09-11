
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
    c.node('isp.asset', 'isp.asset\n(Activo Físico)', shape='Mdiamond', fillcolor='lightblue')
    c.node('isp.netdev', 'isp.netdev\n(Dispositivo de Red)', shape='Mdiamond', fillcolor='lightgreen')

# --- Nodos Hijos ---

# Heredan solo de isp.asset
with dot.subgraph(name='cluster_assets') as c:
    c.attr(label='Activos Físicos Pasivos')
    c.attr(style='dotted')
    c.node('isp.node', 'isp.node (Nodo)')
    c.node('isp.post', 'isp.post (Poste)')
    c.node('isp.cable', 'isp.cable (Cable)')
    c.node('isp.splice_closure', 'isp.splice_closure (Manga)')
    c.node('isp.box', 'isp.box (Caja Nap)')
    c.node('isp.splitter', 'isp.splitter (Spliter)')

# Heredan solo de isp.netdev
with dot.subgraph(name='cluster_netdevs') as c:
    c.attr(label='Dispositivos de Red Lógicos')
    c.attr(style='dotted')
    c.node('isp.olt.card.port', 'isp.olt.card.port (Pon)')
    c.node('isp.radius', 'isp.radius (Radius)')

# Heredan de ambos
with dot.subgraph(name='cluster_both') as c:
    c.attr(label='Activos Físicos y de Red (Equipos Activos)')
    c.attr(style='dotted')
    c.node('isp.core', 'isp.core (Router)')
    c.node('isp.olt', 'isp.olt (OLT)')
    c.node('isp.ap', 'isp.ap (AP)')


# --- Definición de las Relaciones de Herencia ---

# Hijos de isp.asset
dot.edge('isp.node', 'isp.asset')
dot.edge('isp.post', 'isp.asset')
dot.edge('isp.post', 'isp.asset')
dot.edge('isp.cable', 'isp.asset')
dot.edge('isp.splice_closure', 'isp.asset')
dot.edge('isp.box', 'isp.asset')
dot.edge('isp.splitter', 'isp.asset')

# Hijos de isp.netdev
dot.edge('isp.olt.card.port', 'isp.netdev')
dot.edge('isp.radius', 'isp.netdev')

# Hijos de ambos
dot.edge('isp.core', 'isp.asset')
dot.edge('isp.core', 'isp.netdev')
dot.edge('isp.olt', 'isp.asset')
dot.edge('isp.olt', 'isp.netdev')
dot.edge('isp.ap', 'isp.asset')
dot.edge('isp.ap', 'isp.netdev')


# --- Renderizado del archivo PNG ---
try:
    dot.render('herencia_modelos', format='png', view=False, cleanup=True)
    print("¡Éxito! Se ha generado el archivo 'herencia_modelos.png'")
except Exception as e:
    print(f"Error al generar el diagrama: {e}")
    print("Asegúrate de tener Graphviz instalado en tu sistema (ej: 'sudo apt-get install graphviz')")
