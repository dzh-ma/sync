import json
from report_generator import EnergyReportGenerator  # or the relevant function
# If you're testing the top-level "generate_energy_report" function, import that instead.

def main():
    # 1. Load sample energy data from JSON
    with open("example_data.json", "r") as f:
        energy_data = json.load(f)

    # 2. Create the generator object
    report_gen = EnergyReportGenerator(energy_data)

    # 3. Generate the PDF
    pdf_path = report_gen.create_pdf_report()
    # Or if you’re using the top-level function in report_generator:
    # from report_generator import generate_energy_report
    # pdf_path = generate_energy_report(energy_data, format='pdf')

    print(f"PDF successfully generated: {pdf_path}")

if __name__ == "__main__":
    main()
