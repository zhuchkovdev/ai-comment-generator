import io
import os
import torch
import tokenize
import sentencepiece as sp
from torch.nn.utils.rnn import pad_sequence
from download import download_checkpoint, download_vocab
from transformers.models.bart import BartForConditionalGeneration, BartConfig


def _remove_comments_and_docstrings(source):
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
        ltext = tok[4]
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


def generate_comment(code, max_length):
    with torch.no_grad():
        code = _remove_comments_and_docstrings(code)
        inp = spm.tokenize(code)
        inp = torch.tensor(inp).view(1,-1)
        generated = model.generate(input_ids=inp[:MAX_CODE_LEN].to(model.device), 
                                decoder_start_token_id=spm.bos_id(), 
                                num_beams=10,
                                max_length=max_length, no_repeat_ngram_size=4)
        generated = generated[0].cpu().tolist()
        return spm.decode(generated)


# Constants
CHECKPOINT_PATH = 'model_result'
VOCAB_PATH = 'shared_bpe.model'

D_MODEL = 512
NUM_LAYERS = 6
NUM_DECODER_LAYERS = 6
D_FF = 1024
NUM_HEADS = 8
DROPOUT_RATE = 0.1
MAX_CODE_LEN = 340

if(not os.path.exists(VOCAB_PATH)):
    print("Downloading vocab")
    download_vocab(VOCAB_PATH)

if(not os.path.exists(CHECKPOINT_PATH)):
    print("Downloading model checkpoint")
    download_checkpoint(CHECKPOINT_PATH)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

spm = sp.SentencePieceProcessor()
spm.Load(VOCAB_PATH)

model_config = BartConfig(
    vocab_size=spm.vocab_size(),
    d_model=D_MODEL,
    num_layers=NUM_LAYERS,
    num_decoder_layers=NUM_DECODER_LAYERS,
    d_ff=D_FF,
    num_heads=NUM_HEADS, 
    dropout_rate=DROPOUT_RATE,
    decoder_start_token_id=spm.bos_id(),
    tie_word_embeddings = False
)

model = BartForConditionalGeneration(model_config)
model_data = torch.load(CHECKPOINT_PATH, map_location=device)
model.load_state_dict(model_data['model_state'])
