import PyInstaller.__main__
import version_update

version_update.Version()

PyInstaller.__main__.run([
    'main.spec'
])

