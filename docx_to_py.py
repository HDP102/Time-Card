#!/usr/bin/env python3
# Auto-generated from 'Illumio.docx' on 2026-10-09 14:37
# by docx_to_py.py — do not hand-edit; regenerate instead.
#
# META    : document properties and counts
# BLOCKS  : every paragraph / heading / table, in document order
# IMAGES  : embedded media inventory
# HF      : header and footer text
#
# Block shapes:
#   {"type":"heading","level":N,"text":...,"style":...}
#   {"type":"p","text":...,"style":...,"list":bool,"ilvl":N,
#     "runs":[...],"links":[...],"images":[...],"textbox":[...]}
#   {"type":"table","dims":[rows,cols],"rows":[[{"text":...},...],...]}

META = {'source': 'Illumio.docx',
 'extracted': '2026-10-09T14:37:47',
 'title': None,
 'author': 'Nithin Kumar Kandimalla',
 'last_modified_by': 'Nick Bauman',
 'created': '2026-08-26 04:44:00+00:00',
 'modified': '2026-09-28 17:18:00+00:00',
 'revision': 120,
 'paragraphs': 365,
 'headings': 33,
 'tables': 0,
 'words': 6130,
 'sections': 1}

IMAGES = [{'file': 'image1.png', 'bytes': 1924579},
 {'file': 'image2.png', 'bytes': 1596347},
 {'file': 'image3.png', 'bytes': 1680501},
 {'file': 'image4.png', 'bytes': 1602894},
 {'file': 'image5.png', 'bytes': 1522454},
 {'file': 'image6.png', 'bytes': 1543314}]

HF = {'headers': [], 'footers': []}

