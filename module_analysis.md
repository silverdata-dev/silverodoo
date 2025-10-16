# Análisis de Módulos de Odoo

Este documento analiza varios módulos de Odoo de los repositorios `account-analytic`, `account-financial-tools` y `om`.

# Directorio: account-analytic

## Módulo: stock_analytic

*   **Funcionalidad:** Añade distribución analítica a los movimientos de stock.
*   **Dependencias:** `stock_account`, `analytic`
*   **Explicación para el contador:** Permite asignar cuentas y etiquetas analíticas a los movimientos de inventario, lo que ayuda a rastrear los costos de los productos por proyecto o departamento.
*   **Explicación para el desarrollador:** Agrega campos analíticos a los modelos `stock.move`, `stock.scrap`, `stock.move.line` y `stock.picking` para registrar la información analítica en los asientos contables generados.
*   **Explicación para dummies:** Ayuda a saber cuánto dinero en productos se está usando en cada proyecto o área de la empresa.

## Módulo: analytic_base_department

*   **Funcionalidad:** Añade una relación entre las cuentas analíticas y los departamentos.
*   **Dependencias:** `account`, `hr`
*   **Explicación para el contador:** Vincula las cuentas analíticas con los departamentos de la empresa, facilitando el análisis de costos e ingresos por departamento.
*   **Explicación para el desarrollador:** Crea una relación entre `account.analytic.account` y `hr.department`, permitiendo filtrar y agrupar los datos analíticos por departamento.
*   **Explicación para dummies:** Conecta los gastos de un proyecto con el departamento que los realizó.

## Módulo: stock_landed_costs_analytic

*   **Funcionalidad:** Permite añadir información analítica a los costos en destino.
*   **Dependencias:** `stock_landed_costs`, `analytic`
*   **Explicación para el contador:** Asigna cuentas y etiquetas analíticas a las líneas de costos en destino, de modo que los asientos contables de validación reflejen esta distribución.
*   **Explicación para el desarrollador:** Extiende el modelo `stock.landed.cost.lines` para incluir campos analíticos que se transfieren a los asientos contables al validar los costos en destino.
*   **Explicación para dummies:** Ayuda a distribuir los gastos de envío y aduanas de un producto entre diferentes proyectos o departamentos.

## Módulo: account_analytic_tag

*   **Funcionalidad:** Proporciona etiquetas analíticas para una clasificación más detallada de los asientos contables.
*   **Dependencias:** `account`, `analytic`
*   **Explicación para el contador:** Permite etiquetar los asientos contables con múltiples dimensiones analíticas, mejorando la granularidad de los informes.
*   **Explicación para el desarrollador:** Introduce el modelo `account.analytic.tag` y lo integra con `account.move.line` para permitir la asignación de etiquetas analíticas.
*   **Explicación para dummies:** Es como ponerle varias etiquetas a un gasto para saber, por ejemplo, que fue para el "Proyecto X", del "Departamento de Marketing" y para la "Campaña de Navidad".

## Módulo: account_analytic_required

*   **Funcionalidad:** Hace que la cuenta analítica sea obligatoria en los asientos contables de ciertas cuentas.
*   **Dependencias:** `account_usability`
*   **Explicación para el contador:** Asegura que no se olviden de asignar una cuenta analítica en los asientos de gastos o ingresos, garantizando que todos los costos estén correctamente distribuidos.
*   **Explicación para el desarrollador:** Añade una restricción en `account.account` para que se pueda marcar la obligatoriedad de la cuenta analítica, lo que provoca un error si no se cumple en `account.move.line`.
*   **Explicación para dummies:** Es como un recordatorio que te obliga a decir a qué proyecto o área pertenece un gasto antes de guardarlo.

## Módulo: account_analytic_sequence

*   **Funcionalidad:** Restaura la secuencia de las cuentas analíticas.
*   **Dependencias:** `analytic`
*   **Explicación para el contador:** Asigna un código único y secuencial a cada cuenta analítica, facilitando su identificación y organización.
*   **Explicación para el desarrollador:** Añade una secuencia (`ir.sequence`) al modelo `account.analytic.account` para generar códigos únicos para cada nueva cuenta.
*   **Explicación para dummies:** Le pone un número de identificación único a cada proyecto, como si fuera un DNI.

## Módulo: stock_analytic_rule

*   **Funcionalidad:** Añade reglas de distribución para que los movimientos de stock creen líneas analíticas automáticamente.
*   **Dependencias:** `stock`, `account`, `analytic`
*   **Explicación para el contador:** Permite configurar reglas para que los costos de los movimientos de inventario se asignen automáticamente a las cuentas analíticas correctas.
*   **Explicación para el desarrollador:** Crea un modelo de reglas (`stock.analytic.model`) que se aplica a los movimientos de stock para generar `account.analytic.line` de forma automática.
*   **Explicación para dummies:** Es como una regla que dice: "siempre que salga un producto del almacén A, anota el gasto en el proyecto X".

## Módulo: purchase_request_analytic

*   **Funcionalidad:** Permite asignar información analítica a las solicitudes de compra.
*   **Dependencias:** `purchase_request`
*   **Explicación para el contador:** Asigna cuentas y etiquetas analíticas a las solicitudes de compra, permitiendo un seguimiento de los costos desde el inicio del proceso de compra.
*   **Explicación para el desarrollador:** Agrega campos analíticos al modelo `purchase.request` y `purchase.request.line`.
*   **Explicación para dummies:** Permite decir a qué proyecto o departamento pertenece un gasto desde el momento en que se pide permiso para comprar algo.

## Módulo: stock_picking_analytic

*   **Funcionalidad:** Permite definir la cuenta analítica a nivel de albarán.
*   **Dependencias:** `stock_analytic`, `base_view_inheritance_extension`
*   **Explicación para el contador:** Asigna una cuenta analítica a todo un albarán, de modo que todos los movimientos de ese albarán se asocien a la misma cuenta analítica.
*   **Explicación para el desarrollador:** Añade un campo de cuenta analítica al modelo `stock.picking` y propaga su valor a los movimientos de stock relacionados.
*   **Explicación para dummies:** Si en una entrega van productos para un solo proyecto, puedes etiquetar toda la entrega con el nombre de ese proyecto.

## Módulo: sale_analytic_tag

*   **Funcionalidad:** Permite asignar etiquetas analíticas a los pedidos de venta.
*   **Dependencias:** `sale`, `account_analytic_tag`
*   **Explicación para el contador:** Asigna etiquetas analíticas a los pedidos de venta, lo que permite un análisis detallado de los ingresos por diferentes dimensiones.
*   **Explicación para el desarrollador:** Agrega un campo de etiquetas analíticas al modelo `sale.order` y lo propaga a las facturas generadas.
*   **Explicación para dummies:** Permite etiquetar una venta para saber, por ejemplo, que fue para un cliente de "Europa", del sector "Retail" y para la "Campaña de Verano".

