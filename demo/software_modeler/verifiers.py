import os
import subprocess

from loguru import logger
from sherpa_ai.memory.belief import Belief
from sherpa_ai.output_parsers import BaseOutputProcessor
from sherpa_ai.output_parsers.validation_result import ValidationResult


class OutputModel(BaseOutputProcessor):
    """
    Validates the generated model and saves it to a file

    Attributes:
        filename: The name of the file in which to save the model
    """

    def __init__(self, filename: str):
        self.filename = filename

    def process_output(self, text: str, belief: Belief) -> ValidationResult:
        """
        Extracts an Umple model from `text` and saves the model to a file

        Args:
            text: A string of text containing an Umple model (https://cruise.umple.org/umple/)
            belief: The belief of the agent that generated the text

        Returns:
            ValidationResult: The result of the validation
        """
        lines = text.split("\n")
        line_num = 0
        logger.debug(text)
        for line in lines:
            if line.startswith("namespace") or line.startswith("class"):
                break
            line_num += 1

        end = len(lines) - 1
        while end > 0:
            if lines[end] == "```":
                break
            end -= 1
        if end == 0:
            end = len(lines)
        if line_num > len(lines):
            return ValidationResult(
                is_valid=False,
                result=text,
                feedback="No namespace found. The model must have a namespace.",
            )

        model_text = "\n".join(lines[line_num:end])

        with open(self.filename, "w") as f:
            f.write(model_text)

        return ValidationResult(is_valid=True, result=model_text)

    def get_failure_message(self) -> str:
        return "Unable to save the model. Please try again."


class UmpleGeneration(BaseOutputProcessor):
    """
    Uses Umple to validate the model and generate a class diagram

    Attributes:
        umple_path: local filesystem path to the umple jar file
        fail_count: The number of times process_output calls fail
        last_error: The last error message received from Umple
    """

    def __init__(self, umple_path="umple.jar"):
        self.umple_path = umple_path
        self.fail_count = 0
        self.last_error = ""

    def process_output(self, text: str, belief: Belief) -> ValidationResult:
        """
        Validate the model and generate a class diagram

        Args:
            text: The generated model in Umple format
            belief: The belief of the agent that generated `text`

        Returns:
            ValidationResult: The result of the validation. 
            `is_valid` is true if model text passes Umple validation and can be used
            to generate a class diagram, false otherwise.
            `result` contains the generated model diagram.
        """
        if self.fail_count >= 3:
            input(
                f"Unable to fix the model. Please help me to fix  the intermediate representation. Last error received: \n {self.last_error} \n Press Enter to continue..."
            )

        result = subprocess.run(
            ["java", "-jar", self.umple_path, "-g", "java", "model.ump"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stderr_str = result.stderr
        exit_code = result.returncode

        if exit_code != 0:
            self.last_error = stderr_str
            self.fail_count += 1
            return ValidationResult(
                is_valid=False,
                result=text,
                feedback=f"The last model is invalid: {stderr_str}.",
            )

        # generate Class Diagram
        subprocess.check_output(
            ["java", "-jar", self.umple_path, "-g", "GvClassDiagram", "model.ump"],
        )

        subprocess.check_output(
            ["dot", "-Tpng", "modelcd.gv", "-o", "diagram.png"],
        )

        return ValidationResult(is_valid=True, result=text)

    def get_failure_message(self) -> str:
        return "Unable to save the model. Please try again."
