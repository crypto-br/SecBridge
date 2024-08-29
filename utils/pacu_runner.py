import os
import subprocess
import json

def run_pacu(profile_for_pacu, session_name, category):
    print("Running PACU Framework based on the finding data.")
    
    os.environ['AWS_PROFILE'] = profile_for_pacu

    category_enum = [
        "acm__enum",
        "apigateway__enum",
        "aws__enum_account",
        "aws__enum_spend",
        "cloudformation__download_data",
        "codebuild__enum",
        "cognito__enum",
        "dynamodb__enum",
        "ebs__enum_volumes_snapshots",
        "ec2__check_termination_protection",
        "ec2__download_userdata",
        "ec2__enum",
        "ecr__enum",
        "ecs__enum",
        "ecs__enum_task_def",
        "eks__enum",
        "enum__secrets",
        "glue__enum",
        "guardduty__list_accounts",
        "guardduty__list_findings",
        "iam__bruteforce_permissions",
        "iam__detect_honeytokens",
        "iam__enum_action_query",
        "iam__enum_permissions",
        "iam__enum_users_roles_policies_groups",
        "iam__get_credential_report",
        "inspector__get_reports",
        "lambda__enum",
        "lightsail__enum",
        "organizations__enum",
        "rds__enum",
        "rds__enum_snapshots",
        "route53__enum",
        "systemsmanager__download_parameters",
        "transfer_family__enum"
    ]

    category_exploit = [
        "api_gateway__create_api_keys",
        "cognito__attack",
        "ebs__explore_snapshots",
        "ec2__startup_shell_script",
        "ecs__backdoor_task_def",
        "lightsail__download_ssh_keys",
        "lightsail__generate_ssh_keys",
        "lightsail__generate_temp_access",
        "systemsmanager__rce_ec2"
    ]

    category_escalate = [
        "cfn__resource_injection",
        "iam__privesc_scan"
    ]

    category_recon_unauth = [
        "ebs__enum_snapshots_unauth",
        "iam__enum_roles",
        "iam__enum_users"
    ]

    category_exfil = [
        "ebs__download_snapshots",
        "rds__explore_snapshots",
        "s3__download_bucket"
    ]

    category_lateral_move = [
        "cloudtrail__csv_injection",
        "organizations__assume_role",
        "vpc__enum_lateral_movement"
    ]

    category_evade = [
        "cloudtrail__download_event_history",
        "cloudwatch__download_logs",
        "detection__disruption",
        "detection__enum_services",
        "elb__enum_logging",
        "guardduty__whitelist_ip",
        "waf__enum"
    ]

    category_persist = [
        "ec2__backdoor_ec2_sec_groups",
        "iam__backdoor_assume_role",
        "iam__backdoor_users_keys",
        "iam__backdoor_users_password",
        "lambda__backdoor_new_roles",
        "lambda__backdoor_new_sec_groups",
        "lambda__backdoor_new_users"
    ]


    # List to store results
    results = []

    # Check if the session already exists and is active, or create a new session
    try:
        activate_session_command = ['pacu', '--session', session_name]
        subprocess.run(activate_session_command, check=True)
        print("HERE")
    except subprocess.CalledProcessError:
        create_session_command = ['pacu', '--new-session', session_name]
        subprocess.run(create_session_command, check=True)   
    if category == "category_enum":
        for module_name in category_enum:
            if module_name in ["aws__enum_account", 
                            "aws__enum_spend",
                            "ec2__check_termination_protection", 
                            "guardduty__list_findings", 
                            "iam__bruteforce_permissions",
                            "iam__detect_honeytokens",
                            "iam__get_credential_report",
                            "inspector__get_reports",
                            "route53__enum",
                            "organizations__enum",
                            "ecs__enum_task_def",
                            "ec2__download_userdata",
                            "iam__enum_permissions",
                            "lightsail__enum"
                            ]:
                pacu_command = ['pacu', '--session', session_name, '--exec', '--module-name', module_name, '--import-keys', profile_for_pacu]
                print(module_name)
            elif module_name == "iam__enum_action_query":
                print("This module requires a query case")
            elif module_name == "systemsmanager__download_parameters":
                downloads_dir = os.path.expanduser("~/.local/share/pacu/data/downloads/ssm_parameters/")
                os.makedirs(downloads_dir, exist_ok=True)
                ssm_region = "us-east-2"
                with open(os.path.join(downloads_dir, '{}.txt'.format(ssm_region)), 'w+') as f:
                    pacu_command = ['pacu', '--session', session_name, '--exec', '--module-name', module_name, '--module-args', "--regions us-east-2", '--import-keys', profile_for_pacu]
            else:
                pacu_command = ['pacu', '--session', session_name, '--exec', '--module-name', module_name, '--module-args', "--regions us-east-2", '--import-keys', profile_for_pacu]
                print(pacu_command)
            # Execute the PACU command and if necessary rerun an enumeration, we input "y" to proceed.
            process = subprocess.Popen(pacu_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input="y\n")  # Responds "Y" to any confirmation prompts
            if "AccessDeniedException" in stderr:
                stderr = "Module cannot be executed due to lack of permission"
            # Store the result in a dictionary
            result = {
                "module": module_name,
                "stdout": stdout,
                "stderr": stderr
            }
            results.append(result)
            print(stdout)
    else:
        print(category)
        for module_name in category:
            pacu_command = ['pacu', '--session', session_name, '--exec', '--module-name', module_name, '--import-keys', profile_for_pacu]
            process = subprocess.Popen(pacu_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input="y\n")  # Responds "Y" to any confirmation prompts
            # Store the result in a dictionary
            result = {
                "module": module_name,
                "stdout": stdout,
                "stderr": stderr
            }
            results.append(result)  
    # Save the results in a JSON file
    output_file = f"reports/data/report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"Results saved in {output_file}")
