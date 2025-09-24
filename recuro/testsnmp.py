import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


async def run():
    # Helper function for SNMP GET
    async def snmp_get(snmpEngine, host, community, oid):
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            snmpEngine,
            UsmUserData(
                "prueba",
                authKey='Rotulado$$',
                privKey='Rotulado$$',  # tu contraseña de privacidad
                authProtocol=usmHMACSHAAuthProtocol,
                privProtocol=usmDESPrivProtocol

            ),
            #CommunityData(community, mpModel=0),
            await UdpTransportTarget.create((host, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lookupMib=False,
            lexicographicMode=False,
        )
        if errorIndication:
            print(f"SNMP GET Error: {errorIndication}")
            return None
        elif errorStatus:
            print(
                f"SNMP GET Error: {errorStatus.prettyPrint()} at "
                f"{errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}"
            )
            return None
        else:
            return varBinds[0][1].prettyPrint() if varBinds else None

    # Helper function for SNMP WALK (GETNEXT)
    async def snmp_walk(snmpEngine, host, community, base_oid):
        results = []
        for e in await next_cmd(
            snmpEngine,
          #  CommunityData(community, mpModel=0),
            UsmUserData(
                "prueba",
                authKey='Rotulado$$',
                privKey='Rotulado$$',  # tu contraseña de privacidad
                authProtocol=usmHMACSHAAuthProtocol,
                privProtocol=usmDESPrivProtocol

            ),
            await UdpTransportTarget.create((host, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(base_oid)),
            lookupMib=False,
            lexicographicMode=False,
        ):
        #if iterator:

            #print(("iterator", iterator))
           # for e in await iterator:
           if 1:
                if not e: continue
                print(("e",base_oid, e, "_", dir(e)))
                #continue
                for oid, val in e:
                    print(oid.prettyPrint(), '=', val.prettyPrint())
                continue
                #print(("a,b",a, b))
                #errorIndication, errorStatus, errorIndex, varBinds = e[0]
                if errorIndication:
                    print(f"SNMP WALK Error: {errorIndication}")
                    return results
                elif errorStatus:
                    print(
                        f"SNMP WALK Error: {errorStatus.prettyPrint()} at "
                        f"{errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}"
                    )
                    return results
                else:
                    for varBind in varBinds:
                        if not varBind[0].prettyPrint().startswith(base_oid):
                            return results
                        results.append((varBind[0].prettyPrint(), varBind[1].prettyPrint()))
        return results

    # Helper function for SNMP SET
    async def snmp_set(snmpEngine, host, community, oid, value, value_type='OctetString'):
        # Determine the type of value to set
        if value_type == 'Integer32':
            set_value = Integer32(int(value))
        elif value_type == 'OctetString':
            set_value = OctetString(value)
        # Add more types as needed (e.g., Counter32, Gauge32, IpAddress)
        else:
            print(f"Unsupported value type: {value_type}")
            return False

        errorIndication, errorStatus, errorIndex, varBinds = await set_cmd(
            snmpEngine,
         #   CommunityData(community, mpModel=0),
            UsmUserData(
                "prueba",
                authKey='Rotulado$$',
                privKey='Rotulado$$',  # tu contraseña de privacidad
                authProtocol=usmHMACSHAAuthProtocol,
                privProtocol=usmDESPrivProtocol

            ),
            await UdpTransportTarget.create((host, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid), set_value),
            lookupMib=False,
            lexicographicMode=False,
        )
        if errorIndication:
            print(f"SNMP SET Error: {errorIndication}")
            return False
        elif errorStatus:
            print(
                f"SNMP SET Error: {errorStatus.prettyPrint()} at "
                f"{errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}"
            )
            return False
        else:
            print(f"SNMP SET successful for OID {oid} with value {value}")
            return True

    async def get_olt_info(snmpEngine, host, community):
        print(f"\n--- Getting OLT Information for {host} ---")
        sys_descr = await snmp_get(snmpEngine, host, community, "1.3.6.1.2.1.1.1.0")
        sys_uptime = await snmp_get(snmpEngine, host, community, "1.3.6.1.2.1.1.3.0")
        sys_serial = await  snmp_get(snmpEngine, host, community, "1.3.6.1.2.1.47.1.1.1.1.11.67109120")
        sys_name = await snmp_get(snmpEngine, host, community, "1.3.6.1.2.1.1.5.0")

        if sys_descr:
            print(f"System Description: {sys_descr} {sys_serial}")
        if sys_uptime:
            print(f"System Up Time: {sys_uptime}")
        if sys_name:
            print(f"System Name: {sys_name}")

    async def list_clients(snmpEngine, host, community):
        print(f"\n--- Listing Clients for {host} ---")
        # IMPORTANT: Replace '1.3.6.1.4.1.XXXXX.Y.Z' with the actual OID for your OLT's client table.
        # This OID is highly vendor-specific (e.g., for ONUs, CPEs).
        # You might need to consult your OLT's MIB documentation.
        client_table_oid = "1.3.6.1.4.1.99999.1.1.1" # Placeholder OID
        clients = await snmp_walk(snmpEngine, host, community, client_table_oid)
        if clients:
            print("Found Clients:")
            for oid, value in clients:
                print(f"  OID: {oid}, Value: {value}")
        else:
            print("No clients found or OID is incorrect.")
        print("NOTE: The OID used for listing clients is a placeholder. Please replace it with the actual vendor-specific OID for your OLT's client table.")

    async def connect_client(snmpEngine, host, community, client_identifier_oid, status_value):
        print(f"\n--- Connecting Client {client_identifier_oid} on {host} ---")
        # IMPORTANT: Replace '1.3.6.1.4.1.XXXXX.Y.Z.clientStatus' with the actual OID for setting client status.
        # The 'status_value' will depend on your OLT's MIB (e.g., 1 for active, 2 for inactive).
        # This operation is highly vendor-specific and can have significant impact. Use with caution.
        client_status_oid = f"1.3.6.1.4.1.99999.1.1.2.{client_identifier_oid}" # Placeholder OID
        success = await snmp_set(snmpEngine, host, community, client_status_oid, status_value, value_type='Integer32')
        if success:
            print(f"Attempted to connect client {client_identifier_oid}. Please verify on OLT.")
        else:
            print(f"Failed to send connect command for client {client_identifier_oid}.")
        print("NOTE: The OID and status value used for connecting a client are placeholders. Please replace them with the actual vendor-specific OID and values for your OLT.")

    async def disconnect_client(snmpEngine, host, community, client_identifier_oid, status_value):
        print(f"\n--- Disconnecting Client {client_identifier_oid} on {host} ---")
        # IMPORTANT: Replace '1.3.6.1.4.1.XXXXX.Y.Z.clientStatus' with the actual OID for setting client status.
        # The 'status_value' will depend on your OLT's MIB (e.g., 1 for active, 2 for inactive).
        # This operation is highly vendor-specific and can have significant impact. Use with caution.
        client_status_oid = f"1.3.6.1.4.1.99999.1.1.2.{client_identifier_oid}" # Placeholder OID
        success = await snmp_set(snmpEngine, host, community, client_status_oid, status_value, value_type='Integer32')
        if success:
            print(f"Attempted to disconnect client {client_identifier_oid}. Please verify on OLT.")
        else:
            print(f"Failed to send disconnect command for client {client_identifier_oid}.")
        print("NOTE: The OID and status value used for disconnecting a client are placeholders. Please replace them with the actual vendor-specific OID and values for your OLT.")


    snmpEngine = SnmpEngine()
    olt_host = "172.16.0.74"
    community_string = "public" # Consider using a more secure community string or SNMPv3

    # Get OLT Information
    await get_olt_info(snmpEngine, olt_host, community_string)

    # List Clients
    await list_clients(snmpEngine, olt_host, community_string)

    # Example: Connect/Disconnect a client
    # You need to replace 'client_index_or_id' with the actual identifier of the client
    # and 'connect_status_value'/'disconnect_status_value' with the appropriate integer values
    # as defined by your OLT's MIB for active/inactive status.
    # For example, if 1 means active and 2 means inactive:
    # await connect_client(snmpEngine, olt_host, community_string, "client_index_or_id", 1)
    # await disconnect_client(snmpEngine, olt_host, community_string, "client_index_or_id", 2)
    print("\n--- Client Connect/Disconnect Example ---")
    print("To connect/disconnect a client, you need to uncomment the lines in the 'run' function.")
    print("Replace 'client_index_or_id' with the actual identifier of the client (e.g., its port index or unique ID).")
    print("Replace 'connect_status_value' and 'disconnect_status_value' with the appropriate integer values as defined by your OLT's MIB for active/inactive status (e.g., 1 for active, 2 for inactive).")
    print("These operations are highly vendor-specific and require careful use of the correct OIDs and values.")

    async def list_ports_status(snmpEngine, host, community):
        print(f"\n--- Listing Ports and Status for {host} ---")
        # OIDs for interface descriptions and operational status
        if_descr_oid = "1.3.6.1.4.1.5875.800.3.7.1.1.2.3"
        if_oper_status_oid = ".1.3.6.1.4.1.5875.800.3.9.1.1.3"

        # Get descriptions and statuses
        descriptions = await snmp_walk(snmpEngine, host, community, if_descr_oid)
        statuses = await snmp_walk(snmpEngine, host, community, if_oper_status_oid)

        if descriptions and statuses:
            print("Found Ports:")
            # Create a dictionary to map port index to description
            desc_map = {oid.split('.')[-1]: value for oid, value in descriptions}
            
            for oid, status in statuses:
                port_index = oid.split('.')[-1]
                description = desc_map.get(port_index, "Unknown")
                # Statuses are returned as integers (1: up, 2: down, 3: testing, etc.)
                status_str = {
                    '1': 'up',
                    '2': 'down',
                    '3': 'testing',
                    '4': 'unknown',
                    '5': 'dormant',
                    '6': 'notPresent',
                    '7': 'lowerLayerDown'
                }.get(status, "unknown status")
                print(f"  Port: {description} (Index: {port_index}), Status: {status_str}")
        else:
            print("Could not retrieve port information. Check OIDs and device connectivity.")

    snmpEngine = SnmpEngine()
    olt_host = "172.16.0.74"
    community_string = "public" # Consider using a more secure community string or SNMPv3

    # Get OLT Information
    await get_olt_info(snmpEngine, olt_host, community_string)

    # List Ports and their Status
    await list_ports_status(snmpEngine, olt_host, community_string)

    # List Clients
    await list_clients(snmpEngine, olt_host, community_string)

    # Example: Connect/Disconnect a client
    # You need to replace 'client_index_or_id' with the actual identifier of the client
    # and 'connect_status_value'/'disconnect_status_value' with the appropriate integer values
    # as defined by your OLT's MIB for active/inactive status.
    # For example, if 1 means active and 2 means inactive:
    # await connect_client(snmpEngine, olt_host, community_string, "client_index_or_id", 1)
    # await disconnect_client(snmpEngine, olt_host, community_string, "client_index_or_id", 2)
    print("\n--- Client Connect/Disconnect Example ---")
    print("To connect/disconnect a client, you need to uncomment the lines in the 'run' function.")
    print("Replace 'client_index_or_id' with the actual identifier of the client (e.g., its port index or unique ID).")
    print("Replace 'connect_status_value' and 'disconnect_status_value' with the appropriate integer values as defined by your OLT's MIB for active/inactive status (e.g., 1 for active, 2 for inactive).")
    print("These operations are highly vendor-specific and require careful use of the correct OIDs and values.")


    snmpEngine.close_dispatcher()


asyncio.run(run())