BLOCKS = [{'type': 'heading',
  'text': 'Illumio Application Enforcement Procedure',
  'style': 'Title',
  'level': 0},
 {'type': 'heading', 'text': 'Purpose', 'style': 'Heading 1', 'level': 1},
 {'type': 'p',
  'text': 'This procedure provides Network Security Support and Engineering with a repeatable '
          'lifecycle process for validating, preparing, enforcing, and cleaning up Illumio '
          'segmentation controls for Azure-hosted application resources protected through Illumio '
          'Cloud Secure and Azure-native enforcement controls.'},
 {'type': 'p',
  'text': 'The procedure supports the transition from the current non-greenfield state — where '
          'Azure resources may already be represented by Illumio Core VENs, unmanaged objects, '
          'existing Core policy, or Cloud Secure-discovered resources — to a controlled '
          'enforcement model using Illumio Cloud Secure-managed Azure NSG policy where '
          'appropriate. The process is performed at the application/environment pair level to '
          'maintain policy continuity, support phased validation and enforcement, and ensure '
          'retained exceptions or cleanup actions are documented.'},
 {'type': 'heading', 'text': 'Scope', 'style': 'Heading 1', 'level': 1},
 {'type': 'p',
  'text': 'This procedure applies to Azure-hosted application resources in scope for Illumio Cloud '
          'Secure segmentation, including:'},
 {'type': 'p',
  'text': 'Azure-Only applications, where Azure resources do not require reuse or extension of '
          'existing Illumio Core labels, VEN-based policy, unmanaged objects, or Core rulesets',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '1'},
 {'type': 'p',
  'text': 'Hybrid applications, where Azure resources or related application components have '
          'existing Illumio Core labels, VENs, unmanaged objects, or reusable Core rulesets that '
          'may need to be preserved, updated, or extended during transition',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '1'},
 {'type': 'p',
  'text': 'This procedure focuses on operational activities performed by Network Security Support '
          'and Engineering, including Azure inventory validation, tag and label readiness, Illumio '
          'Cloud Secure and Illumio Core ruleset updates, traffic review, enforcement, and '
          'post-enforcement cleanup. Standard change-management, testing, exception, and rollback '
          'practices apply where resources, labels, rulesets, rules, VEN enforcement mode, Azure '
          'NSG enforcement, unmanaged objects, or policy artifacts are modified.'},
 {'type': 'p',
  'text': 'The Workload Mapping for Illumio CORE TO ICS workbook is used as the starting inventory '
          'and label-reference input. The ICS Migration Tracking workbook is used to track phase '
          'status, step progress, and follow-up items.',
  'runs': [{'text': 'The '},
           {'text': 'Workload Mapping for Illumio CORE TO ICS', 'b': True},
           {'text': ' workbook is used as the starting inventory and label-reference input. The '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook is used to track phase status, step progress, and follow-up '
                    'items.'}]},
 {'type': 'p',
  'text': 'Progress for this effort will be maintained in the ICS Migration Tracking workbook at '
          'the application/environment pair level. Each pair will track the current phase and step '
          'status using the standard states of Not Started, In Progress, On Hold, and Complete. '
          'Unresolved issues, blockers, retained artifacts, or accepted non-blocking items should '
          'be documented in the Follow Up Items tab with owner/action where applicable.',
  'runs': [{'text': 'Progress for this effort will be maintained in the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook at the application/environment pair level. Each pair will track the '
                    'current phase and step status using the standard states of Not Started, In '
                    'Progress, On Hold, and Complete. Unresolved issues, blockers, retained '
                    'artifacts, or accepted non-blocking items should be documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with owner/action where applicable.'}]},
 {'type': 'p',
  'text': 'Assignment and sequencing guidance',
  'runs': [{'text': 'Assignment and sequencing guidance', 'b': True}]},
 {'type': 'p',
  'text': 'Applications should be assigned to specific Network Security team members in the ICS '
          'Migration Tracking workbook so each application/environment pair has a clear owner for '
          'validation, policy preparation, enforcement coordination, and follow-up tracking.',
  'runs': [{'text': 'Applications should be assigned to specific Network Security team members in '
                    'the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' '},
           {'text': 'workbook'},
           {'text': ' so each application/environment pair has a clear owner for validation, '
                    'policy preparation, enforcement coordination, and follow-up tracking.'}]},
 {'type': 'p',
  'text': 'When sequencing work, prioritize Hybrid applications first where practical because '
          'existing Illumio Core labels, VENs, unmanaged objects, and rulesets are more likely to '
          'provide a reusable policy starting point. Azure-Only applications can follow where new '
          'Cloud Secure policy structure is required.'},
 {'type': 'p',
  'text': 'For each application, work through the application/environment pairs from the lowest '
          'environment to the highest environment, ending with Production. A higher environment '
          'should not be enforced before the lower environments for that same application have '
          'completed enforcement or have an approved exception.'},
 {'type': 'p',
  'text': 'Work across different applications may proceed in parallel when team capacity, SME '
          'availability, and change windows allow. However, enforcement sequencing within a single '
          'application should remain ordered by environment to reduce the risk of enforcing higher '
          'environments before lower-environment validation and tuning are complete.'},
 {'type': 'p',
  'text': '',
  'images': [{'rid': 'rId8',
              'file': 'image1.png',
              'w_in': 6.5,
              'h_in': 4.33,
              'name': 'Picture 1'}]},
 {'type': 'heading',
  'text': 'Phase 1: Application Validation and Resource Verification',
  'style': 'Heading 1',
  'level': 1},
 {'type': 'p',
  'text': 'Objective: Validate the assigned Azure application, confirm ownership and CMDB '
          'alignment, reconcile the inventory snapshot against current Azure and Illumio Cloud '
          'Secure visibility, verify Azure tag-to-label mapping, and determine whether existing '
          'Illumio Core labels, VENs, unmanaged objects, or rulesets must be reused or extended.',
  'runs': [{'text': 'Objective', 'b': True, 'i': True, 'color': '2F5496'},
           {'text': ': Validate the assigned Azure application, confirm ownership and CMDB '
                    'alignment, reconcile the inventory snapshot against current Azure and Illumio '
                    'Cloud Secure visibility, verify Azure tag-to-label mapping, and determine '
                    'whether existing Illumio Core labels, VENs, unmanaged objects, or rulesets '
                    'must be reused or extended.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': '',
  'images': [{'rid': 'rId9',
              'file': 'image2.png',
              'w_in': 6.5,
              'h_in': 4.33,
              'name': 'Picture 1'}]},
 {'type': 'heading',
  'text': 'Step 1: Application Identification',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Ensures the assigned Azure application has a clear application definition, known owner '
          'or support team, SME contact, and reasonable alignment to an authoritative CMDB record '
          'before validation work begins.',
  'runs': [{'text': 'Ensures the assigned Azure application has a clear application definition, '
                    'known owner or support team, SME contact, and reasonable alignment to an '
                    'authoritative CMDB record before validation work begins.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Use the Workload Mapping for Illumio CORE TO ICS workbook as the starting inventory '
          'reference and the ICS Migration Tracking workbook as the application assignment, phase '
          'status, and follow-up tracker. From the assigned entry, select the target application '
          'for onboarding validation.',
  'runs': [{'text': 'Use the '},
           {'text': 'Workload Mapping for Illumio CORE TO ICS', 'b': True},
           {'text': ' workbook as the starting inventory reference and the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook as the application assignment, phase status, and follow-up tracker. '
                    'From the assigned entry, select the target application for onboarding '
                    'validation.'}]},
 {'type': 'p',
  'text': 'Verify the application name, expected Azure resource scope, ownership, and SME contact '
          'against available CMDB information and Application SME confirmation.'},
 {'type': 'p',
  'text': 'The goal is to establish a clear working application boundary. CMDB cleanup may be '
          'required later, but Phase 1 should not be delayed if the application can be clearly '
          'identified, assigned, and validated. Document unresolved CMDB, naming, ownership, or '
          'SME contact issues in the Follow Up Items tab of the ICS Migration Tracking workbook.',
  'runs': [{'text': 'The goal is to establish a clear working application boundary. CMDB cleanup '
                    'may be required later, but Phase 1 should not be delayed if the application '
                    'can be clearly identified, assigned, and validated. Document unresolved CMDB, '
                    'naming, ownership, or SME contact issues in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab of the ICS Migration Tracking workbook.'}]},
 {'type': 'p', 'text': 'Verify that:'},
 {'type': 'p',
  'text': 'Application name is correct or has been reconciled with the Application SME.',
  'list': True,
  'ilvl': 0,
  'num_id': '21'},
 {'type': 'p',
  'text': 'Application has an identifiable business owner, technical owner, owning support team, '
          'or Application SME contact.',
  'list': True,
  'ilvl': 0,
  'num_id': '21'},
 {'type': 'p',
  'text': 'Application maps to an authoritative CMDB record where possible.',
  'list': True,
  'ilvl': 0,
  'num_id': '21'},
 {'type': 'p',
  'text': 'Expected Azure resource scope is understood well enough to support resource validation.',
  'list': True,
  'ilvl': 0,
  'num_id': '21'},
 {'type': 'p',
  'text': 'Any CMDB mismatch, naming inconsistency, ownership gap, or SME contact gap is '
          'documented in the Follow Up Items tab.',
  'list': True,
  'ilvl': 0,
  'num_id': '21',
  'runs': [{'text': 'Any CMDB mismatch, naming inconsistency, ownership gap, or SME contact gap is '
                    'documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab.'}]},
 {'type': 'heading',
  'text': 'Step 2: Determine Application Type',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Determines whether existing Illumio Core labels, VENs, unmanaged objects, or rulesets '
          'can be reused or extended, or whether a new Illumio Cloud Secure policy path is '
          'required.',
  'runs': [{'text': 'Determines whether existing Illumio Core labels, VENs, unmanaged objects, or '
                    'rulesets can be reused or extended, or whether a new Illumio Cloud Secure '
                    'policy path is required.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Review the application’s current Illumio representation before deciding the application '
          'type. The key decision is whether Azure resources already have Illumio Core labels, '
          'VENs, unmanaged objects, or rulesets that can be reused to preserve policy continuity.'},
 {'type': 'p',
  'text': 'Azure-Only Application',
  'runs': [{'text': 'Azure', 'b': True}, {'text': '-Only Application', 'b': True}]},
 {'type': 'p',
  'text': 'Use this classification when the application resources in scope are hosted in Azure and '
          'there are no existing Illumio Core labels, VEN-based policies, unmanaged objects, or '
          'application rulesets that need to be reused. Azure-Only applications follow a new '
          'Illumio Cloud Secure ruleset and Azure NSG enforcement path.'},
 {'type': 'p', 'text': 'Hybrid Application', 'runs': [{'text': 'Hybrid Application', 'b': True}]},
 {'type': 'p',
  'text': 'Use this classification when the application has existing Illumio Core labels, VENs, '
          'unmanaged objects, or rulesets that represent part of the application or are already '
          'used in policy. A VEN-managed workload with existing labels and policy should be '
          'treated as Hybrid because the existing Illumio Core policy may need to be reused, '
          'updated, or extended with Illumio Cloud Secure labels.'},
 {'type': 'p',
  'text': 'Document the application type in the ICS Migration Tracking workbook before proceeding. '
          'If the classification is unclear, document the issue in the Follow Up Items tab and '
          'review with the Application SME or Network Security Engineering before policy '
          'preparation begins.',
  'runs': [{'text': 'Document the application type in the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook before proceeding. If the classification is unclear, document the '
                    'issue in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab and review with the Application SME or Network Security Engineering '
                    'before policy preparation begins.'}]},
 {'type': 'p', 'text': 'Review the following before confirming the classification:'},
 {'type': 'p',
  'text': 'Review whether any Azure workloads already have Illumio VENs installed.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '22'},
 {'type': 'p',
  'text': 'Identify any existing Illumio Core Application, Environment, Role, or Location labels '
          'for the application.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '22'},
 {'type': 'p',
  'text': 'Identify any unmanaged objects currently representing Azure-hosted application '
          'resources or services.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '22'},
 {'type': 'p',
  'text': 'Search for existing Illumio Core rulesets or rules that reference the application '
          'labels.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '22'},
 {'type': 'p',
  'text': 'Classify the application as Hybrid if existing labels, VENs, unmanaged objects, or '
          'reusable Core policy are found.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '22',
  'runs': [{'text': 'Classify the application as '},
           {'text': 'Hybrid', 'b': True},
           {'text': ' if existing labels, VENs, unmanaged objects, or reusable Core policy are '
                    'found.'}]},
 {'type': 'p',
  'text': 'Classify the application as Azure-Only only when no existing Core policy structure '
          'needs to be reused or extended.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '22',
  'runs': [{'text': 'Classify the application as '},
           {'text': 'Azure-Only', 'b': True},
           {'text': ' only when no existing Core policy structure needs to be reused or '
                    'extended.'}]},
 {'type': 'p',
  'text': 'Document the classification and any unresolved questions in the ICS Migration Tracking '
          'workbook.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '22',
  'runs': [{'text': 'Document the classification and any unresolved questions in the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook.'}]},
 {'type': 'heading', 'text': 'Step 3: Resource Validation', 'style': 'Heading 2', 'level': 2},
 {'type': 'p',
  'text': 'Reconciles the inventory snapshot with current Azure inventory, Illumio Cloud Secure '
          'visibility, and Application SME confirmation to establish the working resource scope '
          'for the application/environment pair.',
  'runs': [{'text': 'Reconciles the inventory snapshot with current Azure inventory, Illumio Cloud '
                    'Secure visibility, and Application SME confirmation to establish the working '
                    'resource scope for the application/environment pair.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Use the inventory snapshot as the starting list of expected Azure resources, not the '
          'final authority. Reconcile it against current Azure inventory, Illumio Cloud Secure '
          'discovered resources, and Application SME confirmation.'},
 {'type': 'p',
  'text': 'Validate all supported Azure resource types in scope for the application, including '
          'compute, Kubernetes, databases, App Services, storage, Key Vaults, load balancers, '
          'private endpoints, firewalls, Redis, and Application Gateways.'},
 {'type': 'p', 'text': 'Validate all identified resources against:'},
 {'type': 'p',
  'text': 'Inventory snapshot verification workbook',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '3'},
 {'type': 'p',
  'text': 'Current Azure resource inventory',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '3'},
 {'type': 'p',
  'text': 'Illumio Cloud Secure discovered resources',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '3'},
 {'type': 'p',
  'text': 'Application SME confirmation',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '3'},
 {'type': 'p', 'text': 'Validation Requirements'},
 {'type': 'p', 'text': 'Confirm that:'},
 {'type': 'p',
  'text': 'Expected resources still present in Azure are included in the working validation scope.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '4'},
 {'type': 'p',
  'text': 'Resources no longer present in Azure are removed from the working scope after SME '
          'confirmation.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '4'},
 {'type': 'p',
  'text': 'Resources still present in Azure but not visible in Illumio Cloud Secure remain in '
          'scope and are documented as discovery issues.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '4'},
 {'type': 'p',
  'text': 'Unexpected or unknown resources are reviewed with the Application SME before inclusion.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '4'},
 {'type': 'p',
  'text': 'Resource mismatches, missing Cloud Secure discovery, unclear ownership, or SME '
          'follow-up items are documented in the Follow Up Items tab.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '4',
  'runs': [{'text': 'Resource mismatches, missing Cloud Secure discovery, unclear ownership, or '
                    'SME follow-up items are documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab.'}]},
 {'type': 'p',
  'text': 'The output of this step is a reconciled resource list for the application/environment '
          'pair, with each expected resource confirmed as present, removed, excluded, or requiring '
          'follow-up.'},
 {'type': 'heading', 'text': 'Step 4: Label Verification', 'style': 'Heading 2', 'level': 2},
 {'type': 'p',
  'text': 'Verifies that Azure tags map to the required Illumio Cloud Secure labels and that any '
          'existing Illumio Core VEN or unmanaged object labels are aligned where needed to '
          'maintain policy continuity during transition.',
  'runs': [{'text': 'Verifies that Azure tags map to the required Illumio Cloud Secure labels and '
                    'that any existing Illumio Core VEN or unmanaged object labels are aligned '
                    'where needed to maintain policy continuity during transition.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Use the Workload Mapping for Illumio CORE TO ICS workbook as the source for expected '
          'Application, Environment, and Role values. Use the ICS Migration Tracking workbook to '
          'track label readiness and unresolved follow-up items. Validate that Azure tags support '
          'the required Illumio Cloud Secure label mapping for each resource in the '
          'application/environment pair.',
  'runs': [{'text': 'Use the '},
           {'text': 'Workload Mapping for Illumio CORE TO ICS', 'b': True},
           {'text': ' workbook as the source for expected Application, Environment, and Role '
                    'values. Use the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook to track label readiness and unresolved follow-up items. Validate '
                    'that Azure tags support the required Illumio Cloud Secure label mapping for '
                    'each resource in the application/environment pair.'}]},
 {'type': 'p', 'text': 'Required Cloud Secure label review should include:'},
 {'type': 'p',
  'text': 'Application — mapped from the Azure application tag.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '5',
  'runs': [{'text': 'Application', 'b': True},
           {'text': ' — mapped from the Azure application tag.'}]},
 {'type': 'p',
  'text': 'Deployment — mapped from the Azure environment tag and used as the policy environment '
          'equivalent.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '5',
  'runs': [{'text': 'Deployment', 'b': True},
           {'text': ' — mapped from the Azure environment tag and used as the policy environment '
                    'equivalent.'}]},
 {'type': 'p',
  'text': 'Role — mapped from the Azure role tag where required for the resource type or policy '
          'design.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '5',
  'runs': [{'text': 'Role', 'b': True},
           {'text': ' — mapped from the Azure role tag where required for the resource type or '
                    'policy design.'}]},
 {'type': 'p',
  'text': 'Service Role — automatically applied by Illumio Cloud Secure for Azure resources and '
          'available for policy use later in the lifecycle.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '5',
  'runs': [{'text': 'Service Role', 'b': True},
           {'text': ' — automatically applied by Illumio Cloud Secure for Azure resources and '
                    'available for policy use later in the lifecycle.'}]},
 {'type': 'p',
  'text': 'For Hybrid applications, also review existing Illumio Core labels used by VENs, '
          'unmanaged objects, and reusable Core rulesets. Existing Core Application, Environment, '
          'Role, and Location labels should be preserved or aligned where needed to maintain '
          'policy continuity, but Azure tag validation should only focus on the approved Azure tag '
          'fields used for Cloud Secure labels.'},
 {'type': 'p',
  'text': 'Tag and Label Correction Process',
  'runs': [{'text': 'Tag and Label Correction Process', 'b': True}]},
 {'type': 'p',
  'text': 'If Azure tags are missing, incorrect, or do not map cleanly to the expected Illumio '
          'Cloud Secure labels, Network Security should not update tags directly for other teams. '
          'Instead, open a request with the appropriate resource SME or owning team to update the '
          'Azure tags.',
  'runs': [{'text': 'If Azure tags are missing, incorrect, or do not map cleanly to the expected '
                    'Illumio Cloud Secure labels, Network Security '},
           {'text': 'should not', 'b': True},
           {'text': ' update tags directly for other teams. Instead, '},
           {'text': 'open a request with the appropriate resource SME or owning team to update the '
                    'Azure tags.',
            'b': True}]},
 {'type': 'p',
  'text': 'Review the current Azure tags for each resource.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '6'},
 {'type': 'p',
  'text': 'Compare the tags to the expected Cloud Secure label mapping in the Workload Mapping for '
          'Illumio CORE TO ICS workbook.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '6',
  'runs': [{'text': 'Compare the tags to the expected Cloud Secure label mapping in the '},
           {'text': 'Workload Mapping for Illumio CORE TO ICS', 'b': True},
           {'text': ' workbook.'}]},
 {'type': 'p',
  'text': 'For Hybrid applications, compare existing Core labels with the corresponding Cloud '
          'Secure labels needed for policy reuse.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '6'},
 {'type': 'p',
  'text': 'Open a request to the resource SME or owning team for required Azure tag corrections.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '6'},
 {'type': 'p',
  'text': 'Document missing tags, label mismatches, missing Cloud Secure label availability, or '
          'unresolved Core-to-Cloud Secure alignment questions in the Follow Up Items tab.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '6',
  'runs': [{'text': 'Document missing tags, label mismatches, missing Cloud Secure label '
                    'availability, or unresolved Core-to-Cloud Secure alignment questions in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab.'}]},
 {'type': 'p',
  'text': 'Track the correction request until the updated resource is rediscovered or the label '
          'mapping is reconciled in Illumio Cloud Secure.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '6'},
 {'type': 'p',
  'text': 'Deployment Label Alignment',
  'runs': [{'text': 'Deployment Label Alignment', 'b': True}]},
 {'type': 'p',
  'text': 'Azure environment tags are limited to Sandbox, NonProd, QA, and Production and should '
          'align to the VNet where the resource is hosted. These values map to Illumio Cloud '
          'Secure Deployment labels and are used as the policy environment equivalent. Some '
          'existing Azure-hosted VENs or unmanaged objects may still use legacy Aurora environment '
          'labels such as DEV, INT, PreProd, or Test. Document any mismatch in the Follow Up Items '
          'tab and plan policy adjustments so existing Core labels can be corrected or bridged '
          'without disrupting current policy.',
  'runs': [{'text': 'Azure environment tags are limited to Sandbox, '},
           {'text': 'NonProd'},
           {'text': ', QA, and Production and should align to the '},
           {'text': 'VNet'},
           {'text': ' where the resource is hosted. These values map to Illumio Cloud Secure '
                    'Deployment labels and are used as the policy environment equivalent. Some '
                    'existing Azure-hosted VENs or unmanaged objects may still use legacy Aurora '
                    'environment labels such as DEV, INT, '},
           {'text': 'PreProd'},
           {'text': ', or Test. Document any mismatch in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab and plan policy adjustments so existing Core labels can be corrected or '
                    'bridged without disrupting current policy.'}]},
 {'type': 'p',
  'text': 'When existing VEN or unmanaged object labels must be changed, follow change-management '
          'standards and confirm the required testing and rollback plan before making the update.'},
 {'type': 'heading', 'text': 'Phase 1 Exit Criteria', 'style': 'Heading 2', 'level': 2},
 {'type': 'p', 'text': 'Phase 1 is complete when:'},
 {'type': 'p',
  'text': '✅ Application name, owner/support team, and SME contact validated or documented for '
          'follow-up',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Application name, owner/support team, and SME contact validated or '
                    'documented for follow-up'}]},
 {'type': 'p',
  'text': '✅ CMDB alignment confirmed or discrepancy documented in the Follow Up Items tab',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' CMDB alignment confirmed or discrepancy documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab'}]},
 {'type': 'p',
  'text': '✅ Application classified as Azure-Only or Hybrid based on whether existing Illumio Core '
          'labels, VENs, unmanaged objects, or reusable policy are present',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Application classified as '},
           {'text': 'Azure-Only', 'b': True},
           {'text': ' or '},
           {'text': 'Hybrid', 'b': True},
           {'text': ' based on whether existing Illumio Core labels, VENs, unmanaged objects, or '
                    'reusable policy are present'}]},
 {'type': 'p',
  'text': '✅ Inventory snapshot reconciled against current Azure inventory, Illumio Cloud Secure '
          'visibility, and Application SME confirmation',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Inventory snapshot reconciled against current Azure inventory, Illumio Cloud '
                    'Secure visibility, and Application SME confirmation'}]},
 {'type': 'p',
  'text': '✅ Reconciled resource list completed for the application/environment pair, with each '
          'expected resource marked as present, removed, excluded, or requiring follow-up',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Reconciled resource list completed for the application/environment pair, '
                    'with each expected resource marked as present, removed, excluded, or '
                    'requiring follow-up'}]},
 {'type': 'p',
  'text': '✅ Azure tags verified against expected Cloud Secure Application, Deployment, and Role '
          'label mapping',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Azure tags verified against expected Cloud Secure '},
           {'text': 'Application', 'b': True},
           {'text': ', '},
           {'text': 'Deployment', 'b': True},
           {'text': ', and '},
           {'text': 'Role', 'b': True},
           {'text': ' label mapping'}]},
 {'type': 'p',
  'text': '✅ Cloud Secure Service Role visibility understood where applicable; no Azure tag '
          'correction required for Service Role',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Cloud Secure '},
           {'text': 'Service Role', 'b': True},
           {'text': ' visibility understood where applicable; no Azure tag correction required for '
                    'Service Role'}]},
 {'type': 'p',
  'text': '✅ Required Azure tag or label follow-up items completed or documented in the Follow Up '
          'Items tab with owner/action',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Required Azure tag or label follow-up items completed or documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with owner/action'}]},
 {'type': 'p',
  'text': '✅ Existing Illumio Core label mismatches that could affect Hybrid policy reuse '
          'documented, corrected, or planned through change management',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Existing Illumio Core label mismatches that could affect Hybrid policy reuse '
                    'documented, corrected, or planned through change management'}]},
 {'type': 'p',
  'text': '✅ ICS Migration Tracking workbook updated with Phase 1 status and unresolved follow-up '
          'items',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook updated with Phase 1 status and unresolved follow-up items'}]},
 {'type': 'heading',
  'text': 'Phase 2: Ruleset Preparation and Policy Development',
  'style': 'Heading 1',
  'level': 1},
 {'type': 'p',
  'text': 'Objective: Prepare the required Illumio policy structure by confirming Cloud Secure '
          'label availability, removing unused generated rulesets where safe, creating Azure-Only '
          'Cloud Secure rulesets, or updating existing Hybrid/Core rulesets where policy '
          'continuity is required.',
  'runs': [{'text': 'Objective', 'b': True, 'i': True, 'color': '2F5496'},
           {'text': ': Prepare the required Illumio policy structure by confirming Cloud Secure '
                    'label availability, removing unused generated rulesets where safe, creating '
                    'Azure-Only Cloud Secure rulesets, or updating existing Hybrid/Core rulesets '
                    'where policy continuity is required.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': '',
  'images': [{'rid': 'rId10',
              'file': 'image3.png',
              'w_in': 6.5,
              'h_in': 4.33,
              'name': 'Picture 1'}]},
 {'type': 'heading',
  'text': 'Step 1: Confirm Illumio Cloud Secure Label Availability',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Confirms that the required Illumio Cloud Secure labels identified in Phase 1 are '
          'approved and available for ruleset scope and policy creation.',
  'runs': [{'text': 'Confirms that the required Illumio Cloud Secure labels identified in Phase 1 '
                    'are approved and available for ruleset scope and policy creation.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Phase 1 validates that Azure tags map to the expected Cloud Secure labels. Before '
          'creating or updating rulesets in Phase 2, confirm that the required labels are visible, '
          'approved, and available for policy use in Illumio Cloud Secure.'},
 {'type': 'p',
  'text': 'Cloud Secure Application label is available for the validated application.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '31',
  'runs': [{'text': 'Cloud Secure '},
           {'text': 'Application', 'b': True},
           {'text': ' label is available for the validated application.'}]},
 {'type': 'p',
  'text': 'Cloud Secure Deployment label is available for the validated environment.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '31',
  'runs': [{'text': 'Cloud Secure '},
           {'text': 'Deployment', 'b': True},
           {'text': ' label is available for the validated environment.'}]},
 {'type': 'p',
  'text': 'Required Application + Deployment pair is approved and available for ruleset scope.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '31',
  'runs': [{'text': 'Required '},
           {'text': 'Application + Deployment', 'b': True},
           {'text': ' pair is approved and available for ruleset scope.'}]},
 {'type': 'p',
  'text': 'Cloud Secure Role labels are available where required by the resource type or policy '
          'design.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '31',
  'runs': [{'text': 'Cloud Secure '},
           {'text': 'Role', 'b': True},
           {'text': ' labels are available where required by the resource type or policy '
                    'design.'}]},
 {'type': 'p',
  'text': 'Cloud Secure Service Role labels are visible where useful for Azure service policy '
          'decisions.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '31',
  'runs': [{'text': 'Cloud Secure '},
           {'text': 'Service Role', 'b': True},
           {'text': ' labels are visible '},
           {'text': 'where'},
           {'text': ' useful for Azure service policy decisions.'}]},
 {'type': 'p',
  'text': 'If any required label or Application/Deployment pair is missing, not approved, or '
          'unclear, document the issue in the Follow Up Items tab and resolve it before creating '
          'or updating rulesets.',
  'runs': [{'text': 'If any required label or Application/Deployment pair is missing, not '
                    'approved, or unclear, document the issue in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab and resolve it before creating or updating rulesets.'}]},
 {'type': 'p',
  'text': 'Label Namespace Consideration',
  'runs': [{'text': 'Label Namespace Consideration', 'b': True}]},
 {'type': 'p',
  'text': 'Labels learned through Illumio Cloud Secure and labels defined in Illumio Core are '
          'separate label namespaces, even when the display names are similar. For example, a '
          'Cloud Secure Application label for “App1” is separate from an Illumio Core Application '
          'label for “App1.”'},
 {'type': 'p',
  'text': 'Illumio Cloud Secure labels are used for Azure-discovered resources.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '7'},
 {'type': 'p',
  'text': 'Illumio Core labels are used for existing Core-managed workloads and may include legacy '
          'prefixes such as A:, E:, R:, or L:.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '7',
  'runs': [{'text': 'Illumio Core labels are used for existing Core-managed workloads and may '
                    'include legacy prefixes such as '},
           {'text': 'A:', 'b': True},
           {'text': ','},
           {'text': ' '},
           {'text': 'E:', 'b': True},
           {'text': ','},
           {'text': ' '},
           {'text': 'R:', 'b': True},
           {'text': ','},
           {'text': ' or '},
           {'text': 'L:', 'b': True},
           {'text': '.'}]},
 {'type': 'p',
  'text': 'Illumio Cloud Secure labels may use the ICS_ prefix.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '7',
  'runs': [{'text': 'Illumio Cloud Secure labels may use the '},
           {'text': 'ICS_', 'b': True},
           {'text': ' prefix.'}]},
 {'type': 'p',
  'text': 'Hybrid application policy may require both Core and Cloud Secure label versions in '
          'ruleset scopes or rules.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '7'},
 {'type': 'heading',
  'text': 'Step 2: Remove Unused Illumio Cloud Secure Rulesets',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Removes empty or obsolete Illumio Cloud Secure-generated rulesets before new policy '
          'work begins.',
  'runs': [{'text': 'Removes empty or obsolete Illumio Cloud Secure-generated rulesets before new '
                    'policy work begins.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'In an earlier Illumio Cloud Secure release, approving an Application and Deployment '
          'pair automatically created an empty ruleset with that pair as the scope. The current '
          'Illumio Cloud Secure version no longer creates these rulesets automatically.'},
 {'type': 'p',
  'text': 'Before creating or updating rulesets for this effort, review the existing policy list '
          'and identify any empty Illumio Cloud Secure-generated rulesets that may have been '
          'created by the earlier behavior.'},
 {'type': 'p', 'text': 'A ruleset may be removed when all of the following are true:'},
 {'type': 'p',
  'text': 'The ruleset has no rules.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '33'},
 {'type': 'p',
  'text': 'The ruleset was generated for an Application/Deployment pair and is not being used for '
          'active policy.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '33'},
 {'type': 'p',
  'text': 'The ruleset is not referenced by current onboarding, enforcement, exception, or '
          'migration work.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '33'},
 {'type': 'p',
  'text': 'The ruleset is not intentionally reserved for pending policy development.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '33'},
 {'type': 'p',
  'text': 'The assigned migration owner or Network Security Engineering confirms it is safe to '
          'remove, if the purpose is unclear.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '33'},
 {'type': 'p',
  'text': 'If the ruleset’s purpose cannot be confirmed, leave it in place and document the '
          'question in the Follow Up Items tab.',
  'runs': [{'text': 'If the ruleset’s purpose cannot be confirmed, leave it in place and document '
                    'the question in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab.'}]},
 {'type': 'p',
  'text': 'This cleanup reduces confusion and helps prevent policy from being built in stale, '
          'duplicate, or unused rulesets.'},
 {'type': 'heading',
  'text': 'Step 3: Determine Ruleset Approach',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Selects the correct ruleset approach based on whether the application requires a new '
          'Illumio Cloud Secure ruleset or updates to existing Illumio Core rulesets for policy '
          'continuity.',
  'runs': [{'text': 'Selects the correct ruleset approach based on whether the application '
                    'requires a new Illumio Cloud Secure ruleset or updates to existing Illumio '
                    'Core rulesets for policy continuity.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Use the application classification from Phase 1 to determine whether policy will be '
          'created in a new Illumio Cloud Secure ruleset or added to existing Illumio Core '
          'rulesets that already represent the application.'},
 {'type': 'heading',
  'text': 'Azure-Only Application Policy Creation',
  'style': 'Heading 3',
  'level': 3},
 {'type': 'p',
  'text': 'Creates a new Illumio Cloud Secure ruleset when no reusable Illumio Core policy '
          'structure exists for the application.',
  'runs': [{'text': 'Creates a new Illumio Cloud Secure ruleset when no reusable Illumio Core '
                    'policy structure exists for the application.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'For Azure-Only applications, create a dedicated Illumio Cloud Secure ruleset when no '
          'reusable Illumio Core ruleset or label structure exists for the application. Scope the '
          'ruleset to the approved Cloud Secure Application and Deployment labels for the '
          'validated application/environment pair.'},
 {'type': 'p',
  'text': 'Create a dedicated Illumio Cloud Secure ruleset for the application/environment pair.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '8'},
 {'type': 'p',
  'text': 'Set the ruleset scope using the approved Illumio Cloud Secure Application and '
          'Deployment labels.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '8'},
 {'type': 'p',
  'text': 'Leave detailed allow rules to Phase 3 traffic validation and policy tuning.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '8'},
 {'type': 'heading', 'text': 'Hybrid Application Policy Updates', 'style': 'Heading 3', 'level': 3},
 {'type': 'p',
  'text': 'Updates existing Illumio Core rulesets so Azure resources represented by Illumio Cloud '
          'Secure labels can participate in the same application policy model during transition.',
  'runs': [{'text': 'Updates existing Illumio Core rulesets so Azure resources represented by '
                    'Illumio Cloud Secure labels can participate in the same application policy '
                    'model during transition.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'For Hybrid applications, locate existing Illumio Core rulesets that already represent '
          'the application through Core labels, VEN-managed workloads, unmanaged objects, or '
          'existing policy rules. Update those rulesets where needed to include the corresponding '
          'Illumio Cloud Secure labels so Azure-discovered resources can participate in the same '
          'policy model during transition.'},
 {'type': 'p',
  'text': 'Do not create a separate Cloud Secure ruleset for a Hybrid application when the '
          'existing Core ruleset should remain the authoritative policy structure during '
          'transition.'},
 {'type': 'p',
  'text': 'When ruleset scopes or rules are changed, follow change-management standards and '
          'confirm the required testing and rollback plan before publishing the update.'},
 {'type': 'p', 'text': 'Required updates', 'runs': [{'text': 'Required updates', 'b': True}]},
 {'type': 'p',
  'text': 'Update ruleset scopes to include the required Illumio Core and Illumio Cloud Secure '
          'label versions where policy continuity is needed.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '20'},
 {'type': 'p',
  'text': 'Add explicit intra-application allow rules where needed so Core-managed resources and '
          'Cloud Secure-discovered Azure resources can communicate during transition.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '20'},
 {'type': 'p',
  'text': 'Apply change-management standards, required testing, and rollback planning before '
          'publishing ruleset scope or rule changes.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '20'},
 {'type': 'p', 'text': 'Labels to include', 'runs': [{'text': 'Labels to include', 'b': True}]},
 {'type': 'p',
  'text': 'Existing Illumio Core Application, Environment, Role, and Location labels used by '
          'current policy where applicable',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '9'},
 {'type': 'p',
  'text': 'Corresponding Illumio Cloud Secure Application and Deployment labels for Azure '
          'resources',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '9'},
 {'type': 'p',
  'text': 'Illumio Cloud Secure Role labels where required',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '9'},
 {'type': 'p',
  'text': 'Illumio Cloud Secure Service Role labels where useful for policy clarity',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '9'},
 {'type': 'p', 'text': 'Validation step', 'runs': [{'text': 'Validation step', 'b': True}]},
 {'type': 'p',
  'text': 'Use rule search to confirm every ruleset and rule that references the application’s '
          'existing Illumio Core labels has been reviewed and updated where the corresponding '
          'Illumio Cloud Secure labels must also be included.'},
 {'type': 'heading', 'text': 'Phase 2 Exit Criteria', 'style': 'Heading 2', 'level': 2},
 {'type': 'p', 'text': 'Phase 2 is complete when:'},
 {'type': 'p',
  'text': '✅ Required Illumio Cloud Secure Application, Deployment, and applicable Role labels '
          'approved and available for policy use',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Required Illumio Cloud Secure '},
           {'text': 'Application', 'b': True},
           {'text': ', '},
           {'text': 'Deployment', 'b': True},
           {'text': ', and applicable '},
           {'text': 'Role', 'b': True},
           {'text': ' labels approved and available for policy use'}]},
 {'type': 'p',
  'text': '✅ Required Application + Deployment pairs approved and available for ruleset scope',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Required '},
           {'text': 'Application + Deployment', 'b': True},
           {'text': ' pairs approved and available for ruleset scope'}]},
 {'type': 'p',
  'text': '✅ Empty or obsolete Illumio Cloud Secure-generated rulesets reviewed and removed where '
          'confirmed safe, or retained with documented rationale',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Empty or obsolete Illumio Cloud Secure-generated rulesets reviewed and '
                    'removed where confirmed safe, or retained with documented rationale'}]},
 {'type': 'p',
  'text': '✅ Azure-Only applications have a dedicated Illumio Cloud Secure ruleset scoped to the '
          'approved Application and Deployment labels',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Azure-Only applications have a dedicated Illumio Cloud Secure ruleset scoped '
                    'to the approved Application and Deployment labels'}]},
 {'type': 'p',
  'text': '✅ Hybrid applications have existing Illumio Core rulesets reviewed and updated where '
          'Cloud Secure labels are needed for policy continuity',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Hybrid applications have existing Illumio Core rulesets reviewed and updated '
                    'where Cloud Secure labels are needed for policy continuity'}]},
 {'type': 'p',
  'text': '✅ Required intra-application policy needs between Illumio Core and Illumio Cloud Secure '
          'label namespaces identified and documented for Phase 3 traffic validation or created '
          'where already validated',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Required intra-application policy needs between Illumio Core and Illumio '
                    'Cloud Secure label namespaces identified and documented for Phase 3 traffic '
                    'validation or created where already validated'}]},
 {'type': 'p',
  'text': '✅ Rule search completed to confirm affected rulesets and rules were reviewed for '
          'required Illumio Cloud Secure label updates',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Rule search completed to confirm affected rulesets and rules were reviewed '
                    'for required Illumio Cloud Secure label updates'}]},
 {'type': 'p',
  'text': '✅ Missing labels, unclear rulesets, or unresolved ruleset approach questions documented '
          'in the Follow Up Items tab with owner/action',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Missing labels, unclear rulesets, or unresolved ruleset approach questions '
                    'documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with owner/action'}]},
 {'type': 'p',
  'text': '✅ Application is ready for Phase 3 traffic validation with SME coordination',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Application is ready for Phase 3 traffic validation with SME coordination'}]},
 {'type': 'p',
  'text': '✅ ICS Migration Tracking workbook updated with Phase 2 status and unresolved follow-up '
          'items',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook updated with Phase 2 status and unresolved follow-up items'}]},
 {'type': 'heading',
  'text': 'Phase 3: Traffic Validation and Policy Tuning',
  'style': 'Heading 1',
  'level': 1},
 {'type': 'p',
  'text': 'Objective: Generate representative application traffic, classify observed flows as '
          'Required, Questionable, or Unnecessary with SME input, create or tune allow policy for '
          'validated Required Traffic, and prepare the application for enforcement planning.',
  'runs': [{'text': 'Objective', 'b': True, 'i': True, 'color': '2F5496'},
           {'text': ': Generate representative application traffic, classify observed flows as '
                    'Required, Questionable, or Unnecessary with SME input, create or tune allow '
                    'policy for validated Required Traffic, and prepare the application for '
                    'enforcement planning.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': '',
  'images': [{'rid': 'rId11',
              'file': 'image4.png',
              'w_in': 6.5,
              'h_in': 4.33,
              'name': 'Picture 1'}]},
 {'type': 'heading',
  'text': 'Step 1: Coordinate With Application SME',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Coordinates representative application activity with the SME so Illumio has enough '
          'observed traffic to support accurate policy creation and tuning.',
  'runs': [{'text': 'Coordinates representative application activity with the SME so Illumio has '
                    'enough observed traffic to support accurate policy creation and tuning.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Work with the Application SME to execute representative application functions and '
          'business transactions for the validated application/environment pair.'},
 {'type': 'p', 'text': 'Representative testing should include, where applicable:'},
 {'type': 'p',
  'text': 'Normal user workflows and business transactions',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '10'},
 {'type': 'p',
  'text': 'Application services and scheduled jobs',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '10'},
 {'type': 'p',
  'text': 'Batch processes, manual triggers, or infrequent business functions',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '10'},
 {'type': 'p',
  'text': 'Integration points, APIs, database connections, and shared service dependencies',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '10'},
 {'type': 'p',
  'text': 'End-to-end testing across the application components in scope',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '10'},
 {'type': 'p',
  'text': 'Document the workflows tested, the testing window, and any known workflows that could '
          'not be exercised during validation. If important workflows cannot be tested during the '
          'validation window, document the gap in the Follow Up Items tab with the owner and '
          'follow-up action.',
  'runs': [{'text': 'Document the workflows tested, the testing window, and any known workflows '
                    'that could not be exercised during validation. If important workflows cannot '
                    'be tested during the validation window, document the gap in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with the owner and follow-up action.'}]},
 {'type': 'p',
  'text': 'The goal is to generate enough valid traffic to distinguish required application '
          'communication from stale, unexpected, or unnecessary flows before policy is created or '
          'enforced.'},
 {'type': 'p',
  'text': 'The output of this step is a documented traffic generation activity for the '
          'application/environment pair, including tested workflows and unresolved testing gaps.'},
 {'type': 'heading', 'text': 'Step 2: Traffic Log Review', 'style': 'Heading 2', 'level': 2},
 {'type': 'p',
  'text': 'Uses Illumio Traffic View and logs to identify required, questionable, and unnecessary '
          'traffic before allow rules are created or enforcement is enabled.',
  'runs': [{'text': 'Uses Illumio Traffic View and logs to identify required, questionable, and '
                    'unnecessary traffic before ',
            'i': True,
            'color': '2F5496'},
           {'text': 'allow', 'i': True, 'color': '2F5496'},
           {'text': ' rules ', 'i': True, 'color': '2F5496'},
           {'text': 'are', 'i': True, 'color': '2F5496'},
           {'text': ' created or enforcement is enabled.', 'i': True, 'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Review application traffic in Illumio Cloud Secure Traffic View and supporting logs for '
          'the validated application/environment pair. Use the Phase 2 ruleset approach to '
          'determine whether flows should be reviewed against a new Cloud Secure ruleset or '
          'existing Hybrid/Core rulesets.'},
 {'type': 'p',
  'text': 'Focus on traffic shown as potentially blocked in draft mode because these flows do not '
          'currently have matching policy rules and would be blocked once enforcement is enabled. '
          'Traffic review may be performed directly in Illumio or exported to Excel for review '
          'with the Application SME.'},
 {'type': 'p', 'text': 'For each potentially blocked flow, review:'},
 {'type': 'p',
  'text': 'Source and destination labels',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '11'},
 {'type': 'p',
  'text': 'Ports and protocols',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '11'},
 {'type': 'p',
  'text': 'Application dependencies',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '11'},
 {'type': 'p',
  'text': 'Database and middleware communication',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '11'},
 {'type': 'p',
  'text': 'Shared enterprise services such as authentication, DNS, monitoring, backup, or '
          'vulnerability scanning',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '11'},
 {'type': 'p',
  'text': 'Unexpected, legacy, or unexplained flows',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '11'},
 {'type': 'p', 'text': 'Classify each flow with the Application SME:'},
 {'type': 'p',
  'text': 'Required Traffic — Communication needed for normal application functionality. Create or '
          'update policy to allow the flow.',
  'runs': [{'text': 'Required Traffic', 'b': True},
           {'text': ' — Communication needed for normal application functionality. Create or '
                    'update policy to allow the flow.'}]},
 {'type': 'p',
  'text': 'Questionable Traffic — Communication that needs SME review before a policy decision is '
          'made. Do not create an allow rule until the business need is confirmed. Document the '
          'question in the Follow Up Items tab with owner/action.',
  'runs': [{'text': 'Questionable Traffic', 'b': True},
           {'text': ' — Communication that needs SME review before a policy decision is made. Do '
                    'not create '},
           {'text': 'an'},
           {'text': ' allow rule until the business need is confirmed. Document the question in '
                    'the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with owner/action.'}]},
 {'type': 'p',
  'text': 'Unnecessary Traffic — Unused, legacy, or unexpected communication paths that should not '
          'be allowed without business justification. Exclude from policy unless the Application '
          'SME provides an approved business need.',
  'runs': [{'text': 'Unnecessary Traffic', 'b': True},
           {'text': ' — Unused, legacy, or unexpected communication paths that should not be '
                    'allowed without business justification. Exclude from policy unless the '
                    'Application SME provides an approved business need.'}]},
 {'type': 'p',
  'text': 'Every rule created from traffic review must include a rule comment documenting the '
          'business need or SME-approved justification for that rule.'},
 {'type': 'p',
  'text': 'The output of this step is a reviewed traffic list with flows classified as required, '
          'questionable, or unnecessary, and unresolved traffic questions documented for '
          'follow-up.'},
 {'type': 'heading',
  'text': 'Step 3: Policy Creation and Tuning',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Updates the required rulesets with SME-validated allow rules, business justification '
          'comments, and Hybrid label coverage where needed.',
  'runs': [{'text': 'Updates the required rulesets with SME-validated allow rules, business '
                    'justification comments, and Hybrid label coverage where needed.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Create or update allow rules only for flows classified as Required Traffic during Step '
          '2 and validated by the Application SME. Add the rules to the appropriate rulesets '
          'identified during Phase 2.',
  'runs': [{'text': 'Create'},
           {'text': ' or update allow rules only for flows classified as '},
           {'text': 'Required Traffic', 'b': True},
           {'text': ' during Step 2 and validated by the Application SME. Add the rules to the '
                    'appropriate rulesets identified during Phase 2.'}]},
 {'type': 'p',
  'text': 'For Azure-Only applications, create or update rules in the dedicated Illumio Cloud '
          'Secure ruleset scoped to the approved Application and Deployment labels. For Hybrid '
          'applications, update existing Illumio Core rulesets where Cloud Secure labels are '
          'needed to maintain policy continuity between Core-managed resources and Cloud '
          'Secure-discovered Azure resources.'},
 {'type': 'p',
  'text': 'Do not create allow rules for Questionable Traffic until the business need is '
          'confirmed. Unnecessary Traffic should remain excluded from policy unless later approved '
          'by the Application SME. Document unresolved traffic decisions, pending SME validation, '
          'or rule implementation blockers in the Follow Up Items tab.',
  'runs': [{'text': 'Do not '},
           {'text': 'create allow'},
           {'text': ' rules for '},
           {'text': 'Questionable Traffic', 'b': True},
           {'text': ' until the business need is confirmed. '},
           {'text': 'Unnecessary Traffic', 'b': True},
           {'text': ' should remain excluded from policy unless later approved by the Application '
                    'SME. Document unresolved traffic decisions, pending SME validation, or rule '
                    'implementation blockers in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab.'}]},
 {'type': 'p',
  'text': 'When modifying rulesets or rules, follow change-management standards and confirm the '
          'required testing and rollback plan before publishing the update.'},
 {'type': 'p',
  'text': 'Each rule should include the appropriate source, destination, port, protocol, and a '
          'rule comment that documents the business justification for the allowed communication.'},
 {'type': 'p', 'text': 'Supported policy updates may include:'},
 {'type': 'p',
  'text': 'Application-to-application communication',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '12'},
 {'type': 'p',
  'text': 'Database and data service communication',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '12'},
 {'type': 'p',
  'text': 'Authentication and directory services',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '12'},
 {'type': 'p',
  'text': 'Monitoring, backup, and vulnerability scanning services',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '12'},
 {'type': 'p',
  'text': 'Approved shared enterprise services',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '12'},
 {'type': 'p',
  'text': 'Hybrid application communication where the consumer, provider, or both require both '
          'Illumio Core and Illumio Cloud Secure label versions in the rule',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '12'},
 {'type': 'p',
  'text': 'After rules are created or updated, review Traffic View in draft mode again. Previously '
          'identified required flows should now show as allowed. If needed, coordinate another '
          'round of SME testing to regenerate traffic and confirm that the updated policy behaves '
          'as expected. Repeat traffic review and policy tuning until required traffic is allowed '
          'and unnecessary traffic remains excluded.'},
 {'type': 'p',
  'text': 'The output of this step is an updated policy set where required traffic is allowed, '
          'questionable traffic is tracked, and unnecessary traffic remains excluded.'},
 {'type': 'heading', 'text': 'Phase 3 Exit Criteria', 'style': 'Heading 2', 'level': 2},
 {'type': 'p', 'text': 'Phase 3 is complete when:'},
 {'type': 'p',
  'text': '✅ Representative traffic generated for the validated application/environment pair with '
          'Application SME coordination',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Representative traffic generated for the validated application/environment '
                    'pair with Application SME coordination'}]},
 {'type': 'p',
  'text': '✅ Tested workflows, testing window, and untested critical workflows documented',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Tested workflows, testing window, and untested critical workflows '
                    'documented'}]},
 {'type': 'p',
  'text': '✅ Illumio Cloud Secure Traffic View and supporting logs reviewed for potentially '
          'blocked traffic',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Illumio Cloud Secure Traffic View and supporting logs reviewed for '
                    'potentially blocked traffic'}]},
 {'type': 'p',
  'text': '✅ Traffic flows classified as Required, Questionable, or Unnecessary with Application '
          'SME input',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Traffic flows classified as '},
           {'text': 'Required', 'b': True},
           {'text': ', '},
           {'text': 'Questionable', 'b': True},
           {'text': ', or '},
           {'text': 'Unnecessary', 'b': True},
           {'text': ' with Application SME input'}]},
 {'type': 'p',
  'text': '✅ Required Traffic allow rules created or updated in the appropriate rulesets with rule '
          'comments documenting business justification',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Required Traffic allow rules created or updated in the appropriate rulesets '
                    'with rule comments documenting business justification'}]},
 {'type': 'p',
  'text': '✅ Questionable Traffic documented in the Follow Up Items tab with owner/action and no '
          'allow rule created until confirmed',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Questionable Traffic documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with owner/action and no allow rule created until confirmed'}]},
 {'type': 'p',
  'text': '✅ Unnecessary Traffic excluded from policy unless approved by the Application SME',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Unnecessary Traffic excluded from policy unless approved by the Application '
                    'SME'}]},
 {'type': 'p',
  'text': '✅ Hybrid consumer or provider rules include both Illumio Core and Cloud Secure label '
          'versions where required for policy continuity',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Hybrid consumer or provider rules include both Illumio Core and Cloud Secure '
                    'label versions where required for policy continuity'}]},
 {'type': 'p',
  'text': '✅ Draft-mode Traffic View confirms previously potentially blocked Required Traffic now '
          'shows as allowed',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Draft-mode Traffic'},
           {'text': ' View confirms previously potentially blocked Required Traffic now shows as '
                    'allowed'}]},
 {'type': 'p',
  'text': '✅ Policy tuning completed through one or more rounds of SME testing, log review, and '
          'rule refinement',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Policy tuning completed through one or more rounds of SME testing, log '
                    'review, and rule refinement'}]},
 {'type': 'p',
  'text': '✅ Application is ready for Phase 4 enforcement planning with unresolved traffic or '
          'testing gaps documented',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Application is ready for Phase 4 enforcement planning with unresolved '
                    'traffic or testing gaps documented'}]},
 {'type': 'p',
  'text': '✅ ICS Migration Tracking workbook updated with Phase 3 status and unresolved follow-up '
          'items',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook updated with Phase 3 status and unresolved follow-up items'}]},
 {'type': 'heading', 'text': 'Phase 4: Enforcement', 'style': 'Heading 1', 'level': 1},
 {'type': 'p',
  'text': 'Objective: Move the application into active enforcement after final readiness review, '
          'approved change scheduling, controlled VEN and/or Cloud Secure-managed Azure NSG '
          'enforcement, and coordinated post-enforcement validation and issue response.',
  'runs': [{'text': 'Objective', 'b': True, 'i': True, 'color': '2F5496'},
           {'text': ': Move the application into active enforcement after final readiness review, '
                    'approved change scheduling, controlled VEN and/or Cloud Secure-managed Azure '
                    'NSG ',
            'i': True,
            'color': '2F5496'},
           {'text': 'enforcement, and', 'i': True, 'color': '2F5496'},
           {'text': ' coordinated post-enforcement validation and issue response.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': '',
  'images': [{'rid': 'rId12',
              'file': 'image5.png',
              'w_in': 6.5,
              'h_in': 4.33,
              'name': 'Picture 1'}]},
 {'type': 'heading', 'text': 'Step 1: Final Readiness Review', 'style': 'Heading 2', 'level': 2},
 {'type': 'p',
  'text': 'Confirms the application/environment pair is ready for enforcement scheduling by '
          'reviewing scope, completed policy tuning, unresolved follow-up items, and recent '
          'traffic changes.',
  'runs': [{'text': 'Confirms the application/environment pair is ready for enforcement scheduling '
                    'by reviewing scope, completed policy tuning, unresolved follow-up items, and '
                    'recent traffic changes.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Before scheduling enforcement, perform a final readiness review for the '
          'application/environment pair and applicable Application + Deployment scope. Confirm the '
          'policy is still accurate, required traffic is allowed, and no unresolved blocker '
          'remains from Phase 3.'},
 {'type': 'p', 'text': 'Confirm that:'},
 {'type': 'p',
  'text': 'Application/environment scope still appears correct',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '39'},
 {'type': 'p',
  'text': 'Required Traffic identified during Phase 3 is allowed in draft-mode Traffic View',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '39'},
 {'type': 'p',
  'text': 'Questionable Traffic has been resolved, accepted as non-blocking, or documented in the '
          'Follow Up Items tab with owner/action',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '39',
  'runs': [{'text': 'Questionable Traffic has been resolved, accepted as non-blocking, or '
                    'documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with owner/action'}]},
 {'type': 'p',
  'text': 'Untested critical workflows from Phase 3 have been tested, accepted as non-blocking, or '
          'documented for follow-up',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '39'},
 {'type': 'p',
  'text': 'No material application, Azure, or environment changes occurred since the Phase 3 '
          'traffic review',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '39'},
 {'type': 'p',
  'text': 'Traffic View and logs do not show new required traffic that would be potentially '
          'blocked',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '39'},
 {'type': 'p',
  'text': 'Any final rule changes are completed and validated with the Application SME where '
          'needed',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '39'},
 {'type': 'p',
  'text': 'If new potentially blocked Required Traffic is identified, return to Phase 3 policy '
          'tuning before scheduling enforcement.'},
 {'type': 'p',
  'text': 'The output of this step is a go/no-go decision to proceed with enforcement scheduling.'},
 {'type': 'heading',
  'text': 'Step 2: Schedule Enforcement Change',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Creates the approved change record and coordinates enforcement timing, SME validation, '
          'and issue-response activities.',
  'runs': [{'text': 'Creates the approved change record and coordinates enforcement timing, SME '
                    'validation, and issue-response activities.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'After the final readiness review results in a go decision, schedule the enforcement '
          'change for the validated application/environment pair. Confirm the Application Owner or '
          'SME is available to perform post-enforcement validation during the agreed '
          'implementation window.'},
 {'type': 'p', 'text': 'The change should include:'},
 {'type': 'p',
  'text': 'Target application/environment pair and applicable Application + Deployment scope',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17'},
 {'type': 'p',
  'text': 'Scheduled enforcement date and implementation window',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17'},
 {'type': 'p',
  'text': 'Rulesets, labels, Azure NSGs, and Azure resources in scope',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17'},
 {'type': 'p',
  'text': 'Enforcement path being applied:',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17'},
 {'type': 'p',
  'text': 'VEN enforcement mode changes for Azure IaaS workloads with installed VENs, where '
          'applicable',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 1,
  'num_id': '17'},
 {'type': 'p',
  'text': 'Cloud Secure-managed Azure NSG inbound and outbound deny rules, where applicable',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 1,
  'num_id': '17'},
 {'type': 'p',
  'text': 'Post-enforcement validation plan, testing window, and SME contact',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17'},
 {'type': 'p',
  'text': 'Known unresolved follow-up items accepted as non-blocking',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17'},
 {'type': 'p',
  'text': 'Issue triage owner and communication path during the implementation window',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17'},
 {'type': 'p',
  'text': 'Rollback or issue-response approach',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17'},
 {'type': 'p',
  'text': 'ICS Migration Tracking workbook updated with the scheduled enforcement window and Phase '
          '4 status',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '17',
  'runs': [{'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook updated with the scheduled enforcement window and Phase 4 status'}]},
 {'type': 'heading', 'text': 'Step 3: Enable Enforcement', 'style': 'Heading 2', 'level': 2},
 {'type': 'p',
  'text': 'Applies the approved VEN and/or Cloud Secure-managed Azure NSG enforcement controls '
          'during the scheduled change window.',
  'runs': [{'text': 'Applies the approved VEN and/or Cloud Secure-managed Azure NSG enforcement '
                    'controls during the scheduled change window.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Enable enforcement only during the approved implementation window and only for the '
          'application/environment pair included in the change record.'},
 {'type': 'p',
  'text': 'Azure NSG enforcement through Illumio Cloud Secure is the target enforcement model for '
          'Azure resources. VEN enforcement applies only to Azure IaaS workloads that still have '
          'VENs installed during transition.'},
 {'type': 'p',
  'text': 'Azure IaaS workloads with VENs installed',
  'runs': [{'text': 'Azure IaaS workloads with VENs installed', 'b': True}]},
 {'type': 'p',
  'text': 'Change the enforcement status for each applicable VEN in the Illumio console. This '
          'causes the local firewall policy on each server to enforce the derived policy from the '
          'approved rulesets and disables the catch-all allow behavior used during the review '
          'phase.'},
 {'type': 'p',
  'text': 'Changing VEN enforcement mode must follow the approved change, validation testing, and '
          'rollback or issue-response plan.'},
 {'type': 'p',
  'text': 'Azure NSG enforcement through Illumio Cloud Secure',
  'runs': [{'text': 'Azure NSG enforcement through Illumio Cloud Secure', 'b': True}]},
 {'type': 'p',
  'text': 'For Azure NSGs in scope for the application/environment pair, Network Security creates '
          'Cloud Secure policy deny rules for inbound and outbound traffic that has not been '
          'explicitly allowed. Illumio Cloud Secure then programs the corresponding '
          'higher-priority deny entries into the applicable Azure NSGs.'},
 {'type': 'p',
  'text': 'After the deny rules are applied, unapproved traffic should begin appearing as denied '
          'in Azure logs and Illumio Traffic Explorer.'},
 {'type': 'p',
  'text': 'Adding Azure NSG deny rules must follow the approved change, validation testing, and '
          'rollback or issue-response plan.'},
 {'type': 'p', 'text': 'Confirm that:'},
 {'type': 'p',
  'text': 'The correct application/environment pair was enforced.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '41'},
 {'type': 'p',
  'text': 'VEN enforcement mode was changed only for approved Azure IaaS workloads with installed '
          'VENs.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '41'},
 {'type': 'p',
  'text': 'Cloud Secure-managed Azure NSG deny rules were applied only to approved Azure NSGs in '
          'scope.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '41'},
 {'type': 'p',
  'text': 'Expected deny entries are visible in the applicable Azure NSGs.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '41'},
 {'type': 'p',
  'text': 'Denied traffic is visible in Azure logs and Illumio Traffic Explorer where applicable.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '41'},
 {'type': 'p',
  'text': 'The ICS Migration Tracking workbook is updated with the enforcement status.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '41',
  'runs': [{'text': 'The '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook is updated with the enforcement status.'}]},
 {'type': 'p',
  'text': 'The output of this step is confirmed enforcement for the approved '
          'application/environment pair using the applicable VEN and/or Cloud Secure-managed Azure '
          'NSG controls.'},
 {'type': 'heading',
  'text': 'Step 4: Post-Enforcement Validation and Issue Response',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Validates application functionality after enforcement and uses denied traffic logs to '
          'confirm expected behavior, correct missed policy, or initiate the approved '
          'issue-response path.',
  'runs': [{'text': 'Validates application functionality after enforcement and uses denied traffic '
                    'logs to confirm expected behavior, correct missed policy, or initiate the '
                    'approved issue-response path.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'After enforcement is enabled, the Application Owner or SME should complete the agreed '
          'post-enforcement validation testing during the implementation window. Network Security '
          'should monitor Azure logs and Illumio Traffic Explorer for denied traffic related to '
          'the enforced application/environment pair.'},
 {'type': 'p', 'text': 'Validate that:'},
 {'type': 'p',
  'text': 'Required application workflows still function as expected.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '42'},
 {'type': 'p',
  'text': 'Previously validated Required Traffic remains allowed.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '42'},
 {'type': 'p',
  'text': 'Expected deny behavior is visible for traffic that was not explicitly allowed.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '42'},
 {'type': 'p',
  'text': 'No new business-required traffic is being denied.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '42'},
 {'type': 'p',
  'text': 'Application Owner or SME confirms the application remains functional after enforcement.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '42'},
 {'type': 'p',
  'text': 'If denied traffic is identified, classify it before making any policy change:'},
 {'type': 'p',
  'text': 'Expected Deny — Traffic that was not approved or required. No policy change is needed.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '43',
  'runs': [{'text': 'Expected Deny', 'b': True},
           {'text': ' — Traffic that was not approved or required. No policy change is needed.'}]},
 {'type': 'p',
  'text': 'Missed Required Traffic — Valid application traffic that should have been allowed. '
          'Update the applicable policy rule, include the business justification comment, publish '
          'the change, and retest with the Application SME.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '43',
  'runs': [{'text': 'Missed Required Traffic', 'b': True},
           {'text': ' — Valid application traffic that should have been allowed. Update the '
                    'applicable policy rule, include the business justification comment, publish '
                    'the change, and retest with the Application SME.'}]},
 {'type': 'p',
  'text': 'Unclear Traffic — Traffic that requires SME review before a policy decision is made. '
          'Document it in the Follow Up Items tab with owner/action and do not create an allow '
          'rule until confirmed.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '43',
  'runs': [{'text': 'Unclear Traffic', 'b': True},
           {'text': ' — Traffic that requires SME review before a policy decision is made. '
                    'Document it in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with owner/action and do not create an allow rule until confirmed.'}]},
 {'type': 'p',
  'text': 'If enforcement causes application impact that cannot be corrected within the approved '
          'implementation window, follow the change record’s rollback or issue-response approach. '
          'Capture denied traffic evidence before rollback where possible.'},
 {'type': 'p',
  'text': 'The output of this step is completed post-enforcement validation, documented issue '
          'response for any denied traffic, and confirmation that the application is stable under '
          'enforcement.'},
 {'type': 'heading', 'text': 'Phase 4 Exit Criteria', 'style': 'Heading 2', 'level': 2},
 {'type': 'p', 'text': 'Phase 4 is complete when:'},
 {'type': 'p',
  'text': '✅ Final readiness review completed for the application/environment pair and applicable '
          'Application + Deployment scope',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Final readiness review completed for the application/environment pair and '
                    'applicable Application + Deployment scope'}]},
 {'type': 'p',
  'text': '✅ Go/no-go decision documented before enforcement scheduling',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Go/no-go decision documented before enforcement scheduling'}]},
 {'type': 'p',
  'text': '✅ Enforcement change scheduled and approved with validation, issue-response, and '
          'rollback approach included',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Enforcement change scheduled and approved with validation, issue-response, '
                    'and rollback approach included'}]},
 {'type': 'p',
  'text': '✅ VEN enforcement status updated only for approved Azure IaaS workloads where '
          'applicable',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' VEN enforcement status updated only for approved Azure IaaS workloads where '
                    'applicable'}]},
 {'type': 'p',
  'text': '✅ Cloud Secure-managed Azure NSG inbound and outbound deny rules applied only to '
          'approved Azure NSGs in scope where applicable',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Cloud Secure-managed Azure NSG inbound and outbound deny rules applied only '
                    'to approved Azure NSGs in scope where applicable'}]},
 {'type': 'p',
  'text': '✅ Expected deny entries visible in the applicable Azure NSGs',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Expected deny entries visible in the applicable Azure NSGs'}]},
 {'type': 'p',
  'text': '✅ Denied traffic visible in Azure logs and Illumio Traffic Explorer where applicable',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Denied traffic visible in Azure logs and Illumio Traffic Explorer where '
                    'applicable'}]},
 {'type': 'p',
  'text': '✅ Post-enforcement validation completed by the Application Owner or SME',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Post-enforcement validation completed by the Application Owner or SME'}]},
 {'type': 'p',
  'text': '✅ Post-enforcement denied traffic classified as Expected Deny, Missed Required Traffic, '
          'or Unclear Traffic',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Post-enforcement denied traffic classified as Expected Deny, Missed Required '
                    'Traffic, or Unclear Traffic'}]},
 {'type': 'p',
  'text': '✅ Missed Required Traffic remediated and retested, or managed through the approved '
          'issue-response path',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Missed Required Traffic remediated and retested, or managed through the '
                    'approved issue-response path'}]},
 {'type': 'p',
  'text': '✅ Unclear Traffic documented in the Follow Up Items tab with owner/action',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Unclear Traffic documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab with owner/action'}]},
 {'type': 'p',
  'text': '✅ Application confirmed stable under enforcement',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Application confirmed stable under enforcement'}]},
 {'type': 'p',
  'text': '✅ ICS Migration Tracking workbook updated with Phase 4 status and unresolved follow-up '
          'items',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook updated with Phase 4 status and unresolved follow-up items'}]},
 {'type': 'heading', 'text': 'Phase 5: Post-Enforcement Cleanup', 'style': 'Heading 1', 'level': 1},
 {'type': 'p',
  'text': 'Objective: Remove or retain post-enforcement Illumio artifacts based on confirmed '
          'enforcement stability, reduce duplicate policy and visibility artifacts, document '
          'approved retained exceptions, and update operational records so Azure enforcement '
          'continues through Illumio Cloud Secure and Azure NSGs.',
  'runs': [{'text': 'Objective', 'b': True, 'i': True, 'color': '2F5496'},
           {'text': ': Remove or retain post-enforcement Illumio artifacts based on confirmed '
                    'enforcement stability, reduce duplicate policy and visibility artifacts, '
                    'document approved retained exceptions, and update operational records so '
                    'Azure enforcement continues through Illumio Cloud Secure and Azure NSGs.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': '',
  'images': [{'rid': 'rId13',
              'file': 'image6.png',
              'w_in': 6.5,
              'h_in': 4.33,
              'name': 'Picture 1'}]},
 {'type': 'heading',
  'text': 'Step 1: Remove VENs from Azure IaaS Workloads',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Removes VENs from Azure-hosted servers only after enforcement is stable and Azure NSGs '
          'provide the required segmentation control.',
  'runs': [{'text': 'Removes VENs from Azure-hosted servers only after enforcement is stable and '
                    'Azure NSGs provide the required segmentation control.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'After Phase 4 enforcement has been validated and the application remains stable for the '
          'agreed monitoring period, remove VENs from Azure-hosted IaaS workloads that no longer '
          'require host-based Illumio enforcement.'},
 {'type': 'p',
  'text': 'Before removing a VEN, confirm Azure NSG enforcement is active for the applicable '
          'application/environment pair, required traffic remains allowed, and rollback or '
          'recovery actions are documented in the approved change.'},
 {'type': 'p',
  'text': 'Confirm the application remains stable after Phase 4 enforcement and the agreed '
          'monitoring period is complete.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '13'},
 {'type': 'p',
  'text': 'Confirm Azure NSG enforcement provides the required segmentation control at the NIC or '
          'subnet level.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '13'},
 {'type': 'p',
  'text': 'Confirm no open Follow Up Items would block VEN removal for the application/environment '
          'pair.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '13'},
 {'type': 'p',
  'text': 'Remove VENs from Azure IaaS workloads where host-based enforcement is no longer '
          'required.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '13'},
 {'type': 'p',
  'text': 'Verify application functionality and denied-traffic behavior after VEN removal.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '13'},
 {'type': 'p',
  'text': 'Update the ICS Migration Tracking workbook with VEN removal status or any retained VEN '
          'rationale.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '13',
  'runs': [{'text': 'Update the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook with VEN removal status or any retained VEN rationale.'}]},
 {'type': 'heading',
  'text': 'Step 2: Remove Persistent Azure Unmanaged Objects',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Removes persistent Azure unmanaged objects only when Cloud Secure discovery and Azure '
          'NSG enforcement have replaced their policy purpose.',
  'runs': [{'text': 'Removes persistent Azure unmanaged objects only when Cloud Secure discovery '
                    'and Azure NSG enforcement have replaced their policy purpose.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Remove unmanaged objects that represent persistent Azure resources or services only '
          'after confirming the corresponding resources are visible in Illumio Cloud Secure and '
          'required policy is enforced through Azure NSGs.'},
 {'type': 'p',
  'text': 'Retain unmanaged objects when they are still required for policy continuity, '
          'operational stability, scale behavior, or an approved exception. Removing or changing '
          'unmanaged objects, including IP changes, must follow change-management standards.'},
 {'type': 'p',
  'text': 'Identify unmanaged objects that represent Azure-hosted resources or persistent Azure '
          'services.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '14'},
 {'type': 'p',
  'text': 'Confirm the corresponding resources are visible in Illumio Cloud Secure.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '14'},
 {'type': 'p',
  'text': 'Confirm required policy is enforced through Azure NSGs.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '14'},
 {'type': 'p',
  'text': 'Confirm the unmanaged object is not required by active Core policy, Hybrid transition '
          'rules, exception handling, or known scale behavior.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '14'},
 {'type': 'p',
  'text': 'Remove unmanaged objects that are no longer required for policy or visibility.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '14'},
 {'type': 'p',
  'text': 'Document retained unmanaged objects and the approved reason for retention.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '14'},
 {'type': 'p',
  'text': 'Update the ICS Migration Tracking workbook with unmanaged object cleanup status or '
          'retained-object rationale.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '14',
  'runs': [{'text': 'Update the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook with unmanaged object cleanup status or retained-object '
                    'rationale.'}]},
 {'type': 'p', 'text': 'Cloudera Exception', 'runs': [{'text': 'Cloudera Exception', 'b': True}]},
 {'type': 'p',
  'text': 'Known exception pattern: Do not remove unmanaged objects used to support Cloudera '
          'fast-deploying resources unless an approved replacement approach exists. Illumio Cloud '
          'Secure may not detect scale, redeploy, or IP changes quickly enough to keep Azure '
          'policy normalized in near real time. Unmanaged objects may be retained to statically '
          'represent all possible IPs for these resources so policy remains stable during '
          'scale-in, scale-out, or redeployment events.'},
 {'type': 'p',
  'text': 'Cloudera unmanaged object exceptions should be documented in the Follow Up Items tab or '
          'exception register and periodically reviewed by Network Security.',
  'runs': [{'text': 'Cloudera unmanaged object exceptions should be documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab or exception register and periodically reviewed by Network Security.'}]},
 {'type': 'heading',
  'text': 'Step 3: Retire Unused Policy Artifacts',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Removes unused or obsolete Illumio artifacts after confirming they are not needed for '
          'active policy, migration work, exceptions, or support operations.',
  'runs': [{'text': 'Removes unused or obsolete Illumio artifacts after confirming they are not '
                    'needed for active policy, migration work, exceptions, or support operations.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Review the application and tenant for unused or obsolete policy artifacts, including:'},
 {'type': 'p',
  'text': 'Unused or obsolete labels',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '15'},
 {'type': 'p',
  'text': 'Duplicate labels',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '15'},
 {'type': 'p',
  'text': 'Unused IP lists',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '15'},
 {'type': 'p',
  'text': 'Stale rulesets',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '15'},
 {'type': 'p',
  'text': 'Obsolete policy rules',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '15'},
 {'type': 'p',
  'text': 'Unneeded unmanaged objects not covered by an approved exception',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '15'},
 {'type': 'p',
  'text': 'Remove artifacts only after confirming they are not used by active policy, onboarding '
          'work, exception handling, ongoing migration activity, or operational support processes. '
          'If ownership or purpose is unclear, retain the artifact and document the question in '
          'the Follow Up Items tab.',
  'runs': [{'text': 'Remove artifacts only after confirming they are not used by active policy, '
                    'onboarding work, '},
           {'text': 'exception'},
           {'text': ' handling, ongoing migration activity, or operational support processes. If '
                    'ownership or purpose is unclear, retain the artifact and document the '
                    'question in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab.'}]},
 {'type': 'p',
  'text': 'Cleanup actions that modify or remove labels, IP lists, rulesets, rules, or unmanaged '
          'objects must include required testing and a rollback or recovery plan.'},
 {'type': 'p',
  'text': 'Confirm artifact ownership where needed.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '16'},
 {'type': 'p',
  'text': 'Validate that the artifact is not referenced by active policy, exception handling, '
          'migration work, or support operations.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '16'},
 {'type': 'p',
  'text': 'Document the cleanup action, retained-artifact rationale, or unresolved ownership '
          'question.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '16'},
 {'type': 'p',
  'text': 'Remove the artifact or retain it with an approved reason.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '16'},
 {'type': 'p',
  'text': 'Update the ICS Migration Tracking workbook and any operational support records affected '
          'by the cleanup.',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '16',
  'runs': [{'text': 'Update the '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook and any operational support records affected by the cleanup.'}]},
 {'type': 'heading',
  'text': 'Step 4: Future Operational Process Considerations',
  'style': 'Heading 2',
  'level': 2},
 {'type': 'p',
  'text': 'Updates tracking, inventory, exception, and support records so post-cleanup operations '
          'reflect the enforced Cloud Secure and Azure NSG model.',
  'runs': [{'text': 'Updates tracking, inventory, exception, and support records so post-cleanup '
                    'operations reflect the enforced Cloud Secure and Azure NSG model.',
            'i': True,
            'color': '2F5496'}]},
 {'type': 'p',
  'text': 'Update enforcement and operations records after cleanup is complete so support teams '
          'understand the current enforcement model, retained exceptions, and any remaining '
          'follow-up actions.'},
 {'type': 'p',
  'text': 'ICS Migration Tracking workbook Phase 5 status and final application/environment pair '
          'status',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '18',
  'runs': [{'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook Phase 5 status and final application/environment pair status'}]},
 {'type': 'p',
  'text': 'Application inventory',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '18'},
 {'type': 'p',
  'text': 'CMDB or application ownership notes where applicable',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '18'},
 {'type': 'p',
  'text': 'Exception register or Follow Up Items tab for retained VENs, unmanaged objects, or '
          'policy artifacts',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '18',
  'runs': [{'text': 'Exception register or '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab for retained VENs, unmanaged objects, or policy artifacts'}]},
 {'type': 'p',
  'text': 'Operational runbook or support notes',
  'style': 'List Paragraph',
  'list': True,
  'ilvl': 0,
  'num_id': '18'},
 {'type': 'p',
  'text': 'Ongoing operations should define how Network Security will approve new applications '
          'after migration, support applications continuing to move from Aurora to Azure, retire '
          'applications, and manage future tag, label, ruleset, exception, and cleanup updates.'},
 {'type': 'heading', 'text': 'Phase 5 Exit Criteria', 'style': 'Heading 2', 'level': 2},
 {'type': 'p', 'text': 'Phase 5 is complete when:'},
 {'type': 'p',
  'text': '✅ Application remains stable after Phase 4 enforcement and the agreed monitoring period '
          'is complete',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Application remains stable after Phase 4 enforcement and the agreed '
                    'monitoring period is complete'}]},
 {'type': 'p',
  'text': '✅ Azure-hosted VENs removed where Azure NSG enforcement provides the required control, '
          'or retained with documented rationale',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Azure-hosted VENs removed where Azure NSG enforcement provides the required '
                    'control, or retained with documented rationale'}]},
 {'type': 'p',
  'text': '✅ Persistent Azure unmanaged objects removed where Cloud Secure discovery and Azure NSG '
          'enforcement have replaced their policy purpose, or retained under approved exception',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Persistent Azure unmanaged objects removed where Cloud Secure discovery and '
                    'Azure NSG enforcement have replaced their policy purpose, or retained under '
                    'approved exception'}]},
 {'type': 'p',
  'text': '✅ Cloudera or other retained unmanaged object exceptions documented in the Follow Up '
          'Items tab or exception register and assigned for periodic review',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Cloudera or other retained unmanaged object exceptions documented in the '},
           {'text': 'Follow Up Items', 'b': True},
           {'text': ' tab or exception register and assigned for periodic review'}]},
 {'type': 'p',
  'text': '✅ Unused labels, IP lists, rulesets, unmanaged objects, and obsolete policy rules '
          'reviewed and cleaned up where confirmed safe, or retained with documented rationale',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' Unused labels, IP lists, rulesets, unmanaged objects, and obsolete policy '
                    'rules reviewed and cleaned up where confirmed safe, or retained with '
                    'documented rationale'}]},
 {'type': 'p',
  'text': '✅ ICS Migration Tracking workbook, application inventory, exception register, and '
          'operational support notes updated with final status and unresolved follow-up items',
  'runs': [{'text': '✅', 'font': 'Segoe UI Emoji'},
           {'text': ' '},
           {'text': 'ICS Migration Tracking', 'b': True},
           {'text': ' workbook, application inventory, exception register, and operational support '
                    'notes updated with final status and unresolved follow-up items'}]}]


def outline(max_level=3):
    """Print the heading tree."""
    for b in BLOCKS:
        if b["type"] == "heading" and b.get("level", 9) <= max_level:
            print("  " * b.get("level", 0) + b["text"])


def plain_text():
    """Whole document as flat text."""
    out = []
    for b in BLOCKS:
        if b["type"] == "table":
            for row in b["rows"]:
                out.append(" | ".join(c["text"] for c in row))
        else:
            out.append(b["text"])
    return "\n".join(out)


def find(needle):
    """Index + block for every block containing needle (case-insensitive)."""
    n = needle.lower()
    return [(i, b) for i, b in enumerate(BLOCKS)
            if n in str(b.get("text", "")).lower()
            or (b["type"] == "table" and n in str(b["rows"]).lower())]


if __name__ == "__main__":
    print(f"{META['paragraphs']} paragraphs, {META['tables']} tables, "
          f"{len(IMAGES)} images, {META['words']} words\n")
    outline()
