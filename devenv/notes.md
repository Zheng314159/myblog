python -m pip install --upgrade pip setuptools wheel
pip install aiohttp



Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

setx PATH "C:\PythonMinimal;%PATH%"

pip config list
pip install numpy -v
pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
%APPDATA%\pip\pip.ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple

https://pypi.tuna.tsinghua.edu.cn/simple
https://pypi.mirrors.ustc.edu.cn/simple
https://mirrors.aliyun.com/pypi/simple


conda install numpy -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda env create -f environment.yml
conda create -n env_name python=3.11 numpy pandas



https://mirrors.tuna.tsinghua.edu.cn/anaconda/
https://mirrors.ustc.edu.cn/anaconda/
https://mirrors.aliyun.com/anaconda/
conda clean -i
conda update conda

poetry install -r https://pypi.tuna.tsinghua.edu.cn/simple
poetry config repositories.tuna https://pypi.tuna.tsinghua.edu.cn/simple
poetry config http-basic.tuna <username> <password>  # 如果需要认证
poetry config repositories.tuna https://pypi.tuna.tsinghua.edu.cn/simple
poetry config pypi-token.tuna <token-if-needed>
poetry config installer.parallel true
poetry config installer.max-time 600



