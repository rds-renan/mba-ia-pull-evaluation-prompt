"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import re
from pathlib import Path

PROMP_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMP_KEY = "bug_to_user_story_v2"
PERSONA = re.compile(
    r"\b(voc[êe]\s+(é|e|ser[áa]|atua|age)|atue como|aja como|assuma o papel|seu papel [ée]|sua fun[çc][ãa]o [ée])",
    re.IGNORECASE,
)

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data():
    if not PROMP_FILE.exists():
            pytest.exit("Prompt não encontrado, não existe ou esta com nome errado, verifique!", returncode=1)

    try:
        prompt_loaded = load_prompts(str(PROMP_FILE))
    except Exception as error:
        pytest.exit(f"Não foi possivel carregar o prompt, erro: {error}")

    if PROMP_KEY not in prompt_loaded:
        pytest.exit(f"Arquivo sem o campo essencial: {PROMP_KEY}", returncode=1)

    return prompt_loaded[PROMP_KEY]


class TestPrompts:
    def test_prompt_is_valid(self, prompt_data):
        """Verifica se o prompt é valido para os testes"""
        assert prompt_data, "Template está vazio."


    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert prompt_data.get("system_prompt"), "system_prompt ausente ou vazio."


    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert PERSONA.search(prompt_data["system_prompt"])


    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        has_user_story = all(mentions in prompt_data["system_prompt"].lower() for mentions in ["como", "eu quero", "para que"])
        has_markdown = any(mentions in prompt_data["system_prompt"] for mentions in ["#", "**", "\n- "])

        assert has_user_story or has_markdown, "Falta exigir um formato de saida."

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt = prompt_data["system_prompt"].lower()
        exemplos = re.findall(r"(?<!por )exemplo\s*(?:\d+|:|>)", prompt)
        entradas = re.findall(r"(?:entrada|input|bug|relato)\s*:", prompt)
        saidas = re.findall(r"(?:sa[íi]da|output|user story|resposta)\s*:", prompt)

        assert len(exemplos) >= 2 or (len(entradas) >= 2 and len(saidas) >= 2), "Falta few-shot no prompt!"


    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        assert "TODO" not in prompt_data["system_prompt"]


    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        assert len(prompt_data['techniques_applied']) > 1, "Falta técnicas de prompt aplicadas! No mínimo duas"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])