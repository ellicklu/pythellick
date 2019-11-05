import os
import xml.dom.minidom

target_folder = 'D:\\projects\\Capital_Projects\\'
user_group_file = "perf_groups_roles_users.xml"
project_file = "projects_200.xml"
report_file = "createPerfReports.xml"
epfm_config_file = "install_package_config.xml"

projects_number = 201
repo = "DOCREPO"
configure_area_name = "EIFQS1"
sheet_deliverables = "Internal Deliverables-allocate new numbers.xlsx"
sheet_deliverables_bol_val = "External Deliverable-Bol-Valves.xlsx"
review_matrix = "Distribution Matrix-Review-G89471.xlsx"

#DQL of creating user accounts
def dql_create_user(user_name, repo):
    create_user_dql = '''
create dm_user object set user_name='{user_name}',
set user_os_name='{user_name}',
set user_source='inline password',
set user_password='qu8l1ty',
set user_address='{user_name}@opentext.com',
set user_state=0,
set user_privileges=16,
set client_capability=4,
set user_xprivileges=0,
set acl_domain='{repo}'
'''
    return create_user_dql.format(user_name=user_name, repo=repo)

#Ant task of creating user account with check
def create_user_action(doc, user_name, repo):
    dql = doc.createElement("dql")
    dql.setAttribute("run_on_global_repository", "false")
    dql.setAttribute("run_on_local_repositories", "true")
    query = doc.createElement("query_objectcheck")
    query.appendChild(doc.createTextNode("dm_user where user_name = '{u}'".format(u=user_name)))
    execute = doc.createElement("query")
    execute.appendChild(doc.createTextNode(dql_create_user(user_name, repo)))
    dql.appendChild(query)
    dql.appendChild(execute)
    return dql

#DQL of adding user to group
def add_user_group(doc, user_name, group_name):
    dql = doc.createElement("dql")
    dql.setAttribute("run_on_global_repository", "false")
    dql.setAttribute("run_on_local_repositories", "true")
    query = doc.createElement("query_objectcheck")
    query.appendChild(
        doc.createTextNode(
            "dm_group where group_name='{g}' and any users_names='{u}'".format(u=user_name, g=group_name)))
    execute = doc.createElement("query")
    execute.appendChild(
        doc.createTextNode(
            "ALTER GROUP '{g}' ADD '{u}'".format(u=user_name, g=group_name)))
    dql.appendChild(query)
    dql.appendChild(execute)
    return dql

### USER GROUP SCRIPT
def generate_user_group_script():
    doc = xml.dom.minidom.Document()
    scripts = doc.createElement("scripts")
    doc.appendChild(scripts)

    for i in range(1, projects_number):
        # create contributor
        user_name = "perfuser{idx}".format(idx=i)
        scripts.appendChild(create_user_action(doc, user_name, repo))
        group_name = "perf{idx}_consumers".format(idx=i)
        scripts.appendChild(add_user_group(doc, user_name, group_name))
        group_name = "perf{idx}_contributors".format(idx=i)
        scripts.appendChild(add_user_group(doc, user_name, group_name))
        group_name = "perf{idx}_controllers".format(idx=i)
        scripts.appendChild(add_user_group(doc, user_name, group_name))
        # create approver
        user_name = "perfuser_a_{idx}".format(idx=i)
        scripts.appendChild(create_user_action(doc, user_name, repo))
        group_name = "perf{idx}_controllers".format(idx=i)
        scripts.appendChild(add_user_group(doc, user_name, group_name))
        group_name = "doc_ctrl"
        scripts.appendChild(add_user_group(doc, user_name, group_name))

        # create delegator
        user_name = "perfuser_f_{idx}".format(idx=i)
        scripts.appendChild(create_user_action(doc, user_name, repo))
        group_name = "perf{idx}_controllers".format(idx=i)
        scripts.appendChild(add_user_group(doc, user_name, group_name))

    user_fp = open('{folder}{file}'.format(folder=target_folder, file=user_group_file), 'w+')
    doc.writexml(user_fp, indent='\t', addindent='\t', newl='\n', encoding='utf-8')
    user_fp.close()


