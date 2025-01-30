from setuptools import setup, find_packages

setup(
    name="autoclicker",  # Replace with your project name
    version="0.1",
    packages=find_packages(where="src"),  # Automatically finds all packages under src/
    package_dir={"": "src"},  # Tells setuptools that packages are under src
    install_requires=[  # List any external dependencies here
        'comtypes==1.4.9',
        'numpy==2.2.1',
        'opencv-python==4.11.0.86',
        'pandas==2.2.3',
        'pillow==11.1.0',
        'pynput==1.7.7',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.2',
        'pywin32==308',
        'pywinauto==0.6.9',
        'scapy==2.6.1',
        'setuptools==75.8.0',
        'six==1.17.0',
        'tzdata==2024.2'
    ],
    include_package_data=True,  # To include files like README, etc.
)