## Módulo: account_analytic_account_tag

*   **Funcionalidad:** Restaura las `tag_ids` en `account.analytic.account`.
*   **Dependencias:** `account_analytic_tag`
*   **Explicación para el contador:** Permite volver a usar etiquetas en las cuentas analíticas para una clasificación más detallada.
*   **Explicación para el desarrollador:** Reintroduce el campo `tag_ids` en el modelo `account.analytic.account`.
*   **Explicación para dummies:** Permite poner etiquetas de colores a tus proyectos para saber qué tipo de gastos tienen.

## Módulo: account_analytic_distribution_model_recalculate

*   **Funcionalidad:** Permite cambiar la distribución analítica de los apuntes asignados por un modelo de distribución.
*   **Dependencias:** `account`, `analytic`
*   **Explicación para el contador:** Si te equivocaste al asignar un gasto a un proyecto, este módulo te permite corregirlo fácilmente.
*   **Explicación para el desarrollador:** Añade la posibilidad de recalcular y modificar la distribución analítica en los apuntes contables (`account.move.line`).
*   **Explicación para dummies:** Si te equivocaste al decir a qué proyecto pertenecía un gasto, esto te deja arreglarlo.

## Módulo: product_analytic

*   **Funcionalidad:** Añade una cuenta analítica en productos y categorías de productos.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Asigna una cuenta analítica por defecto a los productos, de modo que cada vez que se compre o venda un producto, el gasto o ingreso se asigne automáticamente a la cuenta analítica correcta.
*   **Explicación para el desarrollador:** Añade un campo de cuenta analítica a los modelos `product.template` y `product.category`.
*   **Explicación para dummies:** Le dice al sistema que cada vez que compres o vendas una "silla de oficina", el dinero se apunte al proyecto de "Mobiliario".

## Módulo: purchase_stock_analytic

*   **Funcionalidad:** Copia la distribución analítica del pedido de compra al movimiento de stock.
*   **Dependencias:** `purchase_stock`, `stock_analytic`
*   **Explicación para el contador:** Asegura que la información analítica definida en la orden de compra se mantenga consistente hasta la recepción de los productos en el almacén.
*   **Explicación para el desarrollador:** Propaga los campos analíticos de `purchase.order.line` a `stock.move`.
*   **Explicación para dummies:** Si dijiste que una compra era para el "Proyecto X", esto se asegura de que cuando llegue el producto al almacén, siga etiquetado como del "Proyecto X".

## Módulo: account_analytic_document_date

*   **Funcionalidad:** Establece la fecha del documento en las líneas analíticas.
*   **Dependencias:** `account`, `account_reconcile_oca`
*   **Explicación para el contador:** Asegura que la fecha de la línea analítica coincida con la fecha del documento (factura, extracto bancario), mejorando la consistencia de los informes.
*   **Explicación para el desarrollador:** Añade un hook para actualizar la fecha de `account.analytic.line` con la fecha del documento de origen.
*   **Explicación para dummies:** Se asegura de que la fecha del gasto en tus informes sea la misma que la fecha que aparece en la factura.

## Módulo: account_analytic_organization

*   **Funcionalidad:** Añade un campo de organización en el partner para usarlo en la analítica.
*   **Dependencias:** `analytic`, `contacts`, `account`
*   **Explicación para el contador:** Permite clasificar a los clientes y proveedores por organización, y usar esta información para analizar los costos e ingresos.
*   **Explicación para el desarrollador:** Añade un campo `organization_id` a `res.partner` y lo hace disponible en las líneas analíticas y contables.
*   **Explicación para dummies:** Permite agrupar a tus clientes por empresa o grupo empresarial.

## Módulo: purchase_analytic

*   **Funcionalidad:** Permite asignar información analítica a los pedidos de compra.
*   **Dependencias:** `purchase`, `base_view_inheritance_extension`
*   **Explicación para el contador:** Similar a `purchase_request_analytic`, pero a nivel de orden de compra.
*   **Explicación para el desarrollador:** Agrega campos analíticos al modelo `purchase.order` y `purchase.order.line`.
*   **Explicación para dummies:** Permite decir a qué proyecto o departamento pertenece un gasto cuando se realiza la compra.

## Módulo: account_move_update_analytic

*   **Funcionalidad:** Permite actualizar la información analítica en asientos contables ya publicados.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Si te equivocaste al asignar la analítica de una factura ya validada, este módulo te permite corregirla sin tener que cancelar y volver a hacer la factura.
*   **Explicación para el desarrollador:** Proporciona un wizard para modificar los campos analíticos en `account.move` y `account.move.line` que ya han sido publicados.
*   **Explicación para dummies:** Te deja cambiar la etiqueta de un gasto incluso después de haberlo guardado.

## Módulo: account_analytic_distribution_manual

*   **Funcionalidad:** Permite la distribución manual de los importes de los asientos contables a diferentes cuentas analíticas.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite dividir un único apunte contable entre varios departamentos o proyectos.
*   **Explicación para el desarrollador:** Introduce un widget para gestionar la distribución analítica manualmente.
*   **Explicación para dummies:** Ayuda a dividir el costo de algo entre varias personas o proyectos.

## Módulo: analytic_partner

*   **Funcionalidad:** Vincula los apuntes analíticos con los partners.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite buscar y agrupar los apuntes analíticos por cliente o proveedor.
*   **Explicación para el desarrollador:** Añade un campo `partner_id` a `account.analytic.line`.
*   **Explicación para dummies:** Te deja ver todos los gastos e ingresos de un proyecto asociados a un cliente específico.

## Módulo: mrp_stock_analytic

*   **Funcionalidad:** Asigna la cuenta analítica de la orden de producción a los movimientos de stock.
*   **Dependencias:** `mrp_account`, `stock_analytic`
*   **Explicación para el contador:** Asegura que los costos de los materiales utilizados en una orden de producción se asignen a la cuenta analítica correcta.
*   **Explicación para el desarrollador:** Propaga la cuenta analítica de `mrp.production` a `stock.move`.
*   **Explicación para dummies:** Si estás fabricando algo para un proyecto, esto se asegura de que el costo de los materiales se apunte a ese proyecto.

## Módulo: pos_analytic_by_config

*   **Funcionalidad:** Usa la cuenta analítica definida en la configuración del punto de venta para los pedidos.
*   **Dependencias:** `point_of_sale`
*   **Explicación para el contador:** Asigna automáticamente una cuenta analítica a todas las ventas de una tienda o caja.
*   **Explicación para el desarrollador:** Aplica la distribución analítica de `pos.config` a `pos.order`.
*   **Explicación para dummies:** Asigna todas las ventas de una tienda a un centro de costo específico.

