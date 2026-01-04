# -*- coding: utf-8 -*-
"""
结构计算程序通用异常类
"""


class CalculationError(Exception):
    """
    计算错误异常类
    """
    def __init__(self, message, section=None, parameter=None):
        """
        :param message: 错误信息
        :param section: 错误发生的截面编号
        :param parameter: 相关参数
        """
        self.message = message
        self.section = section
        self.parameter = parameter
        super().__init__(self.__str__())
    
    def __str__(self):
        """
        格式化错误信息
        """
        parts = [self.message]
        if self.section:
            parts.append(f"截面：{self.section}")
        if self.parameter:
            parts.append(f"参数：{self.parameter}")
        return " | ".join(parts)


class MaterialError(CalculationError):
    """
    材料参数错误异常类
    """
    pass


class GeometryError(CalculationError):
    """
    几何参数错误异常类
    """
    pass


class ParameterError(CalculationError):
    """
    参数错误异常类
    """
    pass