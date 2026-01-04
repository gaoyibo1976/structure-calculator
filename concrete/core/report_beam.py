from . import rebar, concrete

class BeamReportBase:
    def __init__(self, num, param, result):
        self.num = num
        self.param = param
        self.result = result
        self._parse_params()
        
    def _parse_params(self):
        """解析公共参数"""
        # 解析混凝土参数
        self.fcuk = self._get_param('fcuk')
        conc = concrete.get_params(self.fcuk)
        self.fc = conc["fc"]
        self.ft = conc["ft"]
        self.Ec = conc["Ec"]
        self.α1 = conc["α1"]
        self.β1 = conc["β1"]
        self.εcu = 0.0033
        
        # 解析钢筋参数
        self.fy_grade = self._get_param('fy_grade')
        rt = rebar.get_params(self.fy_grade)
        self.fy = rt["fy"]
        self.Es = rt["Es"]
        self.ξb = rt["ξb"]
        
        self.fyc_grade = self._get_param('fyc_grade')
        rc = rebar.get_params(self.fyc_grade)
        self.fyc = rc["fy"]
        
        self.Ast = self._get_param('Ast')
        self.ast = self._get_param('ast')
        self.Asc = self._get_param('Asc')
        self.asc = self._get_param('asc')
        self.γ0 = self._get_param('γ0')
        
        # 解析结果参数
        self.x = self._get_result('x')
        self.xb = self._get_result('xb')
        self.ξ = self._get_result('ξ')
        self.Mu = self._get_result('Mu')
        self.σs = self._get_result('σs')
        self.σsc = self._get_result('σsc')
        self.check = self._get_result('check')
    
    def _get_param(self, param_name):
        """根据参数名获取参数值，子类需要实现"""
        raise NotImplementedError("子类必须实现_get_param方法")
    
    def _get_result(self, result_name):
        """根据结果名获取结果值，子类需要实现"""
        raise NotImplementedError("子类必须实现_get_result方法")
    
    def _get_title(self):
        """获取报告标题，子类需要实现"""
        raise NotImplementedError("子类必须实现_get_title方法")
    
    def _get_input_params_section(self):
        """获取输入参数部分，子类需要实现"""
        raise NotImplementedError("子类必须实现_get_input_params_section方法")
    
    def _get_calculation_results_section(self):
        """获取计算结果部分，子类需要实现"""
        raise NotImplementedError("子类必须实现_get_calculation_results_section方法")
    
    def generate_report(self):
        """生成完整报告"""
        return f"""{self._get_title()}
{self.num}
一.输入参数
{self._get_input_params_section()}
二.计算结果
{self._get_calculation_results_section()}
{self.check}
"""

class RectBeamReport(BeamReportBase):
    def __init__(self, num, param, result):
        self.b, self.h, self.fcuk, self.fy_grade, self.fyc_grade, \
        self.Ast, self.ast, self.Asc, self.asc, self.γ0 = param
        
        # 从扩展结果中获取M和rs_ratio
        if len(result) > 8:
            self.x, self.xb, self.ξ, self.ξb_val, self.Mu, self.σs, self.σsc, self.check, \
            self.M, self.rs_ratio = result
        else:
            self.x, self.xb, self.ξ, self.ξb_val, self.Mu, self.σs, self.σsc, self.check = result
            self.M = 0
            self.rs_ratio = 0
        
        super().__init__(num, param, result)
    
    def _get_param(self, param_name):
        """根据参数名获取矩形截面参数"""
        param_map = {
            'fcuk': self.fcuk,
            'fy_grade': self.fy_grade,
            'fyc_grade': self.fyc_grade,
            'Ast': self.Ast,
            'ast': self.ast,
            'Asc': self.Asc,
            'asc': self.asc,
            'γ0': self.γ0
        }
        return param_map[param_name]
    
    def _get_result(self, result_name):
        """根据结果名获取矩形截面结果"""
        result_map = {
            'x': self.x,
            'xb': self.xb,
            'ξ': self.ξ,
            'Mu': self.Mu,
            'σs': self.σs,
            'σsc': self.σsc,
            'check': self.check
        }
        return result_map[result_name]
    
    def _get_title(self):
        return "=====矩形截面梁已知配筋计算抗弯承载力====="
    
    def _get_input_params_section(self):
        return f"""1.1 梁宽b：{self.b}mm
1.2 梁高h：{self.h}mm
1.3 混凝土:强度等级C{self.fcuk}，抗压强度设计值fc={self.fc:.1f}N/mm²
1.4 受拉钢筋：强度等级{self.fy_grade}，屈服强度设计值fy={self.fy:.1f}N/mm²，弹性模量Es={self.Es:.1f}N/mm²
1.5 受压钢筋：强度等级{self.fyc_grade}，屈服强度设计值fy'={self.fyc:.1f}N/mm²
1.6 受拉钢筋面积As：{self.Ast}mm²
1.7 受拉钢筋面积As'：{self.Asc}mm²
1.8 受拉钢筋保护计算厚度as：{self.ast}mm
1.9 受压钢筋保护计算厚度as'：{self.asc}mm
1.10 弯矩设计值M：{self.M:.1f}kN·m
1.11 结构重要性系数γ0：{self.γ0:.1f}"""
    
    def _get_calculation_results_section(self):
        return f"""2.1 混凝土受压区高度x={self.x}mm
2.2 界限相对受压区高度ξb·h0={self.xb}mm
2.3 相对受压区高度比ξ={self.ξ}
2.4 界限相对受压区高度比ξb={self.ξb:.4f}
2.5 非地震作用抗弯承载力Mu={self.Mu}kN·m
2.6 地震作用时抗弯承载力MuE={self.Mu / 0.75:.2f}kN·m
2.7 受压钢筋应力σs'={self.σsc:.1f}N/mm²
2.8 受拉钢筋应力σs ={self.σs:.1f}N/mm²
2.9 抗力效应比R/S={self.rs_ratio:.2f}"""

