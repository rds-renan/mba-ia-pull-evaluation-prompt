"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

from pprint import pp

load_dotenv()

PATH_PROMPT = "prompts/bug_to_user_story_v2.yml"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("user", prompt_data["user_prompt"]),
    ])

    try:
        url = Client().push_prompt(
            prompt_name,
            object=prompt,
            is_public=True,
            description=prompt_data.get("description", ""),
            tags=prompt_data.get("tags", []),
        )
    except Exception as error:
        print(f"# Falha no push: {error}")
        return False

    print(f"# Publicado em: {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data=prompt_data)


def main():
    """Função principal"""
    print_section_header("Push de prompts otimizados ao LangSmith Prompt Hub", "~")

    if not check_env_vars(["LANGSMITH_ENDPOINT","LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    user_name = os.environ["USERNAME_LANGSMITH_HUB"]
    prompt_name = "bug_to_user_story_v2"

    print("# Carregando prompt...")
    prompt = load_yaml(PATH_PROMPT)
    if not prompt:
        return 1

    print("# Validando prompt")
    prompt_data = prompt[prompt_name]
    is_valid, faults = validate_prompt(prompt_data=prompt_data)
    if not is_valid:
        print("# Ops, prompt inválido.")
        for fault in faults:
            print(f"   - {fault}")
        return 1

    print(f"# Enviando {prompt_name} para LangSmith HUB")
    if not push_prompt_to_langsmith(f"{user_name}/{prompt_name}", prompt_data):
        return 1

    print("# Pronto, prompt publicado!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
