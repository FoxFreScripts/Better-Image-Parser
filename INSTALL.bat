@echo off

echo Installing dependencies...
pip install httpx[http2] requests beautifulsoup4 art colorama threading urljoin sys ssl time shutil os json
echo Dependencies installed successfully.

echo.
echo Running Rule34 Image Parser for PO_N...
python "Rule34 Image Parser.py"
pause
