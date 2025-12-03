# Script para Odoo Shell
# Ejecutar con: ./odoo-bin shell -c odoo.conf -d midatabase < backfill_ghosts.py

def backfill_ghosts(env):
    assignments = env['silver.assignment'].search([])
    Lead = env['crm.lead']

    print(f"Procesando {len(assignments)} asignaciones...")

    count = 0
    for assign in assignments:
        # Verificar si ya tiene fantasma (buscamos por fecha y asignación)
        existing = Lead.search([
            ('assignment_id', '=', assign.id),
            ('schedule_start', '=', '1980-01-01 08:00:00')
        ])
        
        if not existing:
            Lead.create({
                'name': f"[System] {assign.display_name or 'Instalador'} - Placeholder",
                'type': 'opportunity',
                'assignment_id': assign.id,
                'user_id': assign.user_id.id if assign.user_id else False,
                'schedule_start': '1980-01-01 08:00:00',
                'schedule_stop': '1980-01-01 09:00:00',
                'probability': 0,
                'active': True,
                'description': 'Registro técnico para inicializar la fila en el Timeline. No borrar.'
            })
            print(f"Creado fantasma para: {assign.display_name}")
            count += 1
        else:
            # print(f"Ya existe fantasma para: {assign.display_name}")
            pass

    print(f"Finalizado. Se crearon {count} registros fantasma.")
    # env.cr.commit() # Descomentar si se ejecuta en shell interactiva y se requiere commit manual

if 'env' in locals():
    backfill_ghosts(env)
    env.cr.commit()
