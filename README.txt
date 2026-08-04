V5 使用说明

1. 把整个 car_import_v5 文件夹复制到 C:\cars price\v5
2. 把原来的 Cars price.xlsx 复制到 v5 文件夹
3. 打开 VS Code 终端，进入该目录：
   cd /d "C:\cars price\v5"
4. 安装依赖：
   python -m pip install -r requirements.txt
5. 运行：
   python -m streamlit run app.py

页面：
- 主页面：车辆报价、PDF、自动保存数据库
- 左侧菜单：客户管理
- 左侧菜单：数据统计

数据库会自动生成：
customers.db