# PROJECT SCRIPT
def create_project_action(doc, project_name, configure_area_name):

    action = doc.createElement("action")
    action.setAttribute("name", "clone_project_configuration_action")
    action.setAttribute("selection_mode", "single")

    objectexists = doc.createElement("objectexists")
    objectexists.setAttribute("not", "true")
    objectexists.appendChild(doc.createTextNode("eif_project_config_area where object_name='{prj}'".format(prj=project_name)))

    if_node = doc.createElement("if")
    if_node.appendChild(objectexists)
    action.appendChild(if_node)

    context = doc.createElement("context")
    src_obj = doc.createElement("object")
    src_obj.appendChild(doc.createTextNode("eif_project_config_area where object_name='{cfg}'".format(cfg=configure_area_name)))
    context.appendChild(src_obj)

    tgt_obj = doc.createElement("params")
    param = doc.createElement("param")
    param.setAttribute("name", "new_name")
    param.appendChild(doc.createTextNode(project_name))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "eif_project_name")
    param.appendChild(doc.createTextNode(project_name))
    tgt_obj.appendChild(param)
    param = doc.createElement("param")
    param.setAttribute("name", "title")
    param.appendChild(doc.createTextNode(project_name+"_title"))
    tgt_obj.appendChild(param)
    param = doc.createElement("param")
    param.setAttribute("name", "eif_client")
    param.appendChild(doc.createTextNode(project_name))
    tgt_obj.appendChild(param)
    param = doc.createElement("param")
    param.setAttribute("name", "eif_business_unit")
    param.appendChild(doc.createTextNode("Production"))
    tgt_obj.appendChild(param)
    param = doc.createElement("param")
    param.setAttribute("name", "eif_location")
    param.appendChild(doc.createTextNode("North Sea"))
    tgt_obj.appendChild(param)
    param = doc.createElement("param")
    param.setAttribute("name", "eif_prj_days_response")
    param.appendChild(doc.createTextNode("15"))
    tgt_obj.appendChild(param)
    param = doc.createElement("param")
    param.setAttribute("name", "eif_ext_days_response")
    param.appendChild(doc.createTextNode("15"))
    tgt_obj.appendChild(param)
    param = doc.createElement("param")
    param.setAttribute("name", "eif_review_days")
    param.appendChild(doc.createTextNode("15"))
    tgt_obj.appendChild(param)

    context.appendChild(tgt_obj)

    action.appendChild(context)
    return action

#Creating xml script of loading projects
def generate_project_script():
    doc = xml.dom.minidom.Document()
    action_list = doc.createElement("action_list")
    doc.appendChild(action_list)

    for i in range(1, projects_number):
        # create clone project action
        project_name = "PERF{idx}".format(idx=i)
        action_list.appendChild(create_project_action(doc, project_name, configure_area_name))

    project_fp = open('{folder}{file}'.format(folder=target_folder, file=project_file), 'w+')
    doc.writexml(project_fp, indent='\t', addindent='\t', newl='\n', encoding='utf-8')
    project_fp.close()

#Create report action
def create_report_action(doc, project_name, action_name, report_name, report_display, format):
    action = doc.createElement("action")
    action.setAttribute("name", action_name)

    objectexists = doc.createElement("objectexists")
    objectexists.setAttribute("not", "true")
    objectexists.appendChild(doc.createTextNode("ecs_report where object_name = '{rpt}'".format(rpt=report_name)))

    if_node = doc.createElement("if")
    if_node.appendChild(objectexists)
    action.appendChild(if_node)

    context = doc.createElement("context")
    rpt_folder = doc.createElement("object")
    rpt_folder.appendChild(
        doc.createTextNode(
            "eifx_org_folder where object_name = '01. Templates' and FOLDER('/PROJECTS/{prj}-{prj}/08. Reports')".format(prj=project_name)))
    context.appendChild(rpt_folder)

    tgt_obj = doc.createElement("params")

    param = doc.createElement("param")
    param.setAttribute("name", "reportName")
    param.setAttribute("type", "string")
    param.setAttribute("repeating", "false")
    param.appendChild(doc.createTextNode(report_name))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "targetType")
    param.setAttribute("property", "ecs_internal_ref")
    param.setAttribute("repeating", "false")
    report_type_obj = doc.createElement("object")
    report_type_obj.appendChild(doc.createTextNode("ecs_report_type where object_name='"+report_display+"' and FOLDER('/ECSCONFIG/Application Configuration/" + project_name + "/04 Reports/01 Types')"))
    param.appendChild(report_type_obj)
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "targetTemplate")
    param.setAttribute("property", "ecs_internal_ref")
    param.setAttribute("repeating", "false")
    report_template_obj = doc.createElement("object")
    report_template_obj.appendChild(doc.createTextNode("ecs_report where object_name='"+report_display+"' and FOLDER('/ECSCONFIG/Application Configuration/EIFSHD/04 Reports/02 Templates')"))
    param.appendChild(report_template_obj)
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "reportName")
    param.setAttribute("type", "string")
    param.setAttribute("repeating", "false")
    param.appendChild(doc.createTextNode(report_name))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "activate")
    param.setAttribute("type", "boolean")
    param.setAttribute("repeating", "false")
    param.appendChild(doc.createTextNode("true"))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "targetState")
    param.setAttribute("type", "string")
    param.setAttribute("repeating", "false")
    param.appendChild(doc.createTextNode("Active"))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "format")
    param.setAttribute("type", "string")
    param.setAttribute("repeating", "false")
    param.appendChild(doc.createTextNode(format))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "executionMode")
    param.setAttribute("type", "string")
    param.setAttribute("repeating", "false")
    param.appendChild(doc.createTextNode("synchronous"))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "reportMode")
    param.setAttribute("type", "string")
    param.setAttribute("repeating", "false")
    param.appendChild(doc.createTextNode("save"))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "executionUser")
    param.setAttribute("type", "string")
    param.setAttribute("repeating", "false")
    param.appendChild(doc.createTextNode("session_user"))
    tgt_obj.appendChild(param)

    param = doc.createElement("param")
    param.setAttribute("name", "reportResultLocation")
    param.setAttribute("property", "r_object_id")
    param.setAttribute("repeating", "false")
    folder_object = doc.createElement("object")
    folder_object.appendChild(doc.createTextNode("eifx_org_folder where object_name='02. Results' and FOLDER('/PROJECTS/PERF1-PERF1/08. Reports')"))
    param.appendChild(folder_object)
    tgt_obj.appendChild(param)
    context.appendChild(tgt_obj)
    action.appendChild(context)
    return action