## Módulo: purchase_analytic_tag

*   **Funcionalidad:** Permite asignar etiquetas analíticas a los pedidos de compra.
*   **Dependencias:** `purchase`, `account_analytic_tag`
*   **Explicación para el contador:** Permite un análisis más detallado de las compras por diferentes dimensiones.
*   **Explicación para el desarrollador:** Agrega un campo de etiquetas analíticas a `purchase.order`.
*   **Explicación para dummies:** Permite etiquetar una compra para saber que fue para un "Proyecto X" y para el "Departamento de I+D".

## Módulo: account_analytic_distribution_manual_date

*   **Funcionalidad:** Añade fechas de inicio y fin a las reglas de distribución analítica manual.
*   **Dependencias:** `account_analytic_distribution_manual`
*   **Explicación para el contador:** Permite programar las reglas de distribución para que se apliquen solo en un período de tiempo determinado.
*   **Explicación para el desarrollador:** Añade los campos `date_start` y `date_end` al modelo de distribución.
*   **Explicación para dummies:** Permite que una regla de reparto de gastos solo se aplique, por ejemplo, durante el verano.

## Módulo: account_analytic_parent

*   **Funcionalidad:** Reintroduce la jerarquía en las cuentas analíticas.
*   **Dependencias:** `account`, `analytic`
*   **Explicación para el contador:** Permite crear una estructura de árbol con las cuentas analíticas, por ejemplo, un proyecto principal con sub-proyectos.
*   **Explicación para el desarrollador:** Añade un campo `parent_id` a `account.analytic.account`.
*   **Explicación para dummies:** Permite organizar tus proyectos en carpetas y subcarpetas.

## Módulo: hr_timesheet_analytic_tag

*   **Funcionalidad:** Permite asignar etiquetas analíticas a las hojas de horas.
*   **Dependencias:** `hr_timesheet`, `account_analytic_tag`
*   **Explicación para el contador:** Permite un análisis más detallado de los costos de personal por diferentes dimensiones.
*   **Explicación para el desarrollador:** Agrega un campo de etiquetas analíticas a `account.analytic.line` (timesheets).
*   **Explicación para dummies:** Permite etiquetar las horas que un empleado dedica a una tarea para saber, por ejemplo, que fueron para "Desarrollo" y para el "Proyecto X".

## Módulo: account_analytic_distribution_widget_rebalance

*   **Funcionalidad:** Añade un botón para rebalancear la distribución analítica al 100%.
*   **Dependencias:** `analytic`
*   **Explicación para el contador:** Si estás dividiendo un gasto en porcentajes, este botón te ayuda a asegurarte de que la suma de los porcentajes sea siempre 100%.
*   **Explicación para el desarrollador:** Añade un widget con un botón que ajusta los porcentajes de la distribución analítica.
*   **Explicación para dummies:** Es como un botón de "repartir a partes iguales" para tus gastos.

## Módulo: account_analytic_spread_by_tag

*   **Funcionalidad:** Permite la distribución de costos analíticos por etiqueta.
*   **Dependencias:** `account_analytic_tag`
*   **Explicación para el contador:** Permite distribuir un costo entre varias cuentas analíticas basándose en etiquetas.
*   **Explicación para el desarrollador:** Extiende la funcionalidad de las etiquetas analíticas para permitir la distribución de costos.
*   **Explicación para dummies:** Permite repartir un gasto entre varios proyectos usando etiquetas.

# Directorio: account-financial-tools

## Módulo: account_lock_to_date

*   **Funcionalidad:** Permite establecer una fecha de bloqueo contable en el futuro.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Evita que se registren asientos contables en un período futuro que aún no se ha revisado.
*   **Explicación para el desarrollador:** Añade un wizard para actualizar la fecha de bloqueo.
*   **Explicación para dummies:** Es como poner una barrera para que nadie pueda añadir gastos o ingresos en el futuro por error.

## Módulo: account_asset_force_account

*   **Funcionalidad:** Permite forzar cuentas específicas para los activos.
*   **Dependencias:** `account_asset_management`
*   **Explicación para el contador:** Asegura que los activos se registren siempre en las cuentas contables correctas, evitando errores.
*   **Explicación para el desarrollador:** Añade una restricción en los perfiles de activos para forzar las cuentas de depreciación y gastos.
*   **Explicación para dummies:** Es como una regla que dice que todos los coches de la empresa deben ir a la misma cuenta contable.

## Módulo: account_account_tag_code

*   **Funcionalidad:** Añade un campo de código a las etiquetas de las cuentas.
*   **Dependencias:** `account`, `account_usability`
*   **Explicación para el contador:** Facilita la identificación y el uso de las etiquetas de cuenta, especialmente si tienes muchas.
*   **Explicación para el desarrollador:** Añade un campo `code` al modelo `account.account.tag`.
*   **Explicación para dummies:** Le pone un código corto a las etiquetas para que sea más fácil encontrarlas.

## Módulo: account_chart_update

*   **Funcionalidad:** Detecta cambios y actualiza el plan de cuentas desde una plantilla.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Facilita la actualización del plan de cuentas si hay cambios en la normativa o en la estructura de la empresa.
*   **Explicación para el desarrollador:** Proporciona un wizard para comparar y actualizar el plan de cuentas.
*   **Explicación para dummies:** Actualiza tu lista de cuentas contables automáticamente.

## Módulo: account_move_line_tax_editable

*   **Funcionalidad:** Permite editar los impuestos en los apuntes contables no publicados.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite corregir los impuestos de una factura antes de validarla.
*   **Explicación para el desarrollador:** Hace que el campo de impuestos en `account.move.line` sea editable en ciertos estados.
*   **Explicación para dummies:** Te deja cambiar los impuestos de una factura si te equivocaste.

## Módulo: account_move_post_date_user

*   **Funcionalidad:** Rastrea la fecha y el usuario de publicación de los asientos contables.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite saber quién y cuándo validó una factura.
*   **Explicación para el desarrollador:** Añade campos para registrar el usuario y la fecha de publicación en `account.move`.
*   **Explicación para dummies:** Guarda un registro de quién y cuándo se aprueba cada factura.

## Módulo: mail_template_substitute_account_move

*   **Funcionalidad:** Permite usar plantillas de correo con sustitución de texto para los asientos contables.
*   **Dependencias:** `account`, `mail_template_substitute`
*   **Explicación para el contador:** Permite crear plantillas de correo personalizadas para enviar facturas, con campos que se rellenan automáticamente.
*   **Explicación para el desarrollador:** Integra la funcionalidad de `mail_template_substitute` con `account.move`.
*   **Explicación para dummies:** Te deja crear plantillas de correo para enviar facturas, como si fueran cartas personalizadas.

## Módulo: account_check_deposit

