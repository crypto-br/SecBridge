import os
import subprocess

def run_prowler(profile_for_prowler):
    print("Running Prowler...")
    try:
        prowler_command = ["prowler", "aws", "--severity", "critical", "--profile", f"{profile_for_prowler}", "-M", "json-asff"]
        try:
            process = subprocess.run(prowler_command, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            return (f"Error executing Prowler command: {e}")
        except Exception as e:
            return (f"Unexpected error while executing Prowler: {e}")

        try:
            output_text = process.stdout.strip()
        except AttributeError as e:
            return (f"Error processing Prowler output: {e}")
        except Exception as e:
            return (f"Unexpected error processing Prowler output: {e}")

        if output_text:
            try:
                for line in output_text.splitlines():
                    if "ASFF" in line and line.endswith(".json"):
                        json_path = line.split()[-1]
                        try:
                            if os.path.exists(json_path):
                                print(f"JSON-ASFF file generated at: {json_path}")
                                return json_path
                        except OSError as e:
                            return (f"Error checking the existence of the JSON file: {e}")
                        except Exception as e:
                            return (f"Unexpected error checking the JSON file: {e}")
            except Exception as e:
                return (f"Error processing Prowler output lines: {e}")
        else:
            return "No output captured from Prowler."

    except Exception as e:
        return (f"Error running Prowler: {e}")
