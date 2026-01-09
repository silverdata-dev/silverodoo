## Model: crm.lead
**Inherits:** mail.thread.cc, mail.thread.blacklist, mail.thread.phone, mail.activity.mixin, utm.mixin, format.address.mixin, mail.tracking.duration.mixin

### Fields:
- **name**: `Char`
- **user_id**: `Many2one`
  - **Relation:** `res.users`
- **user_company_ids**: `Many2many`
  - **Relation:** `res.company`
- **team_id**: `Many2one`
  - **Relation:** `crm.team`
- **lead_properties**: `Properties`
- **company_id**: `Many2one`
  - **Relation:** `res.company`
- **referred**: `Char`
- **description**: `Html`
- **active**: `Boolean`
- **type**: `Selection`
- **priority**: `Selection`
- **stage_id**: `Many2one`
  - **Relation:** `crm.stage`
- **stage_id_color**: `Integer`
- **tag_ids**: `Many2many`
  - **Relation:** `crm.tag`
- **color**: `Integer`
- **expected_revenue**: `Monetary`
- **prorated_revenue**: `Monetary`
- **recurring_revenue**: `Monetary`
- **recurring_plan**: `Many2one`
  - **Relation:** `crm.recurring.plan`
- **recurring_revenue_monthly**: `Monetary`
- **recurring_revenue_monthly_prorated**: `Monetary`
- **recurring_revenue_prorated**: `Monetary`
- **company_currency**: `Many2one`
  - **Relation:** `res.currency`
- **date_closed**: `Datetime`
- **date_automation_last**: `Datetime`
- **date_open**: `Datetime`
- **day_open**: `Float`
- **day_close**: `Float`
- **date_last_stage_update**: `Datetime`
- **date_conversion**: `Datetime`
- **date_deadline**: `Date`
- **commercial_partner_id**: `Many2one`
  - **Relation:** `res.partner`
- **partner_id**: `Many2one`
  - **Relation:** `res.partner`
- **partner_is_blacklisted**: `Boolean`
- **contact_name**: `Char`
- **partner_name**: `Char`
- **function**: `Char`
- **email_from**: `Char`
- **email_normalized**: `Char`
- **email_domain_criterion**: `Char`
- **phone**: `Char`
- **phone_sanitized**: `Char`
- **phone_state**: `Selection`
- **email_state**: `Selection`
- **website**: `Char`
- **lang_id**: `Many2one`
  - **Relation:** `res.lang`
- **lang_code**: `Char`
- **lang_active_count**: `Integer`
- **street**: `Char`
- **street2**: `Char`
- **zip**: `Char`
- **city**: `Char`
- **state_id**: `Many2one`
  - **Relation:** `res.country.state`
- **country_id**: `Many2one`
  - **Relation:** `res.country`
- **probability**: `Float`
- **automated_probability**: `Float`
- **is_automated_probability**: `Boolean`
- **won_status**: `Selection`
- **lost_reason_id**: `Many2one`
  - **Relation:** `crm.lost.reason`
- **calendar_event_ids**: `One2many`
  - **Relation:** `calendar.event`
- **duplicate_lead_ids**: `Many2many`
  - **Relation:** `crm.lead`
- **duplicate_lead_count**: `Integer`
- **meeting_display_date**: `Date`
- **meeting_display_label**: `Char`
- **partner_email_update**: `Boolean`
- **partner_phone_update**: `Boolean`
- **is_partner_visible**: `Boolean`
- **campaign_id**: `Many2one`
- **medium_id**: `Many2one`
- **source_id**: `Many2one`
## Model: crm.team
**Inherits:** mail.alias.mixin, crm.team

### Fields:
- **use_leads**: `Boolean`
- **use_opportunities**: `Boolean`
- **alias_id**: `Many2one`
- **assignment_enabled**: `Boolean`
- **assignment_auto_enabled**: `Boolean`
- **assignment_optout**: `Boolean`
- **assignment_max**: `Integer`
- **assignment_domain**: `Char`
- **lead_unassigned_count**: `Integer`
- **lead_all_assigned_month_count**: `Integer`
- **lead_all_assigned_month_exceeded**: `Boolean`
- **lead_properties_definition**: `PropertiesDefinition`
## Model: crm.stage

### Fields:
- **name**: `Char`
- **sequence**: `Integer`
- **is_won**: `Boolean`
- **rotting_threshold_days**: `Integer`
- **requirements**: `Text`
- **team_ids**: `Many2many`
  - **Relation:** `crm.team`
- **fold**: `Boolean`
- **team_count**: `Integer`
- **color**: `Integer`
## Model: Extension of res.partner
**Inherits:** res.partner

### Fields:
- **opportunity_ids**: `One2many`
  - **Relation:** `crm.lead`
- **opportunity_count**: `Integer`
## Model: Extension of crm.lead
**Inherits:** crm.lead

### Fields:
- **silver_address_id**: `Many2one`
  - **Relation:** `silver.address`
- **contract_id**: `Many2one`
  - **Relation:** `silver.contract`
- **plan_type_id**: `Many2one`
  - **Relation:** `silver.plan.type`
- **type_service_id**: `Many2one`
  - **Relation:** `silver.service.type`
- **product_id**: `Many2one`
  - **Relation:** `product.product`
- **node_id**: `Many2one`
  - **Relation:** `silver.node`
- **box_id**: `Many2one`
  - **Relation:** `silver.box`
- **zone_id**: `Many2one`
  - **Relation:** `silver.zone`
## Model: Extension of silver.box
**Inherits:** silver.box

### Fields:
## Model: Extension of silver.reception.channel
**Inherits:** silver.reception.channel

### Fields:
- **team_id**: `Many2one`
  - **Relation:** `crm.team`