*   **Funcionalidad:** Gestiona el depósito de cheques en el banco.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Agrupa los cheques recibidos para generar un único depósito bancario, facilitando la conciliación.
*   **Explicación para el desarrollador:** Crea el modelo `account.check.deposit` para registrar los depósitos.
*   **Explicación para dummies:** Es una bolsa virtual para guardar los cheques antes de llevarlos al banco.

## Módulo: account_asset_management_stock_lot

*   **Funcionalidad:** Vincula los activos con los lotes de stock.
*   **Dependencias:** `account_asset_management`, `stock`
*   **Explicación para el contador:** Permite rastrear los activos a nivel de lote o número de serie.
*   **Explicación para el desarrollador:** Añade una relación entre `account.asset` y `stock.lot`.
*   **Explicación para dummies:** Te deja saber exactamente qué número de serie tiene cada ordenador de la empresa.

## Módulo: account_spread_cost_revenue

*   **Funcionalidad:** Reparte los costos e ingresos a lo largo de un período personalizado.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite periodificar gastos e ingresos, como un seguro anual que se quiere contabilizar mes a mes.
*   **Explicación para el desarrollador:** Crea el modelo `account.spread` para gestionar la distribución de costos e ingresos en el tiempo.
*   **Explicación para dummies:** Te deja repartir un gasto grande en varios meses, para que no parezca que has gastado mucho de golpe.

## Módulo: account_move_line_purchase_info

*   **Funcionalidad:** Introduce la línea del pedido de compra en los apuntes contables.
*   **Dependencias:** `purchase_stock`, `base_view_inheritance_extension`
*   **Explicación para el contador:** Permite ver desde un apunte contable a qué línea de pedido de compra corresponde.
*   **Explicación para el desarrollador:** Añade una relación entre `account.move.line` y `purchase.order.line`.
*   **Explicación para dummies:** Te deja ver desde la factura qué producto exacto se compró.

## Módulo: account_partner_required

*   **Funcionalidad:** Añade una política de obligatoriedad de partner en las cuentas.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Obliga a que ciertos asientos contables tengan siempre un cliente o proveedor asociado.
*   **Explicación para el desarrollador:** Añade una opción en `account.account` para hacer el campo `partner_id` obligatorio.
*   **Explicación para dummies:** No te deja guardar un gasto si no dices a quién se lo pagaste.

## Módulo: account_journal_lock_date

*   **Funcionalidad:** Bloquea cada diario contable de forma independiente.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite cerrar un diario (por ejemplo, el de bancos) sin tener que cerrar todo el período contable.
*   **Explicación para el desarrollador:** Añade fechas de bloqueo a nivel de `account.journal`.
*   **Explicación para dummies:** Te deja cerrar la caja de un día sin tener que cerrar todo el mes.

## Módulo: account_move_print

*   **Funcionalidad:** Añade la opción de imprimir los asientos contables.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite tener una copia en papel o PDF de los asientos contables.
*   **Explicación para el desarrollador:** Añade un informe QWeb para `account.move`.
*   **Explicación para dummies:** Es un botón de "imprimir" para tus asientos contables.

## Módulo: account_sequence_option

*   **Funcionalidad:** Gestiona las opciones de secuencia para los asientos contables.
*   **Dependencias:** `account`, `base_sequence_option`
*   **Explicación para el contador:** Permite configurar cómo se numeran las facturas, asientos, etc.
*   **Explicación para el desarrollador:** Integra `base_sequence_option` con `account.move`.
*   **Explicación para dummies:** Te deja decidir si quieres que tus facturas se numeren como "FAC/2024/001" o de otra forma.

## Módulo: account_asset_management

*   **Funcionalidad:** Gestión completa de los activos fijos de la empresa.
*   **Dependencias:** `account`, `report_xlsx_helper`
*   **Explicación para el contador:** Permite llevar un control detallado de los activos, configurar métodos de depreciación y generar automáticamente los asientos correspondientes.
*   **Explicación para el desarrollador:** Crea modelos para gestionar activos, perfiles y grupos de activos, integrándose con `account.move`.
*   **Explicación para dummies:** Es el libro de mantenimiento de los bienes importantes de la empresa, como coches o edificios.

## Módulo: account_fiscal_year

*   **Funcionalidad:** Crea el año fiscal contable.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite definir el inicio y el fin del año fiscal de la empresa.
*   **Explicación para el desarrollador:** Crea el modelo `account.fiscal.year` para gestionar los períodos fiscales.
*   **Explicación para dummies:** Le dice al sistema cuándo empieza y cuándo acaba el año para la contabilidad de la empresa.

## Módulo: account_move_line_sale_info

*   **Funcionalidad:** Introduce la línea del pedido de venta en los apuntes contables.
*   **Dependencias:** `account_move_line_stock_info`, `sale_stock`
*   **Explicación para el contador:** Permite ver desde un apunte contable a qué línea de pedido de venta corresponde.
*   **Explicación para el desarrollador:** Añade una relación entre `account.move.line` y `sale.order.line`.
*   **Explicación para dummies:** Te deja ver desde la factura qué producto exacto se vendió.

## Módulo: account_tax_repartition_line_tax_group_account

*   **Funcionalidad:** Establece una cuenta por defecto del grupo de impuestos a las líneas de repartición de impuestos.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Facilita la configuración de los impuestos al asignar automáticamente la cuenta contable correcta.
*   **Explicación para el desarrollador:** Añade una automatización para asignar la cuenta desde `account.tax.group`.
*   **Explicación para dummies:** Ayuda a que los impuestos se contabilicen solos en la cuenta correcta.

## Módulo: purchase_unreconciled

*   **Funcionalidad:** Gestiona las compras no conciliadas.
*   **Dependencias:** `account_move_line_purchase_info`, `purchase_stock`
*   **Explicación para el contador:** Ayuda a identificar y gestionar las facturas de compra que no coinciden con las recepciones de mercancía.
*   **Explicación para el desarrollador:** Proporciona herramientas para la conciliación de facturas de compra y albaranes.
*   **Explicación para dummies:** Te avisa si una factura de un proveedor no coincide con lo que has recibido en el almacén.

## Módulo: account_lock_date_update

*   **Funcionalidad:** Permite a un asesor contable actualizar la fecha de bloqueo sin acceso a la configuración técnica.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite cambiar la fecha de cierre contable sin necesidad de tener permisos de administrador.
*   **Explicación para el desarrollador:** Proporciona un wizard con permisos específicos para actualizar la fecha de bloqueo.
*   **Explicación para dummies:** Es un acceso directo para que el contable pueda cambiar la fecha de cierre sin molestar al informático.

## Módulo: account_move_name_sequence

