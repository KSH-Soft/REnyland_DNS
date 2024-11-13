@echo off
mode con: cols=76 lines=15
if not "%1"=="am_admin" (
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0' -ArgumentList 'am_admin'"
    exit /b
)
call:LOGO
echo,
echo,
set /p "VARIABLE=Enter SERVER IP: "
echo,
call:PROCESS
call:LOGO
echo FR : La redirection a bien ete applique
echo,
echo EN : The redirection has been applied successfully.
echo,
pause
exit

:PROCESS
setlocal EnableDelayedExpansion
set HOST_FILE=%SystemRoot%\System32\drivers\etc\hosts
set TEMP_FILE=%TEMP%\hosts.tmp
del "%TEMP_FILE%" 2>nul 
set found_anyland_dns=false
for /f "delims=" %%i in (%HOST_FILE%) do (
    echo %%i | findstr /C:"d26e4xubm8adxu.cloudfront.net" >nul
    if !errorlevel! equ 0 (
        echo # %%i >> "%TEMP_FILE%"
    ) else (
        echo %%i | findstr /C:"d6ccx151yatz6.cloudfront.net" >nul
        if !errorlevel! equ 0 (
            echo # %%i >> "%TEMP_FILE%"
        ) else (
            echo %%i | findstr /C:"app.anyland.com" >nul
            if !errorlevel! equ 0 (
                echo # %%i >> "%TEMP_FILE%"
            ) else (
                echo %%i >> "%TEMP_FILE%"
            )
        )
    )
    echo %%i | findstr /C:"####ANYLAND-DNS####" >nul
    if !errorlevel! equ 0 (
        set found_anyland_dns=true
        echo %VARIABLE% d26e4xubm8adxu.cloudfront.net >> "%TEMP_FILE%"
        echo %VARIABLE% d6ccx151yatz6.cloudfront.net >> "%TEMP_FILE%"
        echo %VARIABLE% app.anyland.com >> "%TEMP_FILE%"
    )
)
if !found_anyland_dns! equ false (
    echo ####ANYLAND-DNS#### >> "%TEMP_FILE%"
    echo %VARIABLE% d26e4xubm8adxu.cloudfront.net >> "%TEMP_FILE%"
    echo %VARIABLE% d6ccx151yatz6.cloudfront.net >> "%TEMP_FILE%"
    echo %VARIABLE% app.anyland.com >> "%TEMP_FILE%"
    echo #### BY AXSYS ##### >> "%TEMP_FILE%"
	
)
move /Y "%TEMP_FILE%" "%HOST_FILE%"
endlocal
GOTO:EOF

:LOGO
cls
echo,
echo    ______ _____            _                 _       ______ _   _  _____ 
echo    ^| ___ \  ___^|          ^| ^|               ^| ^|      ^|  _  \ \ ^| ^|/  ___^|
echo    ^| ^|_/ / ^|__ _ __  _   _^| ^| __ _ _ __   __^| ^|      ^| ^| ^| ^|  \^| ^|\ `--. 
echo    ^|    /^|  __^| '_ \^| ^| ^| ^| ^|/ _` ^| '_ \ / _` ^|      ^| ^| ^| ^| . ` ^| `--. \
echo    ^| ^|\ \^| ^|__^| ^| ^| ^| ^|_^| ^| ^| (_^| ^| ^| ^| ^| (_^| ^|      ^| ^|/ /^| ^|\  ^|/\__/ /
echo    \_^| \_\____/_^| ^|_^|\__, ^|_^|\__,_^|_^| ^|_^|\__,_^|      ^|___/ \_^| \_/\____/ 
echo                       __/ ^|                    ______                  
echo                      ^|___/                    ^|______^|                 
echo,
GOTO:EOF