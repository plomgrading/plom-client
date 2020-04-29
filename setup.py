import os
from setuptools import setup, find_packages
from glob import glob

with open("README.md", "r") as fh:
    long_description = fh.read()

# This directory
dir_setup = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_setup, "plom", "version.py")) as f:
    # Defines __version__
    exec(f.read())

iconList = []
for fn in glob("plom/client/icons/*.svg"):
    iconList.append(fn)
cursorList = []
for fn in glob("plom/client/cursors/*.png"):
    cursorList.append(fn)

client_install_requires = ["toml>=0.10.0", "requests", "requests-toolbelt", "PyQt5"]

server_install_requires = [
    "toml>=0.10.0",
    "tqdm",
    "pandas",
    "passlib",
    "pymupdf>=1.16.14",
    "Pillow",
    "cffi",  # not ours, why doesn't jpegtran-cffi pull this?
    "jpegtran-cffi",
    "weasyprint",
    "aiohttp",
    "pyqrcode",
    "pyzbar",
    "peewee",
    "imutils",
    "opencv-python",
    "tensorflow>=2",
    "lapsolver",  # ID reading
    "PyQt5",
    "requests",  # b/c of deprecated userManager
]

# Non-Python deps for server
#   - imagemagick
#   - ghostscript (optional)
#   - latex installation including (Debian/Ubuntu pkg names):
#       texlive-latex-extra dvipng latexmk texlive-fonts-recommended
#   - latex installation including (Fedora pkg names):
#       tex-preview tex-dvipng texlive-scheme-basic tex-xwatermark tex-charter


setup(
    name="plom",
    version=__version__,
    description="Plom is PaperLess Open Marking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://plomgrading.org",
    author="Andrew Rechnitzer",
    license="AGPLv3+",
    python_requires=">=3.6",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Topic :: Education :: Testing",
    ],
    entry_points={
        "console_scripts": [
            "plom-client=plom.scripts.client:main",
            "plom-demo=plom.scripts.demo:main",
            "plom-init=plom.scripts.plominit:main",
            "plom-build=plom.scripts.build:main",
            "plom-server=plom.scripts.server:main",
            "plom-scan=plom.scripts.scan:main",
            "plom-manager=plom.scripts.manager:main",
            "plom-finish=plom.scripts.finish:main",
            "plom-fake-scribbles=plom.produce.faketools:main",
            "plom-hwscan=plom.scripts.hwscan:main",
        ],
    },
    include_package_data=True,
    data_files=[
        (
            "share/plom",
            [
                "plom/templateTestSpec.toml",
                "plom/produce/digits.json",
                "plom/serverDetails.toml",
                "plom/templateUserList.csv",
                "plom/demoClassList.csv",
                "plom/demoUserList.csv",
                "plom/server/target_Q_latex_plom.png",
                "plom/testTemplates/latexTemplate.tex",
                "plom/testTemplates/latexTemplatev2.tex",
                "plom/testTemplates/idBox2.pdf",
                "plom/client/backGrid1.svg",
                "plom/client/backGrid2.png",
            ],
        ),
        ("share/plom/icons", iconList),
        ("share/plom/cursors", cursorList),
        ("share/applications", ["org.plomgrading.PlomClient.desktop"]),
        ("share/metainfo", ["org.plomgrading.PlomClient.appdata.xml"]),
        ("share/icons/hicolor/128x128/apps/", ["org.plomgrading.PlomClient.png"]),
    ],
    install_requires=list(set(client_install_requires + server_install_requires)),
)