*   **Funcionalidad:** Genera el número del asiento contable a partir de una secuencia.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite tener una numeración personalizada y automática para los asientos contables.
*   **Explicación para el desarrollador:** Sobrescribe el comportamiento estándar de numeración de `account.move`.
*   **Explicación para dummies:** Le pone a los asientos contables el número que tú quieras, en el orden que tú quieras.

## Módulo: account_move_template

*   **Funcionalidad:** Plantillas para asientos contables recurrentes.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite crear plantillas para asientos que se repiten todos los meses, como el alquiler o las nóminas.
*   **Explicación para el desarrollador:** Crea el modelo `account.move.template` para guardar plantillas de asientos.
*   **Explicación para dummies:** Es como una plantilla de Word para tus gastos fijos.

## Módulo: account_chart_update_l10n_eu_oss

*   **Funcionalidad:** Extensión del `account_chart_update` para la localización europea OSS.
*   **Dependencias:** `account_chart_update`, `l10n_eu_oss`
*   **Explicación para el contador:** Si usas la ventanilla única (OSS) para el IVA en la UE, este módulo te ayuda a actualizar tu plan de cuentas.
*   **Explicación para el desarrollador:** Integra `account_chart_update` con las particularidades de `l10n_eu_oss`.
*   **Explicación para dummies:** Es una actualización para tus cuentas si vendes a varios países de Europa.

## Módulo: account_netting

*   **Funcionalidad:** Compensa las cuentas de clientes y proveedores del mismo partner.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Si un cliente es también tu proveedor, este módulo te permite cruzar las facturas de compra y venta para pagar o cobrar solo la diferencia.
*   **Explicación para el desarrollador:** Proporciona un wizard para crear asientos de compensación entre cuentas a cobrar y a pagar.
*   **Explicación para dummies:** Si le debes dinero a alguien que también te debe dinero a ti, esto te deja hacer cuentas y pagar solo la diferencia.

## Módulo: account_journal_restrict_mode

*   **Funcionalidad:** Bloquea todos los asientos publicados de los diarios.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Evita que se modifiquen los asientos contables una vez validados.
*   **Explicación para el desarrollador:** Añade una restricción a nivel de diario para bloquear los asientos publicados.
*   **Explicación para dummies:** Es un candado para que nadie pueda cambiar los asientos contables una vez aprobados.

## Módulo: account_usability

*   **Funcionalidad:** Añade menús faltantes y la opción de habilitar la contabilidad sajona.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Mejora la usabilidad del módulo de contabilidad, añadiendo accesos directos y opciones de configuración.
*   **Explicación para el desarrollador:** Añade vistas y menús para facilitar el acceso a modelos contables.
*   **Explicación para dummies:** Pone botones y menús que faltaban en la contabilidad para que sea más fácil de usar.

## Módulo: account_loan

*   **Funcionalidad:** Gestión de préstamos.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite gestionar los préstamos de la empresa, generar los asientos de pago y calcular los intereses.
*   **Explicación para el desarrollador:** Crea el modelo `account.loan` para la gestión de préstamos.
*   **Explicación para dummies:** Es una libreta para apuntar los préstamos que pide la empresa y controlar los pagos.

## Módulo: account_move_budget

* **Funcionalidad:** Crea presupuestos contables.
* **Dependencias:** `account`, `date_range`
* **Explicación para el contador:** Permite crear presupuestos y compararlos con los gastos e ingresos reales.
* **Explicación para el desarrollador:** Crea el modelo `account.move.budget` para la gestión de presupuestos.
* **Explicación para dummies:** Te deja hacer un plan de gastos e ingresos para el futuro y ver si lo estás cumpliendo.

# Directorio: om

## Módulo: om_account_accountant

*   **Funcionalidad:** Módulo principal que agrupa funcionalidades contables como informes, gestión de activos, presupuestos, pagos recurrentes, seguimiento de clientes, etc.
*   **Dependencias:** `accounting_pdf_reports`, `om_account_asset`, `om_account_budget`, `om_fiscal_year`, `om_recurring_payments`, `om_account_daily_reports`, `om_account_followup`
*   **Explicación para el contador:** Es el centro de control contable, unificando el acceso a todas las herramientas financieras avanzadas.
*   **Explicación para el desarrollador:** Es un meta-módulo que instala y unifica un conjunto de módulos contables. Proporciona un menú coherente.
*   **Explicación para dummies:** La caja de herramientas principal para la contabilidad de la empresa.

## Módulo: accounting_pdf_reports

*   **Funcionalidad:** Genera una amplia variedad de informes financieros y contables en formato PDF.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite generar informes esenciales como el balance general, estado de resultados, libro mayor, y reportes de impuestos.
*   **Explicación para el desarrollador:** Añade informes QWeb y wizards para la generación de PDFs, que pueden ser extendidos.
*   **Explicación para dummies:** Es la "impresora" de informes bonitos para la contabilidad.

## Módulo: om_account_daily_reports

*   **Funcionalidad:** Genera informes diarios como el libro de caja, libro de bancos y libro diario.
*   **Dependencias:** `account`, `accounting_pdf_reports`
*   **Explicación para el contador:** Proporciona herramientas para la revisión diaria de las operaciones de efectivo y bancos.
*   **Explicación para el desarrollador:** Añade wizards e informes QWeb específicos para los reportes diarios.
*   **Explicación para dummies:** Te da un resumen diario de cómo se ha movido el dinero en efectivo y en el banco.

## Módulo: om_account_budget

*   **Funcionalidad:** Gestión de presupuestos.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite crear presupuestos, definir posiciones presupuestarias y comparar los importes reales con los planificados.
*   **Explicación para el desarrollador:** Introduce los modelos `crossovered.budget` y `crossovered.budget.lines` para la gestión presupuestaria.
*   **Explicación para dummies:** Te ayuda a planificar tus gastos e ingresos futuros y a ver si te estás pasando o no.

## Módulo: om_fiscal_year

*   **Funcionalidad:** Gestión de años fiscales y fechas de bloqueo.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite definir el inicio y fin del año fiscal y bloquear períodos para evitar modificaciones.
*   **Explicación para el desarrollador:** Crea el modelo `account.fiscal.year` y wizards para gestionar las fechas de bloqueo.
*   **Explicación para dummies:** Le dice al sistema cuándo empieza y termina el "año contable" de la empresa.

## Módulo: om_recurring_payments

*   **Funcionalidad:** Gestiona pagos recurrentes.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Automatiza la creación de facturas o pagos que se repiten periódicamente, como alquileres o suscripciones.
*   **Explicación para el desarrollador:** Introduce plantillas y un cron para la generación automática de pagos recurrentes.
*   **Explicación para dummies:** Programa los pagos que tienes que hacer todos los meses para que no se te olviden.

## Módulo: om_account_followup

