# SecBridge

**Version:** 1.0

**Author:** Luiz Machado (@cryptobr)

## Description

SecBridge is an integration tool that connects [Prowler](https://github.com/prowler-cloud/prowler) and the [Pacu Framework](https://github.com/RhinoSecurityLabs/pacu), allowing you to automate the security risk assessment in your AWS accounts. The tool checks risks using Prowler and evaluates the exploitability of these risks using Pacu, generating detailed reports.

## Features

- **Dependency Check:** Confirms the existence of essential dependencies like AWS CLI, Python3, Prowler, and Pacu.
- **Prowler Execution:** Runs Prowler to perform a security assessment on the specified AWS account.
- **Pacu Framework Execution:** Allows the execution of the Pacu Framework for exploitation based on specific categories.
- **Report Generation:** Generates detailed reports after running Pacu.
- **Dashboards:** Launches dashboards for visualizing Prowler and Pacu results.
- **AWS Profile Configuration:** Configures AWS-CLI profiles directly through the tool.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/secbridge.git
   cd secbridge
   ```

2. **Install Dependencies:**
   Ensure that AWS CLI, Python3, Prowler, and Pacu are installed. You can check the dependencies by running:
   ```bash
   python secbridge.py --deps
   ```

## Usage

You can run the tool with different options depending on your needs:

- **Check Dependencies:**
  ```bash
  python secbridge.py --deps
  ```

- **Run Prowler:**
  ```bash
  python secbridge.py --prowler
  ```

- **Start Prowler Dashboard (the tool already includes a dashboard, here it just activates it):**
  ```bash
  python secbridge.py --prowler-dash
  ```

- **Run Pacu (Enumeration):**
  ```bash
  python secbridge.py --pacu-enum
  ```

- **Run Pacu (All Categories):**
  ```bash
  python secbridge.py --pacu
  ```

- **Start Pacu with Prowler:**
  ```bash
  python secbridge.py --full
  ```

- **Delete Pacu Sessions:**
  ```bash
  python secbridge.py --prune-pacu
  ```

- **Start Pacu Dashboard:**
  ```bash
  python secbridge.py --pacu-dash
  ```

  ![image](https://github.com/user-attachments/assets/3d40d8f2-1fcb-47a9-ba1e-a69922a1be99)

  ![image](https://github.com/user-attachments/assets/476551c1-20a3-4336-9846-67473d787740)

- **Set Up a New AWS-CLI Profile:**
  ```bash
  python secbridge.py --np
  ```

- **Help:**
  ```bash
  python secbridge.py --help
  ```

## Contribution

Contributions are welcome! If you have suggestions for improvements or found a bug, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For more information or questions, contact [Luiz Machado](https://www.linkedin.com/in/luizmachadoaws/).

This `README.md` provides a comprehensive overview of the SecBridge tool, including how to install it, use it, and contribute.
