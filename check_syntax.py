import py_compile
import sys

try:
    py_compile.compile(r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText\core\llm_client.py", doraise=True)
    print("语法正确")
except py_compile.PyCompileError as e:
    print(f"语法错误: {e}")
    sys.exit(1)