*   **Funcionalidad:** Gestión de seguimiento de cobros a clientes.
*   **Dependencias:** `account`, `mail`
*   **Explicación para el contador:** Ayuda a gestionar las facturas vencidas, enviar recordatorios a clientes y llevar un control de los pagos pendientes.
*   **Explicación para el desarrollador:** Crea niveles de seguimiento y acciones automáticas (como enviar un email) basadas en la antigüedad de la deuda.
*   **Explicación para dummies:** Es un asistente que te ayuda a recordar a los clientes que te deben dinero.

## Módulo: om_account_asset

*   **Funcionalidad:** Gestión de activos fijos.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite registrar los activos de la empresa, calcular su depreciación automáticamente y generar los asientos contables correspondientes.
*   **Explicación para el desarrollador:** Introduce modelos para categorías de activos y los propios activos, generando `account.move` para las depreciaciones.
*   **Explicación para dummies:** Lleva la cuenta de las cosas de valor de la empresa (como ordenadores o coches) y cuánto valor pierden con el tiempo.

# Directorio: odoo-venezuela

## Módulo: l10n_ve_fiscal_lock_days

*   **Funcionalidad:** Restringe la creación de facturas según una cantidad de días configurables.
*   **Dependencias:** `account_accountant`, `l10n_ve_accountant`
*   **Explicación para el contador:** Permite establecer un límite de días hacia atrás para poder emitir o modificar facturas, evitando errores en períodos ya cerrados.
*   **Explicación para el desarrollador:** Añade una validación en `account.move` que comprueba la fecha de la factura contra la configuración de días de bloqueo.
*   **Explicación para dummies:** Es una regla que no te deja hacer facturas con fecha de hace más de X días.

## Módulo: l10n_ve_ref_bank

*   **Funcionalidad:** Valida referencias bancarias en los pagos.
*   **Dependencias:** `l10n_ve_invoice`
*   **Explicación para el contador:** Asegura que las referencias de pago de transferencias y otros métodos bancarios tengan el formato correcto y no se repitan.
*   **Explicación para el desarrollador:** Añade lógica de validación en `account.payment` para comprobar la unicidad y el formato de las referencias bancarias.
*   **Explicación para dummies:** Comprueba que el número de referencia que pones al registrar un pago sea válido y no lo hayas usado antes.

## Módulo: l10n_ve_payment_extension

*   **Funcionalidad:** Módulo principal para la gestión de retenciones de impuestos en Venezuela (IVA e ISLR).
*   **Dependencias:** `l10n_ve_rate`, `l10n_ve_accountant`, `l10n_ve_invoice`, etc.
*   **Explicación para el contador:** Permite generar y gestionar los comprobantes de retención de IVA e ISLR, tanto en compras como en ventas, y generar los reportes correspondientes.
*   **Explicación para el desarrollador:** Introduce los modelos `account.retention.line`, `account.retention.iva`, etc., y extiende `account.move` y `account.payment` para manejar la lógica de retenciones.
*   **Explicación para dummies:** Es la herramienta principal para calcular, registrar y declarar los impuestos que la empresa retiene a otros o que le retienen a ella.

## Módulo: l10n_ve_filter_partner

*   **Funcionalidad:** Módulo técnico para filtrar contactos de clientes y proveedores.
*   **Dependencias:** `web`
*   **Explicación para el contador:** Mejora la búsqueda de clientes y proveedores en los campos de selección.
*   **Explicación para el desarrollador:** Proporciona un "mixin" (una pieza de código reutilizable) para aplicar dominios de búsqueda predeterminados en los campos `partner_id`.
*   **Explicación para dummies:** Hace que sea más fácil y rápido encontrar un cliente o proveedor en las listas desplegables.

## Módulo: l10n_ve_pos_igtf

*   **Funcionalidad:** Calcula el IGTF (Impuesto a las Grandes Transacciones Financieras) en el Punto de Venta (POS).
*   **Dependencias:** `l10n_ve_pos`, `l10n_ve_igtf`
*   **Explicación para el contador:** Aplica el IGTF automáticamente en el POS cuando un cliente paga con moneda extranjera en efectivo.
*   **Explicación para el desarrollador:** Extiende la lógica del POS para añadir el cálculo del IGTF en las líneas de pago y en el total del pedido.
*   **Explicación para dummies:** Calcula el impuesto especial que se cobra en la tienda si alguien paga con dólares en efectivo.

## Módulo: l10n_ve_pos

*   **Funcionalidad:** Adaptaciones del Punto de Venta (POS) para Venezuela.
*   **Dependencias:** `point_of_sale`, `l10n_ve_rate`, `l10n_ve_contact`, etc.
*   **Explicación para el contador:** Permite manejar múltiples monedas en el POS, mostrar precios en la moneda local y extranjera, y adaptar los informes de ventas.
*   **Explicación para el desarrollador:** Extiende las vistas y modelos del POS para incluir lógica de multi-moneda y campos requeridos por la localización.
*   **Explicación para dummies:** Adapta el programa de la caja registradora para que funcione con las reglas y monedas de Venezuela.

## Módulo: l10n_ve_purchase

*   **Funcionalidad:** Personalizaciones para el proceso de compras en Venezuela.
*   **Dependencias:** `purchase`, `account`
*   **Explicación para el contador:** Asegura que el flujo de compras cumpla con las normativas locales.
*   **Explicación para el desarrollador:** Añade campos y lógica específica en el modelo `purchase.order`.
*   **Explicación para dummies:** Ajusta el sistema de compras a como se hacen las cosas en Venezuela.

## Módulo: l10n_ve_location

*   **Funcionalidad:** Añade la estructura de localización geográfica de Venezuela (estados, municipios, parroquias).
*   **Dependencias:** `base`, `contacts`
*   **Explicación para el contador:** Permite registrar direcciones de clientes y proveedores de forma detallada y estandarizada según la división territorial de Venezuela.
*   **Explicación para el desarrollador:** Carga los datos geográficos de Venezuela en los modelos correspondientes y los enlaza con el modelo `res.partner`.
*   **Explicación para dummies:** Contiene la lista de todos los estados, ciudades y municipios de Venezuela para poner las direcciones correctamente.

## Módulo: l10n_ve_tax_payer

*   **Funcionalidad:** Módulo técnico para configurar los tipos de contribuyente en Venezuela.
*   **Dependencias:** `l10n_ve_rate`, `l10n_ve_tax`
*   **Explicación para el contador:** Permite clasificar a los clientes y a la propia empresa según su tipo de contribuyente (ordinario, especial, etc.), lo que afecta cómo se calculan los impuestos.
*   **Explicación para el desarrollador:** Extiende `res.partner` para añadir campos relacionados con la clasificación fiscal venezolana.
*   **Explicación para dummies:** Le dice al sistema si un cliente es "contribuyente especial" o no, para que sepa qué impuestos aplicarle.

