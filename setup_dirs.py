import os
dirs = ['core', 'data', 'ui', 'utils', 'resources']
# Find the project base
for root, folders, files in os.walk(r'E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files'):
    if 'README.md' in files and 'IntelliKnowGraphText' in root:
        base = root
        break
else:
    base = r'E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText'

for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)
print('Created dirs at:', base)
