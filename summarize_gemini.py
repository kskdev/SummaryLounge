import base64
import os

import toml
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import Part
from vertexai.generative_models import Tool
from vertexai.generative_models import FinishReason
import vertexai.preview.generative_models as generative_models

class PDFSummarizer:
    def __init__(self):
        self.responses = ""

        with open("./config.toml","r",encoding="UTF-8") as f: self.conf=toml.load(f)
        self.system_prompt = self.conf["SystemPrompt"]["OchiaiFormat"]
        self.project_id  = self.conf["GCPGemini"]["ProjectID"]
        self.region_name = self.conf["GCPGemini"]["RegionName"]
        self.model_name  = self.conf["GCPGemini"]["ModelName"]
        self.credential  = self.conf["GCPIAM"]["CredentialJson"]

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credential

        vertexai.init(project=self.project_id, location=self.region_name)

        self.generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }

        self.safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH:
                generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:
                generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:
                generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT:
                generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # ハルシネーションの抑制(gemini-1.5-pro-001は 2024/05/27段階では非対応)
        self.tools = [
            Tool.from_google_search_retrieval(
            google_search_retrieval=generative_models.grounding.GoogleSearchRetrieval(disable_attribution=True)
            ),
        ]

        self.model = GenerativeModel(
            model_name         = self.model_name,
            # tools              = self.tools,
            system_instruction = [self.system_prompt],
        )

    def encode_base64(self, filepath):
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("UTF-8")


    def save(self, outpath):
        with open(outpath, "w", encoding="UTF-8") as f:
            return f.write(self.responses.text)


    def run(self, pdfpath, user_prompt=None):
        base64_pdf = Part.from_data(
            mime_type="application/pdf",
            data     =self.encode_base64(pdfpath),
        )
        if user_prompt is None: self.user_prompt = "まとめてください．"
        else                  : self.user_prompt = user_prompt
        self.responses = self.model.generate_content(
            contents          = [base64_pdf,self.user_prompt],
            generation_config = self.generation_config,
            safety_settings   = self.safety_settings,
            stream            = False,
        )
        return self.responses.text


if __name__ == "__main__":

    input_path = "../2002.08688v2.pdf"
    output_dir = "./Result"

    input_name  = os.path.basename(input_path).replace(".pdf","")
    output_name = "summary_{}.md".format(input_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir,output_name)

    summarizer = PDFSummarizer()
    res = summarizer.run(input_path)
    summarizer.save(output_path)
    print(res)