## Módulo: l10n_ve_stock

*   **Funcionalidad:** Adaptaciones de inventario para la localización venezolana.
*   **Dependencias:** `stock`, `l10n_ve_tax`, `product`, etc.
*   **Explicación para el contador:** Ajusta la valoración del inventario y los informes relacionados para cumplir con las prácticas locales.
*   **Explicación para el desarrollador:** Modifica modelos como `product.category`, `stock.picking` y añade informes de inventario.
*   **Explicación para dummies:** Adapta el control del almacén a las reglas de Venezuela.

## Módulo: l10n_ve_accountant

*   **Funcionalidad:** Módulo central de la contabilidad venezolana.
*   **Dependencias:** `account_reports`, `l10n_ve_tax`, `l10n_ve_contact`, etc.
*   **Explicación para el contador:** Contiene el plan de cuentas, impuestos, y configuraciones base para la contabilidad en Venezuela.
*   **Explicación para el desarrollador:** Es el módulo principal que establece las bases contables de la localización, modificando `account.move`, `account.payment`, etc.
*   **Explicación para dummies:** Es el corazón de la contabilidad para que todo funcione según las leyes de Venezuela.

## Módulo: l10n_ve_rate

*   **Funcionalidad:** Módulo técnico para la configuración de tasas de cambio en Venezuela.
*   **Dependencias:** `l10n_ve_base`
*   **Explicación para el contador:** Permite configurar cómo se gestionarán las diferentes tasas de cambio (por ejemplo, BCV).
*   **Explicación para el desarrollador:** Proporciona la base para que otros módulos puedan obtener y utilizar las tasas de cambio.
*   **Explicación para dummies:** Es el encargado de saber a cuánto está el dólar cada día.

## Módulo: l10n_ve_contact

*   **Funcionalidad:** Añade campos específicos de Venezuela a los contactos (partners).
*   **Dependencias:** `contacts`, `l10n_ve_rate`, `l10n_ve_location`
*   **Explicación para el contador:** Permite registrar información fiscal importante de clientes y proveedores, como el RIF y el tipo de contribuyente.
*   **Explicación para el desarrollador:** Extiende el modelo `res.partner` con campos como el RIF, nacionalidad, etc.
*   **Explicación para dummies:** Añade las casillas para poner el RIF y otros datos venezolanos a tus contactos.

## Módulo: l10n_ve_invoice

*   **Funcionalidad:** Adaptaciones para la facturación en Venezuela.
*   **Dependencias:** `l10n_ve_accountant`, `od_journal_sequence`, etc.
*   **Explicación para el contador:** Gestiona los números de control de las facturas, el formato de impresión y otros requisitos fiscales para la facturación.
*   **Explicación para el desarrollador:** Extiende `account.move` para añadir el número de control, y personaliza la secuencia de facturación y los informes.
*   **Explicación para dummies:** Se asegura de que tus facturas tengan el formato y los números que exige el SENIAT.

## Módulo: l10n_ve_auditlog

*   **Funcionalidad:** Módulo de auditoría para la localización venezolana.
*   **Dependencias:** `l10n_ve_accountant`, `l10n_ve_payment_extension`
*   **Explicación para el contador:** Registra un historial de cambios en documentos importantes, como facturas y pagos, para fines de auditoría.
*   **Explicación para el desarrollador:** Crea modelos para registrar logs de auditoría sobre operaciones contables críticas.
*   **Explicación para dummies:** Es un "chismoso" que anota quién cambia qué cosa en la contabilidad.

## Módulo: l10n_ve_iot_mf

*   **Funcionalidad:** Integración con máquinas fiscales a través de la caja IoT.
*   **Dependencias:** `iot`, `l10n_ve_invoice`, etc.
*   **Explicación para el contador:** Permite que Odoo se comunique directamente con la impresora fiscal para imprimir las facturas.
*   **Explicación para el desarrollador:** Implementa la comunicación con las DLLs de las impresoras fiscales a través de la caja IoT de Odoo.
*   **Explicación para dummies:** Es el "traductor" que permite que Odoo hable con la impresora fiscal.

## Módulo: l10n_ve_tax

*   **Funcionalidad:** Configuración de impuestos para Venezuela.
*   **Dependencias:** `account`, `l10n_ve_base`, `l10n_ve_rate`
*   **Explicación para el contador:** Contiene la configuración de los diferentes tipos de IVA y otros impuestos aplicables en Venezuela.
*   **Explicación para el desarrollador:** Carga los impuestos (`account.tax`) con su configuración específica para Venezuela.
*   **Explicación para dummies:** Contiene todos los porcentajes de impuestos (IVA 16%, IVA reducido, etc.) que se usan en el país.

## Módulo: l10n_ve_sale

*   **Funcionalidad:** Adaptaciones para el proceso de ventas en Venezuela.
*   **Dependencias:** `sale_management`, `l10n_ve_invoice`, etc.
*   **Explicación para el contador:** Asegura que los pedidos de venta y presupuestos manejen correctamente la multi-moneda y los impuestos locales.
*   **Explicación para el desarrollador:** Extiende `sale.order` para añadir lógica de precios y visualización de monedas.
*   **Explicación para dummies:** Ajusta el sistema de ventas a como se hacen las cosas en Venezuela.

## Módulo: l10n_ve_studio

*   **Funcionalidad:** Limita el uso de Odoo Studio para la localización venezolana.
*   **Dependencias:** `l10n_ve_base`
*   **Explicación para el contador:** Evita que se realicen cambios con Odoo Studio que puedan romper la funcionalidad de la localización.
*   **Explicación para el desarrollador:** Oculta o deshabilita ciertas funcionalidades de Odoo Studio para proteger la integridad de los módulos de localización.
*   **Explicación para dummies:** Pone "cinta de no tocar" en algunas partes de Odoo Studio para que no se dañe la configuración de Venezuela.

## Módulo: l10n_ve_binaural

*   **Funcionalidad:** Plan de cuentas base para Venezuela.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Proporciona un plan de cuentas estándar y recomendado para empresas en Venezuela.
*   **Explicación para el desarrollador:** Es un módulo de datos que carga un `account.chart.template`.
*   **Explicación para dummies:** Es una lista de cuentas contables ya hecha para que puedas empezar a trabajar rápido.

## Módulo: od_journal_sequence

*   **Funcionalidad:** Secuencias personalizadas para los diarios contables.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Permite tener numeraciones diferentes y automáticas para cada tipo de operación en la contabilidad (facturas, notas de débito, etc.).
*   **Explicación para el desarrollador:** Extiende `account.journal` para permitir la configuración de secuencias más flexibles.
*   **Explicación para dummies:** Permite que las facturas tengan un número, las notas de débito otro, y así sucesivamente.

## Módulo: l10n_ve_stock_reports

