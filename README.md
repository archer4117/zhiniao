# zhiniao

图形验证码识别需要依赖tesserocr(建议安装whl包)
tesserocr需要先安装tesseract.exe，下载地址：https://digi.bib.uni-mannheim.de/tesseract，
安装完成后需要配置环境变量
（对应版本需要匹配。如tesserocr2.4.0对应的tesseract为4.0具体版本对应参考https://github.com/simonflueckiger/tesserocr-windows_build/releases）

安装之后如出现如下错误：
RuntimeError: Failed to init API, possibly an invalid tessdata path: C:\Users\zw\AppData\Local\Programs\Python\Python36\/tessdata/

需要将tesseract安装目录下的tessdata文件夹拷贝到Python安装目录下 如/python36/
