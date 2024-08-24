import os
import subprocess

def run_prowler(profile_for_prowler):
    print("Executando o Prowler...")
    try:
        prowler_command = ["prowler", "aws", "--severity", "critical", "--profile", f"{profile_for_prowler}", "-M", "json-asff"]
        try:
            process = subprocess.run(prowler_command, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            return (f"Erro na execução do comando Prowler: {e}")
        except Exception as e:
            return (f"Erro inesperado ao executar o Prowler: {e}")

        try:
            output_text = process.stdout.strip()
        except AttributeError as e:
            return (f"Erro ao processar a saída do Prowler: {e}")
        except Exception as e:
            return (f"Erro inesperado ao processar a saída do Prowler: {e}")

        if output_text:
            try:
                for line in output_text.splitlines():
                    if "ASFF" in line and line.endswith(".json"):
                        json_path = line.split()[-1]
                        try:
                            if os.path.exists(json_path):
                                print(f"Arquivo JSON-ASFF gerado em: {json_path}")
                                return json_path
                        except OSError as e:
                            return (f"Erro ao verificar a existência do arquivo JSON: {e}")
                        except Exception as e:
                            return (f"Erro inesperado ao verificar o arquivo JSON: {e}")
            except Exception as e:
                return (f"Erro ao processar as linhas da saída do Prowler: {e}")
        else:
            return "Nenhuma saída do Prowler foi capturada."

    except Exception as e:
        return (f"Erro ao rodar o Prowler: {e}")
