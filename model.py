import io
import os
import re
import torch
import tokenize
from download import download_file_from_google_drive
from transformers import BartTokenizerFast
from transformers.models.bart import BartForConditionalGeneration

# Constants
CHECKPOINT_PATH = 'bart_based'
CHECKPOINT_REMOTE_ID = "1P6Evc4LP5RzULq63kYHdsWNb4utO2Avj"
MAX_CODE_LEN = 340

class DocstringGenerator:
    def __init__(self):
        if(not os.path.exists(CHECKPOINT_PATH)):
            print("Downloading model checkpoint")
            download_file_from_google_drive(CHECKPOINT_REMOTE_ID, CHECKPOINT_PATH)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model_data = torch.load(CHECKPOINT_PATH, map_location=device)

        self.tokenizer = BartTokenizerFast.from_pretrained('facebook/bart-base')
        self.model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")
        self.model.load_state_dict(model_data['model_state'])

    def _remove_comments_and_docstrings_(self, source):
        io_obj = io.StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += (" " * (start_col - last_col))
            if token_type == tokenize.COMMENT:
                pass
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
                    if prev_toktype != tokenize.NEWLINE:
                        if start_col > 0:
                            out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        out = '\n'.join(l for l in out.splitlines() if l.strip())
        return out

    def generate(self, code, max_length):
        with torch.no_grad():
            code = self._remove_comments_and_docstrings_(code)
            code = re.sub("\s+", " ", code)
            inp = self.tokenizer(code)['input_ids']
            inp = torch.tensor(inp).view(1,-1)[:,:MAX_CODE_LEN].clone()
            generated = self.model.generate(input_ids=inp.to(self.model.device), 
                                    decoder_start_token_id=self.tokenizer.bos_token_id, 
                                    num_beams=10,
                                    max_length=max_length, no_repeat_ngram_size=4)
            generated = generated[0].cpu().tolist()
            generated.remove(self.tokenizer.bos_token_id)
            generated.remove(self.tokenizer.eos_token_id)
            return self.tokenizer.decode(generated)