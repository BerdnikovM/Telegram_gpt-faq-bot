@echo off
REM Инициализация структуры проекта GPT-FAQ Bot

REM Папки верхнего уровня
mkdir app
mkdir app\handlers
mkdir app\keyboards
mkdir app\repositories
mkdir app\services

REM Пустые файлы
type nul > app\__init__.py
type nul > app\config.py
type nul > app\db.py
type nul > app\models.py
type nul > app\bot.py

REM Handlers
type nul > app\handlers\__init__.py
type nul > app\handlers\start.py
type nul > app\handlers\faq.py
type nul > app\handlers\ask.py
type nul > app\handlers\admin.py

REM Keyboards
type nul > app\keyboards\__init__.py
type nul > app\keyboards\reply.py
type nul > app\keyboards\faq_inline.py
type nul > app\keyboards\admin_inline.py

REM Repositories
type nul > app\repositories\__init__.py
type nul > app\repositories\faq_repo.py
type nul > app\repositories\user_repo.py
type nul > app\repositories\cache_repo.py
type nul > app\repositories\unanswered_repo.py
type nul > app\repositories\limits_repo.py

REM Services
type nul > app\services\__init__.py
type nul > app\services\faq_service.py
type nul > app\services\llm_provider.py
type nul > app\services\text_norm.py

REM Дополнительные файлы в корне
type nul > Dockerfile
type nul > docker-compose.yml
type nul > requirements.txt
type nul > README.md
type nul > .env.example
type nul > LICENSE

echo Структура проекта успешно создана!
pause
