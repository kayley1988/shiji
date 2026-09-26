"""
NLP 模块 - 诗词标注工具集
"""
from .poetry_tagger import PoetryTagger, PoemLine, get_tagger
try:
    from .bert_tagger import BertPoetryTagger, get_bert_tagger
except (ImportError, OSError):
    # 服务器未安装 torch/transformers，跳过 BERT 标注器
    BertPoetryTagger = None
    get_bert_tagger = None
from .question_generator import QuestionGenerator, Question, QuizResult, FEIHUA_KEYWORDS
from .char_convert import to_simplified, normalize_poetry_text

__all__ = [
    'PoetryTagger',
    'PoemLine', 
    'get_tagger',
    'BertPoetryTagger',
    'get_bert_tagger',
    'QuestionGenerator',
    'Question',
    'QuizResult',
    'FEIHUA_KEYWORDS',
    'to_simplified',
    'normalize_poetry_text',
]
