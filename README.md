# SecBridge

**Version:** 1.2

**Author:** Luiz Machado (@cryptobr)

## Description

SecBridge is an integration tool that connects [Prowler](https://github.com/prowler-cloud/prowler) and the [Pacu Framework](https://github.com/RhinoSecurityLabs/pacu), allowing you to automate the security risk assessment in your AWS accounts. The tool checks risks using Prowler and evaluates the exploitability of these risks using Pacu, generating detailed reports.

## Features

- **Dependency Check:** Confirms the existence of essential dependencies like AWS CLI, Python3, Prowler, and Pacu.
- **Prowler Execution:** Runs Prowler to perform a security assessment on the specified AWS account.
- **Pacu Framework Execution:** Allows the execution of the Pacu Framework for exploitation based on specific categories.
- **Report Generation:** Generates detailed reports after running Pacu, including HTML and JSON formats.
- **Dashboards:** Launches dashboards for visualizing Prowler and Pacu results.
- **AWS Profile Configuration:** Configures AWS-CLI profiles directly through the tool with credential validation.
- **Structured Logging:** Provides comprehensive logging with different verbosity levels and colored formatting.
- **Unit Testing:** Includes automated tests to ensure code quality.

## Installation

### Standard Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/secbridge.git
   cd secbridge
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check System Dependencies:**
   Ensure that AWS CLI, Python3, Prowler, and Pacu are installed. You can check and install the dependencies by running:
   ```bash
   python secbridge.py deps
   ```

### Docker Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/secbridge.git
   cd secbridge
   ```

2. **Build and Run with Docker:**
   ```bash
   docker build -t secbridge .
   docker run -it --rm -v ~/.aws:/root/.aws:ro -v $(pwd)/reports:/app/reports -v $(pwd)/logs:/app/logs secbridge
   ```

3. **Or use Docker Compose:**
   ```bash
   docker-compose up --build
   ```

   This will mount your AWS credentials and the reports/logs directories.

## Usage

You can run the tool with different commands:

- **Check Dependencies:**
  ```bash
  python secbridge.py deps
  ```

- **Run Prowler:**
  ```bash
  python secbridge.py prowler
  ```

- **Start Prowler Dashboard:**
  ```bash
  python secbridge.py prowler-dash
  ```

- **Run Pacu (Enumeration):**
  ```bash
  python secbridge.py pacu-enum
  ```

- **Run Pacu (With Specific Category):**
  ```bash
  python secbridge.py pacu
  ```

- **Start Pacu with Prowler (Full Assessment):**
  ```bash
  python secbridge.py full
  ```

- **Delete Pacu Sessions:**
  ```bash
  python secbridge.py prune-pacu
  ```

- **Start Pacu Dashboard:**
  ```bash
  python secbridge.py pacu-dash
  ```
  
  You can specify a custom port:
  ```bash
  python secbridge.py pacu-dash --port 8080
  ```

  ![image](https://github.com/user-attachments/assets/3d40d8f2-1fcb-47a9-ba1e-a69922a1be99)

  ![image](https://github.com/user-attachments/assets/476551c1-20a3-4336-9846-67473d787740)

- **Set Up a New AWS-CLI Profile:**
  ```bash
  python secbridge.py np
  ```

- **Help:**
  ```bash
  python secbridge.py --help
  ```

## Testing

Run the unit tests to ensure everything is working correctly:

```bash
pytest tests/
```

## Project Structure

```
secbridge/
├── config/
│   └── pacu_modules.json     # Configuration for Pacu modules
├── logs/                     # Log files directory
├── reports/                  # Generated reports
│   ├── data/                 # JSON data files
│   └── prowler/              # Prowler reports
├── tests/                    # Unit tests
├── utils/                    # Utility modules
│   ├── aws_config.py         # AWS profile configuration
│   ├── dependencies.py       # Dependency checking
│   ├── pacu_report.py        # Report generation for Pacu
│   ├── pacu_runner.py        # Pacu execution
│   └── prowler_runner.py     # Prowler execution
├── requirements.txt          # Python dependencies
├── CHANGELOG.md              # Change history
├── secbridge.py              # Main application
└── README.md                 # Documentation
```

## Contribution

Contributions are welcome! If you have suggestions for improvements or found a bug, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For more information or questions, contact [Luiz Machado](https://www.linkedin.com/in/luizmachadoaws/).
