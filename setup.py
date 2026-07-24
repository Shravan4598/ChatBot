"""
setup.py

Package configuration for Production AI ChatBot.
"""

from setuptools import find_packages, setup
from typing import List


PROJECT_NAME = "ChatBot"

VERSION = "1.0.0"

AUTHOR = "Shravan Kumar Pandey"

AUTHOR_EMAIL = "shravankumarpandey825412@gmail.com"



def get_requirements() -> List[str]:
    """
    Read dependencies from requirements.txt
    """

    requirements_list: List[str] = []


    try:

        with open(
            "requirements.txt",
            "r"
        ) as file:


            requirements_list = [

                requirement.strip()

                for requirement in file.readlines()

                if requirement.strip()

                and not requirement.startswith("#")

            ]


    except FileNotFoundError:

        pass


    return requirements_list



setup(

    name=PROJECT_NAME,


    version=VERSION,


    author=AUTHOR,


    author_email=AUTHOR_EMAIL,


    description=(

        "Production AI Chatbot using "

        "LangGraph, LangChain, Gemini, "

        "RAG and AI Tools"

    ),


    packages=find_packages(),


    install_requires=get_requirements(),


    python_requires=">=3.11",


    include_package_data=True,


    classifiers=[

        "Programming Language :: Python :: 3",

        "Programming Language :: Python :: 3.11",

        "Framework :: Streamlit",

    ],

)