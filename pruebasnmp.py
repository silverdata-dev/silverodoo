# -*- coding: utf-8 -*-

from pysnmp.hlapi import *

# ----------------------------------------------------
# Configuración
# ----------------------------------------------------
# La dirección IP de tu OLT
host = '172.16.0.74'

# La community string (la "contraseña" de tu SNMP)
community_string = 'public'

# ----------------------------------------------------
# OIDs relevantes del MIB
# ----------------------------------------------------
# La descripción del sistema (estándar SNMP)
sys_descr_oid = '1.3.6.1.2.1.1.1.0'

# El OID de la tabla de puertos de enlace ascendente del MIB V1600GSwitch.my
up_link_port_table_oid = '1.3.6.1.4.1.37950.1.1.5.10.1.1.1'
# Para obtener el estado administrativo de un puerto
up_link_port_admin_status_oid = up_link_port_table_oid + '.1.4'
# Para obtener el estado operativo de un puerto
up_link_port_oper_status_oid = up_link_port_table_oid + '.1.5'


# ----------------------------------------------------
# Función para realizar la consulta SNMP
# ----------------------------------------------------
def snmp_get_scalar(oid):
    """Obtiene un valor escalar (de un solo objeto) usando SNMP."""
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community_string, mpModel=1),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        return f"Error: {errorIndication}"
    elif errorStatus:
        return f"Error en el GET: {errorStatus.prettyPrint()}"
    else:
        return varBinds[0][1].prettyPrint()


def snmp_walk_table(oid_table):
    """
    Recorre una tabla SNMP y devuelve los datos como un diccionario.
    Carga el MIB para la traducción de OIDs.
    """
    results = {}

    # Cargar el MIB que me pasaste
    mib_view_controller = MibViewController(SnmpEngine().get
    MibInstrum().mibBuilder)
    mib_view_controller.loadModules('V1600GSwitch-March 13, 2025')

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData(community_string, mpModel=1),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid_table)),
        lookupMib=True,
        ignoreNonIncreasingOid=True
    ):
        if errorIndication:
            print(f"Error: {errorIndication}")
            break
        elif errorStatus:
            print(f"Error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            break
        else:
            for oid, val in varBinds:
                index = oid[-1]  # El último elemento del OID es el índice del puerto
                if index not in results:
                    results[index] = {}
                results[index][str(oid)] = val.prettyPrint()

    return results


# ----------------------------------------------------
# Ejecución del script
# ----------------------------------------------------
if __name__ == "__main__":
    print("--- 🕵️‍♀️ Información del OLT ---")
    sys_descr = snmp_get_scalar(sys_descr_oid)
    print(f"Descripción del sistema: {sys_descr}")

    print("\n--- 📡 Estado de los puertos de enlace ascendente ---")
    ports_info = snmp_walk_table(up_link_port_table_oid)

    if ports_info:
        for port_index, port_data in ports_info.items():
            admin_status_val = port_data.get(up_link_port_admin_status_oid + '.' + str(port_index))
            oper_status_val = port_data.get(up_link_port_oper_status_oid + '.' + str(port_index))

            # Mapeo de valores de estado numéricos a etiquetas más amigables
            admin_status_map = {'1': 'up', '2': 'down', '3': 'testing'}
            oper_status_map = {'1': 'up', '2': 'down', '3': 'testing'}

            admin_status = admin_status_map.get(admin_status_val, admin_status_val)
            oper_status = oper_status_map.get(oper_status_val, oper_status_val)

            print(f"Puerto {port_index}:")
            print(f"  Estado Admin: {admin_status}")
            print(f"  Estado Oper: {oper_status}")
    else:
        print("No se encontró información de puertos.")