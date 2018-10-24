Feature: Drone integration
    It will create `.drone.yml` file inside project to have integration with Drone IO. 

Scenario: Drone files successfully created
    Given I set up new micro service with drone support
    Then there should be created a file in <file_path> with <expected_content_filename>

    Examples:
        | file_path                   | expected_content_filename                |
        | .coveragerc                 | expected_coveragerc                      |
        | .drone.yml                  | expected_drone.yml                       |
        | .flake8                     | expected_flake8                          |
        | requirements/ci.txt         | expected_requirements_ci_txt_content.txt |
        | scripts/tcp-port-wait.sh    | expected_tcp-port-wait.sh                |
        | scripts/run-tests.sh        | expected_run-tests.sh                    |


Scenario: Expected messages for successfully created drone files
    Given I set up new micro service with drone support
    Then <expected_message> should be shown with <expected_color>

    Examples:
        | expected_message                                                                                                                | expected_color |
        | Drone CI support was successfully added. Make sure to configure the needed permissions in the Drone CI web administration panel | blue           |