*   **Funcionalidad:** Genera el informe del Libro de Inventario para Venezuela.
*   **Dependencias:** `stock`, `account`, `l10n_ve_invoice`, etc.
*   **Explicación para el contador:** Proporciona la herramienta para generar el Libro de Inventario en el formato requerido por la ley.
*   **Explicación para el desarrollador:** Añade un wizard y un informe QWeb/XLSX para generar el reporte a partir de los movimientos de inventario.
*   **Explicación para dummies:** Crea el informe oficial que tienes que entregar sobre lo que hay en tu almacén.

## Módulo: l10n_ve_stock_purchase

*   **Funcionalidad:** Integra las compras con el inventario para la localización.
*   **Dependencias:** `purchase_stock`
*   **Explicación para el contador:** Asegura que la información de las órdenes de compra fluya correctamente hacia los movimientos de inventario.
*   **Explicación para el desarrollador:** Es un módulo puente que conecta `purchase_stock` con la localización.
*   **Explicación para dummies:** Conecta el departamento de compras con el de almacén.

## Módulo: l10n_ve_stock_account

*   **Funcionalidad:** Integra el inventario con la contabilidad para la localización.
*   **Dependencias:** `l10n_ve_stock`, `l10n_ve_invoice`, etc.
*   **Explicación para el contador:** Gestiona las guías de despacho, notas de entrega y su impacto contable, incluyendo la facturación posterior.
*   **Explicación para el desarrollador:** Extiende `stock.picking` para añadir guías de despacho y la lógica para su facturación.
*   **Explicación para dummies:** Conecta el almacén con la facturación, permitiendo crear facturas a partir de lo que se despacha.

## Módulo: l10n_ve_igtf

*   **Funcionalidad:** Módulo base para el cálculo del IGTF.
*   **Dependencias:** `l10n_ve_rate`, `l10n_ve_invoice`, etc.
*   **Explicación para el contador:** Contiene la configuración y lógica base para el cálculo del IGTF en facturas y pagos.
*   **Explicación para el desarrollador:** Extiende `account.move` y `account.payment` para añadir la lógica del IGTF.
*   **Explicación para dummies:** Es el "cerebro" que sabe cómo y cuándo calcular el impuesto a los pagos en dólares.

## Módulo: l10n_ve_pos_mf

*   **Funcionalidad:** Integración del Punto de Venta con Máquinas Fiscales.
*   **Dependencias:** `l10n_ve_pos`, `pos_iot`, `l10n_ve_iot_mf`
*   **Explicación para el contador:** Permite que las ventas realizadas en el POS se impriman directamente en la impresora fiscal.
*   **Explicación para el desarrollador:** Conecta el flujo del POS con el módulo de IoT para impresoras fiscales.
*   **Explicación para dummies:** Hace que la caja registradora imprima las facturas en la impresora fiscal oficial.

## Módulo: account_fiscal_year_closing

*   **Funcionalidad:** Asistente genérico para el cierre del año fiscal.
*   **Dependencias:** `account`
*   **Explicación para el contador:** Proporciona una herramienta para generar los asientos de cierre y apertura del ejercicio contable.
*   **Explicación para el desarrollador:** Introduce un modelo para plantillas de cierre y un wizard para ejecutar el proceso.
*   **Explicación para dummies:** Es el asistente que te ayuda a "cerrar los libros" al final del año.

## Módulo: l10n_ve_currency_rate_live

*   **Funcionalidad:** Sincroniza automáticamente la tasa de cambio del BCV.
*   **Dependencias:** `l10n_ve_rate`, `currency_rate_live`
*   **Explicación para el contador:** Actualiza la tasa de cambio del dólar (BCV) todos los días de forma automática.
*   **Explicación para el desarrollador:** Implementa un servicio de `currency_rate_live` para obtener la tasa desde la API del BCV.
*   **Explicación para dummies:** Es un robot que actualiza el precio del dólar en el sistema todos los días.

## Módulo: l10n_ve_account_fiscalyear_closing

*   **Funcionalidad:** Adaptaciones del cierre fiscal para Venezuela.
*   **Dependencias:** `account_fiscal_year_closing`, `l10n_ve_contact`, `l10n_ve_rate`
*   **Explicación para el contador:** Adapta el proceso de cierre de año a las normativas y prácticas contables de Venezuela.
*   **Explicación para el desarrollador:** Extiende las plantillas de cierre fiscal con cuentas y configuraciones específicas de Venezuela.
*   **Explicación para dummies:** Ajusta el "cierre de libros" a las reglas de Venezuela.

## Módulo: l10n_binaural_hide_studio_menu

*   **Funcionalidad:** Oculta el menú de Odoo Studio basado en permisos.
*   **Dependencias:** `web`, `web_studio`
*   **Explicación para el contador:** Permite restringir qué usuarios pueden acceder a Odoo Studio para evitar cambios no deseados.
*   **Explicación para el desarrollador:** Utiliza Javascript para ocultar el menú de Studio si el usuario no pertenece a un grupo específico.
*   **Explicación para dummies:** Es un interruptor para esconder el botón de "Odoo Studio" a quienes no deben tocarlo.

## Módulo: l10n_ve_base

*   **Funcionalidad:** Módulo base técnico para la localización venezolana.
*   **Dependencias:** `base`, `web`
*   **Explicación para el contador:** Es un módulo técnico que no tiene impacto directo, pero es necesario para que otros módulos de la localización funcionen.
*   **Explicación para el desarrollador:** Contiene configuraciones y modelos base que son extendidos por otros módulos de la localización.
*   **Explicación para dummies:** Son los cimientos sobre los que se construyen los otros módulos de la localización de Venezuela.

## Módulo: l10n_ve_invoice_digital

*   **Funcionalidad:** Módulo para la facturación digital en Venezuela.
*   **Dependencias:** `l10n_ve_igtf`, `l10n_ve_iot_mf`, etc.
*   **Explicación para el contador:** Integra la facturación con las impresoras fiscales y gestiona las retenciones digitales.
*   **Explicación para el desarrollador:** Orquesta la comunicación entre la facturación, las impresoras fiscales y los módulos de retenciones.
*   **Explicación para dummies:** Es el que junta la factura, la impresora fiscal y las retenciones para que todo funcione digitalmente.

## Módulo: l10n_binaural

*   **Funcionalidad:** Plan de cuentas para Venezuela (Binaural).
*   **Dependencias:** `account`
*   **Explicación para el contador:** Proporciona un plan de cuentas alternativo y pre-configurado para empresas de servicios en Venezuela.
*   **Explicación para el desarrollador:** Es un módulo de datos que carga un plan de cuentas, impuestos y diarios.
*   **Explicación para dummies:** Es otra lista de cuentas contables ya hecha, especialmente para empresas de servicios.
