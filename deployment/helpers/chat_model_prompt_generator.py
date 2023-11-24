import re
import torch

class LanguageLevelAssistant:
    """
    A class to assist in language level translation tasks, using a specified language model.

    Attributes:
        model (Model): The machine learning model for generating responses.
        tokenizer (Tokenizer): The tokenizer for processing text inputs.
        costings (dict): A dictionary to track the cost associated with each operation.
    """

    def __init__(self, model_name, model_dir):
        """
        Initialize the LanguageLevelAssistant class with a model name.

        Args:
            model_name (str): The name of the model to load.
        """
        self.model_dir = model_dir
        self.model_name = model_name
        self.model, self.tokenizer = self.load_model(model_name, model_dir)
        self.model.eval()  # Set the model to evaluation mode
        self.costings = {}

    @staticmethod
    def load_model(model_name, model_dir):
        """
        Load the model and tokenizer for the given model name.

        Args:
            model_name (str): The name of the model to load.

        Returns:
            tuple: A tuple containing the loaded model and tokenizer.
        """
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_dir,
            low_cpu_mem_usage=True,
            device_map = "auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        return model, tokenizer

    def generate_prompt(self, instruction, context):
        """
        Create a formatted prompt using the given instruction and context.

        Args:
            instruction (str): The instruction for the prompt.
            context (str): Additional context to be included in the prompt.

        Returns:
            str: The formatted prompt.
        """
        SYSTEM_PROMPT = f"""<s>[INST] <<SYS>> \n
        You are a helpful, respectful and honest assistant. Always simplify the text to the asked target language level from the source language level, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.<</SYS>>\n"""
        INSTRUCTION = f"{instruction}:\n {context} [/INST] \n\n"
        formatted_prompt = SYSTEM_PROMPT + INSTRUCTION
        return formatted_prompt

    def make_inference(self, instruction, context=None):
        """
        Generate a response based on the given instruction and context.

        Args:
            instruction (str): The instruction to process.
            context (str, optional): The context to be included in the prompt. Defaults to None.

        Returns:
            str: The generated response.
        """
        prompt = self.generate_prompt(instruction, context)
        inputs = self.tokenizer(text=prompt, return_tensors="pt", return_token_type_ids=False).to("cuda")

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                do_sample=True,
                max_new_tokens=250,
                use_cache=False,
            )
        decoded_response = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
        return decoded_response


    @staticmethod
    def map_cefr_to_text(language_level):
        """
        Map a CEFR language level to its textual representation.

        Args:
            language_level (int): The CEFR language level.

        Returns:
            str: Textual representation of the CEFR level.
        """
        level_mapping = {"3": "advanced", "2": "intermediate", "1": "beginner"}
        return level_mapping.get(str(language_level), "Unrecognized language level")

    def generate_instruction_column(self, source_cefr, target_cefr):
        """
        Generate a column instruction for language simplification.

        Args:
            source_cefr (int): The source language CEFR level.
            target_cefr (int): The target language CEFR level.

        Returns:
            str: Instruction for simplifying the language level.
        """
        source_level_text = self.map_cefr_to_text(source_cefr)
        target_level_text = self.map_cefr_to_text(target_cefr)
        return f"Simplify from {source_level_text} to {target_level_text} language level"

    @staticmethod
    def extract_levels(text):
        """
        Extract CEFR levels from the given text.

        Args:
            text (str): The text containing CEFR levels.

        Returns:
            tuple: A tuple containing the source and target CEFR levels, or None if not found.
        """
        pattern = re.compile(r'CEFR Level (\d)')
        levels = pattern.findall(text)
        if len(levels) == 2:
            return tuple(levels)
        else:
            print('Could not extract both levels from the text.')
            return None, None