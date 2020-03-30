from setuptools import setup, find_packages
from glob import glob

iconList = []
for fn in glob("plom/client/icons/*.svg"):
    iconList.append(fn)
cursorList = []
for fn in glob("plom/client/cursors/*.png"):
    cursorList.append(fn)

setup(
    name="plom",
    version="0.3.90",
    description="Paperless online marking",
    url="https://plom.gitlab.io/plom/",
    author="Andrew Rechnitzer",
    license="AGPL3",
    packages=find_packages(),
    scripts=[
        "plom/scripts/plom-init.py",
        "plom/scripts/plom-manager.py",
    ],
    entry_points={
        "console_scripts": [
            "plom-client=plom.scripts.client:main",
            "plom-build=plom.scripts.build:main",
            "plom-server=plom.scripts.server:main",
            "plom-scan=plom.scripts.scan:main",
            "plom-fake-scribbles=plom.produce.faketools:main",
        ],
    },
    include_package_data=True,
    data_files=[
        (
            "share/plom",
            [
                "plom/templateTestSpec.toml",
                "plom/serverDetails.toml",
                "plom/templateUserList.csv",
                "plom/demoClassList.csv",
                "plom/demoUserList.csv",
                "plom/server/target_Q_latex_plom.png",
                "plom/testTemplates/latexTemplate.tex",
                "plom/testTemplates/latexTemplatev2.tex",
                "plom/testTemplates/idBox2.pdf",
            ],
        ),
        ("share/plom/icons", iconList),
        ("share/plom/cursors", cursorList),
    ],
)