#Creating xml script of loading report templates
def generate_reports_script():
    doc = xml.dom.minidom.Document()
    action_list = doc.createElement("action_list")
    doc.appendChild(action_list)

    for i in range(1, projects_number):
        # create report to project action
        project_name = "PERF{idx}".format(idx=i)

        action_name = "Create Master Documents Report"
        report_name = "Master-Report-PERF{idx}".format(idx=i)
        report_display = "Master Documents Report"
        action_list.appendChild(create_report_action(doc, project_name, action_name, report_name, report_display, "pdf"))

        action_name = "Create Review Task Report"
        report_name = "Review-Report-PERF{idx}".format(idx=i)
        report_display = "Review Task Report"
        action_list.appendChild(create_report_action(doc, project_name, action_name, report_name, report_display, "docx"))

    project_fp = open('{folder}{file}'.format(folder=target_folder, file=report_file), 'w+')
    doc.writexml(project_fp, indent='\t', addindent='\t', newl='\n', encoding='utf-8')
    project_fp.close()

#Ant task of loading a sheet
def create_project_load_sheet(doc, project_name, sheet_name):
    load_sheet = doc.createElement("load_sheet")
    load_sheet.setAttribute("loadsheetPath", "${deploy.package}/RepositoryConfig/Loadsheets/" + sheet_name)
    load_sheet.setAttribute("contentLocation", "${deploy.package}/RepositoryConfig/content")
    load_sheet.setAttribute("projectCode", project_name)
    load_sheet.setAttribute("doctypeName", "Document Loading")
    load_sheet.setAttribute("doctypeTemplate", "Loading Internal Deliverable Doc Template")
    return load_sheet

#Ant task of import matrix
def import_project_matrix(doc, project_name, matrix_name):
    import_matrix = doc.createElement("import_matrix")
    import_matrix.setAttribute("distributionMatrixFile", "${deploy.package}/RepositoryConfig/distribution/" + matrix_name)
    import_matrix.setAttribute("doctypeName", "Transmittal Matrix")
    import_matrix.setAttribute("projectCode", project_name)
    import_matrix.setAttribute("doctypeTemplate", "Review Transmittal Matrix")
    import_matrix.setAttribute("resultProperty", "new.matrix.id")
    import_matrix.setAttribute("publish", "true")
    return import_matrix

#generate xml of sample data config
def generate_install_package_config():
    doc = xml.dom.minidom.Document()
    epfm_config = doc.createElement("epfm_release_package_config")

    epfm_config.appendChild(doc.createElement("appserver_config"))

    repo_config = doc.createElement("repository_config")

    run_action = doc.createElement("run_actions")
    run_action.setAttribute("actionListFile", "${deploy.package}/RepositoryConfig/projects/"+project_file)
    run_action.setAttribute("componentid", "create_projects")
    run_action.setAttribute("componentversion", "1")
    repo_config.appendChild(run_action)

    import_global_group = doc.createElement("import")
    import_global_group.setAttribute("file", "${basedir}/${deploy.package}/initialize_groups_roles.xml")
    repo_config.appendChild(import_global_group)

    import_user_group = doc.createElement("import")
    import_user_group.setAttribute("file", "${basedir}/${deploy.package}/"+user_group_file)
    repo_config.appendChild(import_user_group)

    create_reports = doc.createElement("create_reports")
    create_reports.setAttribute("actionListFile", "${deploy.package}/RepositoryConfig/projects/"+report_file)
    create_reports.setAttribute("componentid", "create_perf_reports")
    create_reports.setAttribute("componentversion", "1")
    repo_config.appendChild(create_reports)

    for i in range(1, projects_number):
        # create clone project load sheets
        project_name = "PERF{idx}".format(idx=i)
        #Load delivery doc sheet to project
        sheet_name = sheet_deliverables
        repo_config.appendChild(create_project_load_sheet(doc, project_name, sheet_name))
        #Load bol_val delivery doc sheet to project
        #sheet_name = sheet_deliverables_bol_val
        #repo_config.appendChild(create_project_load_sheet(doc, project_name, sheet_name))
        #Load review matrix to project
        repo_config.appendChild(import_project_matrix(doc, project_name, review_matrix))

    epfm_config.appendChild(repo_config)
    doc.appendChild(epfm_config)

    epfm_cfg_fp = open('{folder}{file}'.format(folder=target_folder, file=epfm_config_file), 'w+')
    doc.writexml(epfm_cfg_fp, indent='\t', addindent='\t', newl='\n', encoding='utf-8')
    epfm_cfg_fp.close()

generate_project_script()
generate_user_group_script()
generate_reports_script()
generate_install_package_config()