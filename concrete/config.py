# -*- coding: utf-8 -*-
"""
混凝土梁抗弯承载力计算程序配置文件
"""
import os

# 项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 数据文件路径
EXCEL_INPUT_PATH = os.path.join(PROJECT_ROOT, 'input', '梁抗弯承载力数据文件.xlsx')

# 结果输出配置
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
EXCEL_OUTPUT_NAME = "梁抗弯承载力计算结果.xlsx"
EXCEL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, EXCEL_OUTPUT_NAME)

# 抗震承载力调整系数
GAMMA_RE = 0.75

# Excel列定义
OUTPUT_COLS = {
    "x_col": "受压区高度x",  # Q列
    "mu_col": "抗弯承载力Mu",  # R列
    "mue_col": "抗震承载力MuE",  # S列
    "rs_col": "抗力效应比R/S"  # T列
}

# Q-T列的列索引映射（Excel列号从1开始）
COL_MAPPING = {
    "x_col": 17,  # Q列
    "mu_col": 18,  # R列
    "mue_col": 19,  # S列
    "rs_col": 20  # T列
}
