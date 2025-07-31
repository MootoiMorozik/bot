import os
import zipfile
import tempfile
import subprocess
from flask import Flask, request, render_template, redirect, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get('zipfile')

        if not file or file.filename == '':
            flash("Файл не выбран.")
            return redirect("/")

        if not file.filename.endswith(".zip"):
            flash("Поддерживаются только .zip файлы.")
            return redirect("/")

        # Создание временной папки
        temp_dir = tempfile.mkdtemp(prefix="bot_")
        zip_path = os.path.join(temp_dir, "bot.zip")
        file.save(zip_path)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            flash("Ошибка при распаковке ZIP.")
            return redirect("/")

        main_py = os.path.join(temp_dir, "main.py")
        if not os.path.isfile(main_py):
            flash("main.py не найден в архиве.")
            return redirect("/")

        try:
            subprocess.Popen(["python", "main.py"], cwd=temp_dir)
            flash("✅ Бот успешно запущен!")
        except Exception as e:
            flash(f"Ошибка запуска: {e}")

        return redirect("/")

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
