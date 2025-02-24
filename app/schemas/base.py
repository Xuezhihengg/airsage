from pydantic import BaseModel


def to_camel(string: str) -> str:
    """将蛇形命名法转换为驼峰命名法"""
    return ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(string.split('_')))


class _BaseModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
