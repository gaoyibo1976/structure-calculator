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
        
        # 设置主题
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # 结果输出窗口
        self.result_window = None
        
        # 当前工作目录和数据文件
        self.current_dir = os.getcwd()
        self.data_file = "梁抗弯承载力数据文件.xlsx"
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建交互区1：单个截面计算
        self.frame_single = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_single, text="单个截面计算")
        
        # 创建交互区2：批量计算
        self.frame_batch = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_batch, text="批量计算")
        
        # 创建结果输出区
        self.frame_result = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_result, text="计算结果")
        
        # 初始化各个区域
        self.init_single_frame()
        self.init_batch_frame()
        self.init_result_frame()
        
        # 初始化状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("就绪")
    
    def init_single_frame(self):
        """初始化单个截面计算区"""
        # 创建参数输入框架
        param_frame = ttk.LabelFrame(self.frame_single, text="截面参数")
        param_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 参数列表
        params = [
            ("截面类型", ["矩形", "T形"], "sec_type"),
            ("梁宽b", "mm", "b", 200),
            ("梁高h", "mm", "h", 400),
            ("受压翼缘宽度bf'", "mm", "bf", 1200),
            ("受压翼缘厚度hf'", "mm", "hf", 100),
            ("混凝土强度等级", "C", "fcuk", 30),
            ("受拉钢筋强度等级", ["HRB335", "HRB400", "HRB500"], "fy_grade", "HRB400"),
            ("受压钢筋强度等级", ["HRB335", "HRB400", "HRB500"], "fyc_grade", "HRB400"),
            ("受拉钢筋面积As", "mm²", "Ast", 1500),
            ("受拉钢筋as", "mm", "ast", 35),
            ("受压钢筋面积As'", "mm²", "Asc", 0),
            ("受压钢筋as'", "mm", "asc", 35),
            ("弯矩设计值M", "kN·m", "M", 250),
            ("是否地震作用组合", ["是", "否"], "is_seismic", "否"),
            ("结构重要性系数γ0", "", "gamma0", 1.0)
        ]
        
        self.param_vars = {}
        
        # 创建参数输入控件
        for i, param in enumerate(params):
            row = i // 3
            col = (i % 3) * 4
            
            label = ttk.Label(param_frame, text=f"{param[0]}:")
            label.grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
            
            if len(param) == 3:
                # 下拉菜单
                var = tk.StringVar(value=param[1][0])
                combo = ttk.Combobox(param_frame, textvariable=var, values=param[1], state="readonly")
                combo.grid(row=row, column=col+1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
            else:
                # 带单位的输入框
                unit = param[1]
                default_val = param[3]
                
                # 创建输入框
                var = tk.StringVar(value=str(default_val))
                entry = ttk.Entry(param_frame, textvariable=var, width=10)
                entry.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=5)
                
                # 绑定焦点事件，显示提示
                entry.bind("<FocusIn>", lambda e, p=param: self.show_param_hint(p))
                entry.bind("<FocusOut>", lambda e: self.status_var.set("就绪"))
                
                # 显示单位
                unit_label = ttk.Label(param_frame, text=unit)
                unit_label.grid(row=row, column=col+2, sticky=tk.W, padx=5, pady=5)
            
            self.param_vars[param[-1]] = var
        
        # 创建计算按钮
        calc_btn = ttk.Button(self.frame_single, text="计算", command=self.calculate_single)
        calc_btn.pack(side=tk.BOTTOM, padx=10, pady=10)
    
    def init_batch_frame(self):
        """初始化批量计算区"""
        # 创建数据文件选择框架
        file_frame = ttk.LabelFrame(self.frame_batch, text="数据文件")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 当前工作目录和数据文件
        ttk.Label(file_frame, text="当前工作目录：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.dir_var = tk.StringVar(value=self.current_dir)
        dir_entry = ttk.Entry(file_frame, textvariable=self.dir_var, state="readonly")
        dir_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Button(file_frame, text="选择目录", command=self.select_directory).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(file_frame, text="数据文件：").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_var = tk.StringVar(value=self.data_file)
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=30)
        file_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(file_frame, text="选择文件", command=self.select_file).grid(row=1, column=2, padx=5, pady=5)
        
        # 创建截面列表框
        list_frame = ttk.LabelFrame(self.frame_batch, text="截面列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.section_list = tk.Listbox(list_frame, height=10)
        self.section_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.section_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.section_list.config(yscrollcommand=scrollbar.set)
        
        # 绑定列表框选择事件
        self.section_list.bind("<<ListboxSelect>>", self.on_section_select)
        
        # 创建计算选项框架
        option_frame = ttk.LabelFrame(self.frame_batch, text="计算选项")
        option_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 生成Excel结果文件选项
        self.excel_var = tk.BooleanVar(value=True)
        excel_check = ttk.Checkbutton(option_frame, text="生成Excel结果文件", variable=self.excel_var, command=self.toggle_excel_entry)
        excel_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(option_frame, text="文件名：").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.excel_file_var = tk.StringVar(value="抗弯承载力计算结果.xlsx")
        self.excel_entry = ttk.Entry(option_frame, textvariable=self.excel_file_var)
        self.excel_entry.grid(row=0, column=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 创建计算按钮
        btn_frame = ttk.Frame(self.frame_batch)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="按数据文件计算", command=self.calculate_batch).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新截面列表", command=self.refresh_section_list).pack(side=tk.LEFT, padx=5)
    
    def init_result_frame(self):
        """初始化结果输出区"""
        # 创建工具栏
        toolbar = ttk.Frame(self.frame_result)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="保存结果", command=self.save_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="另存为", command=self.save_result_as).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="分离窗口", command=self.detach_result_window).pack(side=tk.LEFT, padx=5)
        
        # 创建文本输出框
        self.result_text = tk.Text(self.frame_result, wrap=tk.WORD, font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.result_text, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 添加文本样式
        self.result_text.tag_configure("title", font=("Consolas", 12, "bold"))
        self.result_text.tag_configure("heading", font=("Consolas", 10, "bold"))
        self.result_text.tag_configure("error", foreground="red")
    
    def show_param_hint(self, param):
        """显示参数输入提示"""
        if len(param) == 3:
            hint = f"选择截面类型：{', '.join(param[1])}"
        else:
            name, unit, _, default = param
            hint = f"{name}：单位{unit}，默认值{default}"
        self.status_var.set(hint)
    
    def toggle_excel_entry(self):
        """切换Excel文件名输入框的状态"""
        if self.excel_var.get():
            self.excel_entry.config(state="normal")
        else:
            self.excel_entry.config(state="disabled")
    
    def select_directory(self):
        """选择工作目录"""
        dir_path = filedialog.askdirectory(initialdir=self.current_dir)
        if dir_path:
            self.current_dir = dir_path
            self.dir_var.set(dir_path)
            self.status_var.set(f"工作目录已设置为：{dir_path}")
    
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
            
            # 添加到列表框
            for idx, row in df.iterrows():
                sec_num = row.get("截面编号", f"截面{idx+1}")
                sec_type = row.get("截面类型", "未知")
                self.section_list.insert(tk.END, f"{sec_num} - {sec_type}")
                
            self.status_var.set(f"已加载{len(df)}个截面")
        except Exception as e:
            messagebox.showerror("错误", f"读取数据文件失败：{str(e)}")
            self.status_var.set("读取数据文件失败")
    
    def on_section_select(self, event):
        """当选择截面时，更新交互区1的参数"""
        selection = self.section_list.curselection()
        if selection:
            idx = selection[0]
            try:
                # 读取数据文件
                file_path = os.path.join(self.current_dir, self.data_file)
                df = pd.read_excel(file_path, engine="openpyxl")
                
                if idx < len(df):
                    row = df.iloc[idx]
                    # 更新交互区1的参数
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
                    
                    self.status_var.set(f"已加载截面{idx+1}")
            except Exception as e:
                messagebox.showerror("错误", f"加载截面数据失败：{str(e)}")
                self.status_var.set("加载截面数据失败")
    
    def calculate_single(self):
        """单个截面计算"""
        try:
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
        except Exception as e:
            messagebox.showerror("错误", f"计算失败：{str(e)}")
            self.status_var.set("计算失败")
    
    def calculate_batch(self):
        """批量计算"""
        try:
            # 获取数据文件路径
            file_path = os.path.join(self.current_dir, self.data_file)
            
            # 读取数据文件
            df = pd.read_excel(file_path, engine="openpyxl")
            
            # 显示计算结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "=====批量计算结果=====\n", "title")
            self.result_text.insert(tk.END, f"数据文件：{file_path}\n")
            self.result_text.insert(tk.END, f"共{len(df)}个截面\n\n")
            
            # 导入数据准备和保存函数
            from concrete.core.beam_utils import prepare_calculation_data, save_excel_result_with_style
            from concrete.config import OUTPUT_COLS, EXCEL_INPUT_PATH, EXCEL_OUTPUT_PATH
            
            # 准备计算数据
            param, result_data = prepare_calculation_data(df)
            
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
            
            # 显示所有报告
            for report in all_reports:
                self.result_text.insert(tk.END, report + "\n\n")
            
            # 生成Excel结果文件
            if self.excel_var.get():
                excel_file = os.path.join(self.current_dir, self.excel_file_var.get())
                # 这里应该调用实际的Excel生成函数
                self.result_text.insert(tk.END, f"\n正在生成Excel结果文件...\n")
                self.root.update()
                
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
        except Exception as e:
            messagebox.showerror("错误", f"批量计算失败：{str(e)}")
            self.status_var.set("批量计算失败")
    
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
    
    def detach_result_window(self):
        """分离结果窗口"""
        if not self.result_window:
            # 创建新窗口
            self.result_window = tk.Toplevel(self.root)
            self.result_window.title("计算结果")
            self.result_window.geometry("800x600")
            
            # 创建工具栏
            toolbar = ttk.Frame(self.result_window)
            toolbar.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Button(toolbar, text="保存结果", command=self.save_result).pack(side=tk.LEFT, padx=5)
            ttk.Button(toolbar, text="另存为", command=self.save_result_as).pack(side=tk.LEFT, padx=5)
            ttk.Button(toolbar, text="关闭窗口", command=self.attach_result_window).pack(side=tk.LEFT, padx=5)
            
            # 创建文本框
            self.detached_text = tk.Text(self.result_window, wrap=tk.WORD, font=("Consolas", 10))
            self.detached_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(self.detached_text, orient=tk.VERTICAL, command=self.detached_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.detached_text.config(yscrollcommand=scrollbar.set)
            
            # 添加文本样式
            self.detached_text.tag_configure("title", font=("Consolas", 12, "bold"))
            self.detached_text.tag_configure("heading", font=("Consolas", 10, "bold"))
            self.detached_text.tag_configure("error", foreground="red")
            
            # 复制当前结果
            self.detached_text.insert(tk.END, self.result_text.get(1.0, tk.END))
            
            # 绑定窗口关闭事件
            self.result_window.protocol("WM_DELETE_WINDOW", self.attach_result_window)
        
        # 显示分离窗口
        self.result_window.deiconify()
        self.result_window.lift()
    
    def attach_result_window(self):
        """附加结果窗口"""
        if self.result_window:
            # 复制分离窗口的内容到主窗口
            if hasattr(self, 'detached_text'):
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, self.detached_text.get(1.0, tk.END))
            
            # 销毁分离窗口
            self.result_window.destroy()
            self.result_window = None
    
    def update_result(self, result):
        """更新结果显示"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        
        # 如果分离窗口存在，也更新其内容
        if self.result_window and hasattr(self, 'detached_text'):
            self.detached_text.delete(1.0, tk.END)
            self.detached_text.insert(tk.END, result)

def main():
    """主函数"""
    root = tk.Tk()
    app = BeamCalculationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()