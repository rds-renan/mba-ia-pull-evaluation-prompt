"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

LANGCHAIN_HUB_PROMPT="leonanluppi/bug_to_user_story_v1"
PATH_SAVE_PROMPT="prompts/bug_to_user_story_v1.yml"

def pull_prompts_from_langsmith(client: Client):
    print("# Executando pull")
    prompt_template = client.pull_prompt(
        LANGCHAIN_HUB_PROMPT,
        dangerously_pull_public_prompt=True
    )

    print("# Preparando dados")
    system_prompt = ""
    user_prompt = ""
    name_prompt = prompt_template.metadata["lc_hub_repo"]

    for message in prompt_template.messages:
        if isinstance(message, SystemMessagePromptTemplate):
            system_prompt = message.prompt.template
        elif isinstance(message, HumanMessagePromptTemplate):
            user_prompt = message.prompt.template

    prompt_data = {
        name_prompt: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"]
        }
    }

    print("# Salvando prompt")
    return save_yaml(prompt_data, PATH_SAVE_PROMPT)


def main():
    """Função principal"""
    print_section_header("Pull de prompt do LangChain HUB", "~")

    if not check_env_vars(["LANGSMITH_ENDPOINT","LANGSMITH_API_KEY"]):
        return 1

    client = Client()
    if not pull_prompts_from_langsmith(client=client):
        return 1

    print("# Pronto, prompt salvo!")
    return 0
    

if __name__ == "__main__":
    sys.exit(main())
