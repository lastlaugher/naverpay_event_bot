pyinstaller --onefile main.py 
copy dist\main.exe .
"c:\Program Files\7-Zip\7z.exe" a naverpay_bot.zip main.exe accounts.txt event_urls.txt
del main.exe