class TBeamReport(BeamReportBase):
    def __init__(self, num, param, result):
        self.b, self.h, self.bf, self.hf, self.fcuk, self.fy_grade, \
        self.fyc_grade, self.Ast, self.ast, self.Asc, self.asc, self.γ0 = param
        
        # 从扩展结果中获取M和rs_ratio
        if len(result) > 9:
            self.flag, self.x, self.xb, self.ξ, self.ξb_val, self.Mu, \
            self.σs, self.σsc, self.check, self.M, self.rs_ratio = result
        else:
            self.flag, self.x, self.xb, self.ξ, self.ξb_val, self.Mu, \
            self.σs, self.σsc, self.check = result
            self.M = 0
            self.rs_ratio = 0
        
        super().__init__(num, param, result)
    
    def _get_param(self, param_name):
        """根据参数名获取T形截面参数"""
        param_map = {
            'fcuk': self.fcuk,
            'fy_grade': self.fy_grade,
            'fyc_grade': self.fyc_grade,
            'Ast': self.Ast,
            'ast': self.ast,
            'Asc': self.Asc,
            'asc': self.asc,
            'γ0': self.γ0
        }
        return param_map[param_name]
    
    def _get_result(self, result_name):
        """根据结果名获取T形截面结果"""
        result_map = {
            'x': self.x,
            'xb': self.xb,
            'ξ': self.ξ,
            'Mu': self.Mu,
            'σs': self.σs,
            'σsc': self.σsc,
            'check': self.check
        }
        return result_map[result_name]
    
    def _get_title(self):
        return "=====T形截面梁已知配筋计算抗弯承载力====="
    
    def _get_input_params_section(self):
        return f"""1.1 梁宽b：{self.b}mm
1.2 梁高h：{self.h}mm
1.3 受压翼缘宽度bf'：{self.bf}mm
1.4 受压翼缘厚度hf'：{self.hf}mm
1.5 混凝土:强度等级C{self.fcuk}，抗压强度设计值fc={self.fc:.1f}N/mm²
1.6 受拉钢筋：强度等级{self.fy_grade}，屈服强度设计值fy={self.fy:.1f}N/mm²，弹性模量Es={self.Es:.1f}N/mm²
1.7 受压钢筋：强度等级{self.fyc_grade}，屈服强度设计值fy'={self.fyc:.1f}N/mm²
1.8 受拉钢筋面积As：{self.Ast}mm²
1.9 受拉钢筋面积As'：{self.Asc}mm²
1.10 受拉钢筋保护计算厚度as：{self.ast}mm
1.11 受压钢筋保护计算厚度as'：{self.asc}mm
1.12 弯矩设计值M：{self.M:.1f}kN·m
1.13 结构重要性系数γ0：{self.γ0:.1f}"""
    
    def _get_calculation_results_section(self):
        return f"""2.1 T形截面类型判别：{self.flag}
2.2 混凝土受压区高度x={self.x}mm
2.3 界限相对受压区高度ξb·h0={self.xb}mm
2.4 相对受压区高度比ξ={self.ξ}
2.5 界限相对受压区高度比ξb={self.ξb:.4f}
2.6 非地震作用抗弯承载力Mu={self.Mu}kN·m
2.7 地震作用时抗弯承载力MuE={self.Mu / 0.75:.2f}kN·m
2.8 受压钢筋应力σs'={self.σsc:.1f}N/mm²
2.9 受拉钢筋应力σs ={self.σs:.1f}N/mm²
2.10 抗力效应比R/S={self.rs_ratio:.2f}"""

# 保持原有函数接口兼容
def report_beam_rect_fc(num, param, result):
    report = RectBeamReport(num, param, result)
    return report.generate_report()

def report_beam_t_fc(num, param, result):
    report = TBeamReport(num, param, result)
    return report.generate_report()