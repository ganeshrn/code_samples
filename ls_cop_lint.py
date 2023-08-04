import os
import tempfile
import yaml

from copy import deepcopy
from ansiblelint.rules import RulesCollection
from ansiblelint.runner import Runner
from ansiblelint.constants import DEFAULT_RULESDIR
from ansiblelint.config import options as default_options
from ansiblelint.runner import LintResult, _get_matches
from ansiblelint.file_utils import Lintable
from ansiblelint.config import Options
from ansiblelint.transformer import Transformer
from pprint import pprint

completion = """---
- hosts: localhost
  tasks:
  - name: disable ufw service
    ansible.builtin.service:
      name: ufw
      enabled: false
      state: stopped
    when: '"ufw" in services'
"""


def run_linter(
    config_options: Options,
    default_rules_collection: RulesCollection,
    inline_completion: str,
) -> str:
    """Runs the Runner to populate a LintResult for a given snippet."""
    transformed_completion = inline_completion

    # create a temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".yml"
    ) as temp_file:
        # write the YAML string to the file
        temp_file.write(inline_completion)
        # get the path to the file
        temp_completion_path = temp_file.name

    config_options.lintables = [temp_completion_path]
    result = _get_matches(rules=default_rules_collection, options=config_options)
    # lintable = Lintable(temp_completion_path, kind="playbook")
    # result = Runner(lintable, rules=default_rules_collection).run()
    run_transform(result, config_options)

    # read the transformed file
    with open(temp_completion_path, "r", encoding="utf-8") as yaml_file:
        transformed_completion = yaml_file.read()

    # delete the temporary file
    os.remove(temp_completion_path)

    return transformed_completion


def run_transform(lint_result: LintResult, config_options: Options):
    transformer = Transformer(result=lint_result, options=config_options)
    transformer.run()


new_options = deepcopy(default_options)
new_options.write_list = ["all"]
transformed_completion = run_linter(
    new_options, RulesCollection(rulesdirs=[DEFAULT_RULESDIR]), completion
)
print(f"----Before----\n{completion}")
print(f"\n----After----\n{transformed_completion}")

# rules = RulesCollection(rulesdirs=[DEFAULT_RULESDIR], options=new_options)
# rules.register()
# results = Runner(test_suggestion, rules=rules).run()
# print(results)
