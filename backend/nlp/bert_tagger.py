"""
BERT 增强版诗词标注器
使用预训练中文 BERT 模型进行更精准的语义分析
"""
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    TRANSFORMERS_AVAILABLE = True
except (ImportError, OSError):
    TRANSFORMERS_AVAILABLE = False
    torch = None

from typing import List, Dict, Optional

from .poetry_tagger import PoetryTagger, PoemLine, get_tagger


class BertPoetryTagger:
    """基于 BERT 的诗词标注器"""

    def __init__(self, model_path: str = None):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers/torch 不可用，BERT 标注器无法初始化")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 默认使用本地模型路径（E盘）
        if model_path is None:
            model_path = "E:/AI/Models/bert-base-chinese-v2"
        
        print(f"使用设备: {self.device}")
        print(f"加载 BERT 模型: {model_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # 基础标注器
        self.dict_tagger = get_tagger()
        
        print("BERT 模型加载完成")

    def analyze(self, line: str) -> Dict:
        """综合分析诗句"""
        # 1. 词典标注（快速）
        dict_result = self.dict_tagger.tag(line)
        
        # 2. BERT 词性分析
        pos_tags = self._get_pos_tags(line)
        
        # 3. 命名实体识别
        entities = self._get_entities(line)
        
        return {
            'content': line,
            'dict_tags': dict_result.to_dict(),
            'pos_tags': pos_tags,
            'entities': entities,
            'suggested_tags': self._suggest_tags(line, dict_result, pos_tags, entities)
        }

    def _get_pos_tags(self, text: str) -> List[Dict]:
        """使用 BERT 获取词性标注"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        predictions = torch.argmax(outputs.logits, dim=-1)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        
        # 简化输出
        result = []
        for i, (token, pred) in enumerate(zip(tokens, predictions[0])):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                result.append({
                    'token': token,
                    'id': int(pred)
                })
        return result

    def _get_entities(self, text: str) -> List[str]:
        """识别命名实体（简单实现）"""
        # 这里可以用更复杂的 NER 模型
        # 目前先用词典匹配
        entities = []
        
        # 地名识别
        regions = ['江南', '塞北', '长安', '洛阳', '扬州', '江陵', '洞庭', '潇湘', '玉门', '阳关']
        for region in regions:
            if region in text:
                entities.append(f"LOC:{region}")
        
        # 人名识别（简单）
        names = ['李白', '杜甫', '王维', '白居易', '孟浩然', '王之涣', '李商隐', '杜牧']
        for name in names:
            if name in text:
                entities.append(f"PER:{name}")
        
        return entities

    def _suggest_tags(self, text: str, dict_result: PoemLine, 
                     pos_tags: List[Dict], entities: List[str]) -> Dict:
        """综合建议标签"""
        suggestions = {
            'season': dict_result.season,
            'element': dict_result.element,
            'imagery': list(dict_result.imagery),
            'emotion': list(dict_result.emotion),
            'color': dict_result.color,
            'region': dict_result.region,
            'entities': entities,
            'confidence': self._calculate_confidence(dict_result, entities)
        }
        return suggestions

    def _calculate_confidence(self, result: PoemLine, entities: List[str]) -> float:
        """计算标注置信度"""
        score = 0.5
        
        if result.season:
            score += 0.15
        if result.element:
            score += 0.15
        if result.imagery:
            score += 0.1 * min(len(result.imagery), 3)
        if entities:
            score += 0.1 * min(len(entities), 2)
        
        return min(score, 1.0)


# 全局实例
_bert_tagger = None

def get_bert_tagger(model_path: str = None) -> BertPoetryTagger:
    """获取 BERT 标注器实例"""
    global _bert_tagger
    if _bert_tagger is None:
        # 默认使用 E 盘本地模型
        if model_path is None:
            model_path = "E:/AI/Models/bert-base-chinese-v2"
        _bert_tagger = BertPoetryTagger(model_path)
    return _bert_tagger


if __name__ == '__main__':
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    print("=" * 60)
    print("BERT 诗词标注测试")
    print("=" * 60)
    
    tagger = get_bert_tagger()
    
    test_lines = [
        "床前明月光",
        "疑是地上霜",
        "春眠不觉晓",
        "春风又绿江南岸",
        "明月松间照",
        "清泉石上流"
    ]
    
    for line in test_lines:
        print(f"\n诗句: {line}")
        result = tagger.analyze(line)
        print(f"  季节: {result['suggested_tags']['season'] or '无'}")
        print(f"  五行: {result['suggested_tags']['element'] or '无'}")
        print(f"  意象: {', '.join(result['suggested_tags']['imagery']) or '无'}")
        print(f"  置信度: {result['suggested_tags']['confidence']:.2f}")
