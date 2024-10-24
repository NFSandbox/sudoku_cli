import subprocess
from loguru import logger

INPUT_FILE = "report.md"
OUTPUT_FILE = "report.docx"
STYLE_REF = "ref.docx"


def main():
    logger.info("Generating report documentation...")

    # construct command
    command = f"pandoc {INPUT_FILE} -o {OUTPUT_FILE} --reference-doc {STYLE_REF}"

    logger.info(
        f"""
        Command to execute:
        {command}
        """
    )
    try:
        subprocess.run(
            command,
            shell=True,
        )
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return

    logger.success("Report generated successfully!")
    return


if __name__ == "__main__":
    main()
