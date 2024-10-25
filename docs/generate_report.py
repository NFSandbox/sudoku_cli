import subprocess
from loguru import logger

INPUT_FILE = "report.md"
OUTPUT_FILE_NAME = "report"
OUTPUT_SUBFIXES: list[str] = ["docx"]
STYLE_REF = "ref.docx"


def main() -> None:
    logger.info("Generating report documentation...")

    # construct command list
    command_list: list[str] = []
    for s in OUTPUT_SUBFIXES:
        logger.info(f"Generating {OUTPUT_FILE_NAME}.{s} file...")

        command = (
            f"pandoc {INPUT_FILE} -o {OUTPUT_FILE_NAME}.{s} --reference-doc {STYLE_REF}"
        )
        if s == "pdf":
            command += " --pdf-engine=xelatex"
        command_list.append(command)

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
