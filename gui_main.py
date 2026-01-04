import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import pandas as pd

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入实际的计算模块
from concrete.main.梁抗弯承载力计算 import calculate_single_item
from concrete.core.beam_rect_fc import beam_rect_fc
from concrete.core.beam_t_fc import beam_t_fc
from concrete.core.report_beam import report_beam_rect_fc, report_beam_t_fc
from concrete.config import GAMMA_RE

class BeamCalculationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("梁抗弯承载力计算程序")
        self.root.geometry("1200x800")
        
        # 设置主题和样式
        self.style = ttk.Style()
        self.style.theme_use("clam")
        # 将复选框样式设置为对勾
        self.style.configure("TCheckbutton", indicatoron=True)
        
        # 当前工作目录和数据文件，默认使用input文件夹
        self.current_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "input")
        self.data_file = "梁抗弯承载力数据文件.xlsx"
        
        # 结果窗口
        self.result_window = None
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧参数区
        self.left_frame = ttk.LabelFrame(self.main_frame, text="单个截面参数")
        self.left_frame.grid(row=0, column=0, rowspan=3, sticky=tk.N+tk.S+tk.E+tk.W, padx=5, pady=5)
        
        # 右侧数据文件和列表区
        self.right_frame = ttk.LabelFrame(self.main_frame, text="批量计算")
        self.right_frame.grid(row=0, column=1, sticky=tk.N+tk.E+tk.W, padx=5, pady=5)
        
        # 右侧计算选项区
        self.option_frame = ttk.LabelFrame(self.main_frame, text="计算选项")
        self.option_frame.grid(row=1, column=1, sticky=tk.N+tk.E+tk.W, padx=5, pady=5)
        
        # 右侧按钮区
        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.grid(row=2, column=1, sticky=tk.N+tk.E+tk.W, padx=5, pady=5)
        
        # 设置网格权重，让组件能够随窗口大小调整
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=0)
        
        # 初始化状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("就绪")
        
        # 初始化各个区域
        self.init_left_frame()
        self.init_right_frame()
        self.init_option_frame()
        self.init_btn_frame()
        
        # 初始化结果窗口
        self.init_result_window()
    
    def init_left_frame(self):
        """初始化左侧参数区"""
        # 参数列表
        params = [
            ("截面类型", ["矩形", "T形"], "sec_type", "矩形"),
            ("梁宽b", "mm", "b", 200),
            ("梁高h", "mm", "h", 400),
            ("受压翼缘宽度bf'", "mm", "bf", 1200),
            ("受压翼缘厚度hf'", "mm", "hf", 100),
            ("混凝土强度等级C", "", "fcuk", 30),  # 将C移到参数名称中
            ("受拉钢筋强度等级", ["HPB300", "HRB335", "HRB400", "HRB500", "HRBF335", "HRBF400", "HRBF500"], "fy_grade", "HRB400"),
            ("受压钢筋强度等级", ["HPB300", "HRB335", "HRB400", "HRB500", "HRBF335", "HRBF400", "HRBF500"], "fyc_grade", "HRB400"),
            ("受拉钢筋面积As", "mm²", "Ast", 1500),
            ("受拉钢筋as", "mm", "ast", 35),
            ("受压钢筋面积As'", "mm²", "Asc", 0),
            ("受压钢筋as'", "mm", "asc", 35),
            ("弯矩设计值M", "kN·m", "M", 250),
            ("是否地震作用组合", ["否", "是"], "is_seismic", "否"),
            ("结构重要性系数γ0", "", "gamma0", 1.0)
        ]
        
        self.param_vars = {}
        
        # 创建参数输入控件
        for i, param in enumerate(params):
            row = i
            col = 0
            
            label = ttk.Label(self.left_frame, text=f"{param[0]}:", width=15)
            label.grid(row=row, column=col, sticky=tk.E, padx=5, pady=5)
            col += 1
            
            if len(param) == 4:
                # 下拉菜单或带单位的输入框
                if isinstance(param[1], list):
                    # 下拉菜单 - 宽度与文本框一致
                    var = tk.StringVar(value=param[3])
                    combo = ttk.Combobox(self.left_frame, textvariable=var, values=param[1], state="readonly", width=10)
                    combo.grid(row=row, column=col, sticky=tk.W, padx=0, pady=5)  # 减少左侧间距
                    
                    # 绑定焦点事件，显示提示
                    combo.bind("<FocusIn>", lambda e, p=param: self.show_param_hint(p))
                    combo.bind("<FocusOut>", lambda e: self.status_var.set("就绪"))
                    
                    # 绑定选择事件，用于截面类型切换
                    if param[0] == "截面类型":
                        combo.bind("<<ComboboxSelected>>", self.on_section_type_change)
                    
                    col += 1
                    
                    # 如果有单位，显示单位
                    if isinstance(param[1], list) and len(param[1]) > 0 and not isinstance(param[1][0], str):
                        unit_label = ttk.Label(self.left_frame, text=param[1])
                        unit_label.grid(row=row, column=col, sticky=tk.W, padx=2, pady=5)  # 减少左侧间距
                else:
                    # 带单位的输入框
                    unit = param[1]
                    default_val = param[3]
                    
                    # 创建输入框
                    var = tk.StringVar(value=str(default_val))
                    entry = ttk.Entry(self.left_frame, textvariable=var, width=10)
                    entry.grid(row=row, column=col, sticky=tk.W, padx=0, pady=5)  # 减少左侧间距
                    
                    # 绑定焦点事件，显示提示
                    entry.bind("<FocusIn>", lambda e, p=param: self.show_param_hint(p))
                    entry.bind("<FocusOut>", lambda e: self.status_var.set("就绪"))
                    
                    col += 1
                    
                    # 显示单位，靠近输入框
                    unit_label = ttk.Label(self.left_frame, text=unit)
                    unit_label.grid(row=row, column=col, sticky=tk.W, padx=2, pady=5)  # 减少左侧间距
            
            self.param_vars[param[-1]] = var
        
        # 初始隐藏T形截面参数
        # 确保param_vars中已经有sec_type键后再调用
        if 'sec_type' in self.param_vars:
            self.on_section_type_change(None)
        
        # 尝试加载数据文件的第一行数据到参数区
        self.load_default_data()
    
    def init_right_frame(self):
        """初始化右侧数据文件和列表区"""
        # 数据文件选择
        file_frame = ttk.Frame(self.right_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="数据文件：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_var = tk.StringVar(value=self.data_file)
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=25)
        self.file_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Button(file_frame, text="选择文件", command=self.select_file).grid(row=0, column=2, padx=5, pady=5)
        
        # 当前工作目录显示
        dir_frame = ttk.Frame(self.right_frame)
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dir_frame, text="当前目录：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.dir_var = tk.StringVar(value=self.current_dir)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, state="readonly")
        dir_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 截面列表框 - 调整宽度为更紧凑的尺寸
        list_frame = ttk.Frame(self.right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(list_frame, text="截面列表：").pack(anchor=tk.W, padx=5, pady=5)
        
        # 减小列表框宽度，只显示序号和编号
        self.section_list = tk.Listbox(list_frame, height=15, width=35)
        self.section_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.section_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.section_list.config(yscrollcommand=scrollbar.set)
        
        # 绑定列表框选择事件
        self.section_list.bind("<<ListboxSelect>>", self.on_section_select)
    
    def load_default_data(self):
        """加载数据文件的第一行数据到参数区"""
        try:
            file_path = os.path.join(self.current_dir, self.data_file)
            if os.path.exists(file_path):
                df = pd.read_excel(file_path, engine="openpyxl")
                if not df.empty:
                    row = df.iloc[0]
                    # 更新参数区的参数，确保键存在
                    if 'sec_type' in self.param_vars:
                        self.param_vars["sec_type"].set(row.get("截面类型", "矩形"))
                    if 'b' in self.param_vars:
                        self.param_vars["b"].set(str(row.get("b", 200)))
                    if 'h' in self.param_vars:
                        self.param_vars["h"].set(str(row.get("h", 400)))
                    if 'bf' in self.param_vars:
                        self.param_vars["bf"].set(str(row.get("bf", 1200)))
                    if 'hf' in self.param_vars:
                        self.param_vars["hf"].set(str(row.get("hf", 100)))
                    if 'fcuk' in self.param_vars:
                        self.param_vars["fcuk"].set(str(row.get("混凝土强度等级C", 30)))
                    if 'fy_grade' in self.param_vars:
                        self.param_vars["fy_grade"].set(row.get("受拉钢筋强度等级", "HRB400"))
                    if 'fyc_grade' in self.param_vars:
                        self.param_vars["fyc_grade"].set(row.get("受压钢筋强度等级", "HRB400"))
                    if 'Ast' in self.param_vars:
                        self.param_vars["Ast"].set(str(row.get("受拉钢筋面积As", 1500)))
                    if 'ast' in self.param_vars:
                        self.param_vars["ast"].set(str(row.get("受拉钢筋as", 35)))
                    if 'Asc' in self.param_vars:
                        self.param_vars["Asc"].set(str(row.get("受压钢筋面积As", 0)))
                    if 'asc' in self.param_vars:
                        self.param_vars["asc"].set(str(row.get("受压钢筋as", 35)))
                    if 'M' in self.param_vars:
                        self.param_vars["M"].set(str(row.get("弯矩设计值M", 250)))
                    if 'is_seismic' in self.param_vars:
                        self.param_vars["is_seismic"].set("是" if row.get("是否地震作用组合", 0) == 1 else "否")
                    if 'gamma0' in self.param_vars:
                        self.param_vars["gamma0"].set(str(row.get("结构重要性系数γ0", 1.0)))
                    
                    # 保存数据以便后续使用
                    self.df = df
                    
                    # 刷新截面列表
                    self.refresh_section_list()
                    
                    self.status_var.set("已加载默认截面数据")
        except Exception as e:
            self.status_var.set(f"加载默认数据失败：{str(e)}")
            # 这是初始化过程，不显示错误对话框
            pass
    
    def init_option_frame(self):
        """初始化右侧计算选项区"""
        # 生成Excel结果文件选项
        self.excel_var = tk.BooleanVar(value=True)
        # 使用ttk.Checkbutton，默认样式为对勾
        excel_check = ttk.Checkbutton(self.option_frame, text="生成Excel结果文件", variable=self.excel_var, command=self.toggle_excel_entry)
        excel_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.option_frame, text="文件名：").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.excel_file_var = tk.StringVar(value="抗弯承载力计算结果.xlsx")
        self.excel_entry = ttk.Entry(self.option_frame, textvariable=self.excel_file_var)
        self.excel_entry.grid(row=0, column=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 设置网格权重
        self.option_frame.columnconfigure(2, weight=1)
    
    def init_btn_frame(self):
        """初始化右侧按钮区"""
        # 使用grid布局管理器
        btn_frame = ttk.Frame(self.btn_frame)
        btn_frame.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        
        ttk.Button(btn_frame, text="单个截面计算", command=self.calculate_single).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="批量计算", command=self.calculate_batch).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="刷新截面列表", command=self.refresh_section_list).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="修改并保存", command=self.modify_and_save).grid(row=0, column=3, padx=5, pady=5)
        
        # 设置框架权重，让按钮居中
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.columnconfigure(3, weight=1)
    
    def init_result_window(self):
        """初始化结果窗口"""
        # 创建结果窗口
        self.result_window = tk.Toplevel(self.root)
        self.result_window.title("计算结果")
        self.result_window.geometry("800x600")
        
        # 创建工具栏
        toolbar = ttk.Frame(self.result_window)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="保存结果", command=self.save_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="另存为", command=self.save_result_as).pack(side=tk.LEFT, padx=5)
        
        # 创建文本输出框
        self.result_text = tk.Text(self.result_window, wrap=tk.WORD, font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.result_text, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 添加文本样式
        self.result_text.tag_configure("title", font=("Consolas", 12, "bold"))
        self.result_text.tag_configure("heading", font=("Consolas", 10, "bold"))
        self.result_text.tag_configure("error", foreground="red")
        
        # 显示结果窗口
        self.result_window.deiconify()
    
    def show_param_hint(self, param):
        """显示参数输入提示"""
        if len(param) == 4:
            if isinstance(param[1], list):
                hint = f"{param[0]}：请选择{'、'.join(param[1])}"
            else:
                hint = f"{param[0]}：单位{param[1]}，默认值{param[3]}"
            self.status_var.set(hint)
    
    def toggle_excel_entry(self):
        """切换Excel文件名输入框的状态"""
        if self.excel_var.get():
            self.excel_entry.config(state="normal")
        else:
            self.excel_entry.config(state="disabled")
    
    def on_section_type_change(self, event):
        """截面类型切换事件"""
        sec_type = self.param_vars["sec_type"].get()
        
        # 显示或隐藏T形截面参数
        for widget in self.left_frame.winfo_children():
            # 获取控件的位置
            info = widget.grid_info()
            if info and "row" in info:
                row = info["row"]
                # 3和4行是T形截面参数（受压翼缘宽度和厚度）
                if sec_type == "矩形" and (row == 3 or row == 4):
                    widget.grid_remove()
                elif sec_type == "T形" and (row == 3 or row == 4):
                    widget.grid()
                else:
                    widget.grid()
    
    def select_file(self):
        """选择数据文件"""
        file_path = filedialog.askopenfilename(
            initialdir=self.current_dir,
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            title="选择数据文件"
        )
        if file_path:
            self.data_file = os.path.basename(file_path)
            self.current_dir = os.path.dirname(file_path)
            self.file_var.set(self.data_file)
            self.dir_var.set(self.current_dir)
            self.refresh_section_list()
            self.status_var.set(f"数据文件已选择：{file_path}")
    
    def refresh_section_list(self):
        """刷新截面列表"""
        try:
            # 清空列表
            self.section_list.delete(0, tk.END)
            
            # 读取Excel文件
            file_path = os.path.join(self.current_dir, self.data_file)
            df = pd.read_excel(file_path, engine="openpyxl")
            
            # 保存数据以便后续使用
            self.df = df
            
            # 添加到列表框，显示截面序号和编号
            for idx, row in df.iterrows():
                sec_num = row.get("截面编号", "")
                sec_type = row.get("截面类型", "未知")
                self.section_list.insert(tk.END, f"序号：{idx+1}  编号：{sec_num}  类型：{sec_type}")
                
            self.status_var.set(f"已加载{len(df)}个截面")
        except Exception as e:
            messagebox.showerror("错误", f"读取数据文件失败：{str(e)}")
            self.status_var.set("读取数据文件失败")
    
    def on_section_select(self, event):
        """当选择截面时，更新参数区的参数"""
        selection = self.section_list.curselection()
        if selection and hasattr(self, 'df'):
            idx = selection[0]
            try:
                if idx < len(self.df):
                    row = self.df.iloc[idx]
                    # 更新参数区的参数
                    self.param_vars["sec_type"].set(row.get("截面类型", "矩形"))
                    self.param_vars["b"].set(str(row.get("b", 200)))
                    self.param_vars["h"].set(str(row.get("h", 400)))
                    self.param_vars["bf"].set(str(row.get("bf", 1200)))
                    self.param_vars["hf"].set(str(row.get("hf", 100)))
                    self.param_vars["fcuk"].set(str(row.get("混凝土强度等级C", 30)))
                    self.param_vars["fy_grade"].set(row.get("受拉钢筋强度等级", "HRB400"))
                    self.param_vars["fyc_grade"].set(row.get("受压钢筋强度等级", "HRB400"))
                    self.param_vars["Ast"].set(str(row.get("受拉钢筋面积As", 1500)))
                    self.param_vars["ast"].set(str(row.get("受拉钢筋as", 35)))
                    self.param_vars["Asc"].set(str(row.get("受压钢筋面积As", 0)))
                    self.param_vars["asc"].set(str(row.get("受压钢筋as", 35)))
                    self.param_vars["M"].set(str(row.get("弯矩设计值M", 250)))
                    self.param_vars["is_seismic"].set("是" if row.get("是否地震作用组合", 0) == 1 else "否")
                    self.param_vars["gamma0"].set(str(row.get("结构重要性系数γ0", 1.0)))
                    
                    # 保存当前选中的行索引
                    self.current_row_idx = idx
                    
                    self.status_var.set(f"已加载截面{idx+1}")
            except Exception as e:
                messagebox.showerror("错误", f"加载截面数据失败：{str(e)}")
                self.status_var.set("加载截面数据失败")
    
    def calculate_single(self):
        """单个截面计算"""
        try:
            # 检查param_vars字典是否包含所需的所有键
            required_keys = ["sec_type", "b", "h", "bf", "hf", "fcuk", "fy_grade", "fyc_grade", 
                           "Ast", "ast", "Asc", "asc", "M", "is_seismic", "gamma0"]
            
            # 确保所有必需的键都存在
            for key in required_keys:
                if key not in self.param_vars:
                    messagebox.showerror("错误", f"参数缺失：{key}")
                    self.status_var.set(f"参数缺失：{key}")
                    return
            
            # 获取参数
            sec_type = self.param_vars["sec_type"].get()
            b = float(self.param_vars["b"].get())
            h = float(self.param_vars["h"].get())
            bf = float(self.param_vars["bf"].get())
            hf = float(self.param_vars["hf"].get())
            fcuk = float(self.param_vars["fcuk"].get())
            fy_grade = self.param_vars["fy_grade"].get()
            fyc_grade = self.param_vars["fyc_grade"].get()
            Ast = float(self.param_vars["Ast"].get())
            ast = float(self.param_vars["ast"].get())
            Asc = float(self.param_vars["Asc"].get())
            asc = float(self.param_vars["asc"].get())
            M = float(self.param_vars["M"].get())
            is_seismic = 1 if self.param_vars["is_seismic"].get() == "是" else 0
            gamma0 = float(self.param_vars["gamma0"].get())
            
            # 构建计算参数
            item = {
                "sec_type": sec_type,
                "sec_num": "单个计算",
                "M": M,
                "is_seismic": is_seismic,
                "γ0": gamma0
            }
            
            if sec_type == "矩形":
                # 矩形截面计算
                rect_calc_p = [b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc, gamma0]
                result = beam_rect_fc(*rect_calc_p)
                
                # 计算抗力效应比
                Mu = result[4]
                MuE = Mu / GAMMA_RE
                rs_ratio = (MuE / M if is_seismic == 1 else Mu / M) if M > 0 else 0
                
                # 生成扩展结果（包含M和rs_ratio）
                extended_result = result + (M, rs_ratio)
                
                # 生成报告
                report = report_beam_rect_fc("单个计算截面", rect_calc_p, extended_result)
            else:
                # T形截面计算
                t_calc_p = [b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc, gamma0]
                result = beam_t_fc(*t_calc_p)
                
                # 计算抗力效应比
                Mu = result[5]
                MuE = Mu / GAMMA_RE
                rs_ratio = (MuE / M if is_seismic == 1 else Mu / M) if M > 0 else 0
                
                # 生成扩展结果（包含M和rs_ratio）
                extended_result = result + (M, rs_ratio)
                
                # 生成报告
                report = report_beam_t_fc("单个计算截面", t_calc_p, extended_result)
            
            # 显示结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, report)
            self.status_var.set("单个截面计算完成")
        except ValueError as e:
            messagebox.showerror("错误", f"参数输入错误：{str(e)}")
            self.status_var.set("参数输入错误")
        except KeyError as e:
            messagebox.showerror("错误", f"参数键缺失：{str(e)}")
            self.status_var.set(f"参数键缺失：{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
            self.status_var.set(f"计算失败：{str(e)}")
    
    def calculate_batch(self):
        """批量计算"""
        try:
            # 获取数据文件路径
            file_path = os.path.join(self.current_dir, self.data_file)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"数据文件不存在：{file_path}")
                self.status_var.set(f"数据文件不存在：{file_path}")
                return
            
            # 读取数据文件
            df = pd.read_excel(file_path, engine="openpyxl")
            
            # 导入数据准备函数
            from concrete.core.beam_utils import prepare_calculation_data
            
            # 准备计算数据
            param, result_data = prepare_calculation_data(df)
            
            # 显示计算结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "=====批量计算结果=====\n", "title")
            self.result_text.insert(tk.END, f"数据文件：{file_path}\n")
            self.result_text.insert(tk.END, f"共{len(df)}个截面\n\n")
            
            # 遍历所有截面进行计算
            total_count = len(param)
            error_count = 0
            
            # 保存所有报告
            all_reports = []
            
            for idx, item in enumerate(param):
                # 调用单个计算函数
                x, Mu, M, rs_ratio, report, error_msg = calculate_single_item(item, idx, total_count)
                
                # 添加报告到列表
                all_reports.append(report)
                
                # 记录错误
                if error_msg:
                    error_count += 1
                
                # 更新状态
                self.status_var.set(f"正在计算截面{idx+1}/{total_count}")
                self.root.update()
                if self.result_window:
                    self.result_window.update()
            
            # 显示所有报告
            for report in all_reports:
                self.result_text.insert(tk.END, report + "\n\n")
            
            # 生成Excel结果文件
            if self.excel_var.get():
                excel_file = os.path.join(self.current_dir, self.excel_file_var.get())
                
                self.result_text.insert(tk.END, f"\n正在生成Excel结果文件...\n")
                self.root.update()
                if self.result_window:
                    self.result_window.update()
                
                # 导入实际的Excel保存函数
                from concrete.core.beam_utils import save_excel_result_with_style
                
                # 保存Excel结果
                save_excel_result_with_style(result_data, excel_file, file_path)
                
                self.result_text.insert(tk.END, f"已生成Excel结果文件：{excel_file}\n")
            
            # 显示总结
            summary = f"\n=====计算总结=====\n"
            summary += f"总截面数：{total_count}\n"
            summary += f"成功计算：{total_count - error_count}\n"
            summary += f"计算失败：{error_count}\n"
            self.result_text.insert(tk.END, summary)
            
            self.status_var.set(f"批量计算完成，共{total_count}个截面，{error_count}个失败")
        except FileNotFoundError as e:
            messagebox.showerror("错误", f"文件不存在：{str(e)}")
            self.status_var.set(f"文件不存在：{str(e)}")
        except PermissionError as e:
            messagebox.showerror("错误", f"权限不足：{str(e)}")
            self.status_var.set(f"权限不足：{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"批量计算失败：{str(e)}")
            self.status_var.set(f"批量计算失败：{str(e)}")
    
    def modify_and_save(self):
        """修改并保存截面数据"""
        try:
            if not hasattr(self, 'df') or not hasattr(self, 'current_row_idx'):
                messagebox.showwarning("警告", "请先选择一个截面进行修改")
                return
            
            # 获取当前选中的行索引
            idx = self.current_row_idx
            
            # 获取修改后的参数
            sec_type = self.param_vars["sec_type"].get()
            b = float(self.param_vars["b"].get())
            h = float(self.param_vars["h"].get())
            bf = float(self.param_vars["bf"].get())
            hf = float(self.param_vars["hf"].get())
            fcuk = float(self.param_vars["fcuk"].get())
            fy_grade = self.param_vars["fy_grade"].get()
            fyc_grade = self.param_vars["fyc_grade"].get()
            Ast = float(self.param_vars["Ast"].get())
            ast = float(self.param_vars["ast"].get())
            Asc = float(self.param_vars["Asc"].get())
            asc = float(self.param_vars["asc"].get())
            M = float(self.param_vars["M"].get())
            is_seismic = 1 if self.param_vars["is_seismic"].get() == "是" else 0
            gamma0 = float(self.param_vars["gamma0"].get())
            
            # 更新数据框
            self.df.at[idx, "截面类型"] = sec_type
            self.df.at[idx, "b"] = b
            self.df.at[idx, "h"] = h
            self.df.at[idx, "bf"] = bf
            self.df.at[idx, "hf"] = hf
            self.df.at[idx, "混凝土强度等级C"] = fcuk
            self.df.at[idx, "受拉钢筋强度等级"] = fy_grade
            self.df.at[idx, "受压钢筋强度等级"] = fyc_grade
            self.df.at[idx, "受拉钢筋面积As"] = Ast
            self.df.at[idx, "受拉钢筋as"] = ast
            self.df.at[idx, "受压钢筋面积As"] = Asc
            self.df.at[idx, "受压钢筋as"] = asc
            self.df.at[idx, "弯矩设计值M"] = M
            self.df.at[idx, "是否地震作用组合"] = is_seismic
            self.df.at[idx, "结构重要性系数γ0"] = gamma0
            
            # 保存到文件
            file_path = os.path.join(self.current_dir, self.data_file)
            self.df.to_excel(file_path, index=False, engine="openpyxl")
            
            # 刷新截面列表
            self.refresh_section_list()
            
            messagebox.showinfo("成功", f"截面{idx+1}的数据已保存")
            self.status_var.set(f"截面{idx+1}的数据已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存截面数据失败：{str(e)}")
            self.status_var.set("保存截面数据失败")
    
    def save_result(self):
        """保存结果"""
        try:
            result = self.result_text.get(1.0, tk.END)
            if not result.strip():
                messagebox.showwarning("警告", "没有可保存的结果")
                return
            
            file_path = filedialog.asksaveasfilename(
                initialdir=self.current_dir,
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                title="保存计算结果"
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result)
                self.status_var.set(f"结果已保存到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存结果失败：{str(e)}")
            self.status_var.set("保存结果失败")
    
    def save_result_as(self):
        """另存结果"""
        self.save_result()


def main():
    """主函数"""
    root = tk.Tk()
    app = BeamCalculationGUI(root)
    
    # 设置窗口位置，让主窗口和结果窗口并列显示
    root.geometry("800x600+100+100")
    
    root.mainloop()

if __name__ == "__main__":
    main()