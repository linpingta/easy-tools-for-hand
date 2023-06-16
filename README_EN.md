This repository contains several independent projects and scripts aimed at improving work efficiency. They may be extracted and separated into standalone projects when appropriate.

1. project_maker: Quickly generates the basic directory structure for Python/Scala projects.

        ./project_maker_py.sh -p test
        ./project_maker_scala.sh -p test

2. fabfile.py: Based on fabric, it stores commonly used command operations, including Git commands and remote directory operations.

        fab git_commit # Commit Git changes
        fab scp_from_remote / scp_to_remote # Remote file copy

3. template_maker: Facilitates rapid code templating, based on Jinja2. It is primarily used for generating commonly used offline model and data monitoring scripts in the workplace.

        usage: base_maker [-h] [-t TEMPLATES] [-c CONFPATH]

        template maker

        optional arguments:
        -h, --help show this help message and exit
        -t TEMPLATES, --templates TEMPLATES
        template names to make, should be defined as a section
        name in conf, and have a related file in the templates/
        folder
        -c CONFPATH, --confpath CONFPATH
        configuration path for template detail info

        example:
          python base_maker.py -t base_template1.py,base_template2.py
          python base_maker.py -t templates/base_template.py -c conf/marker.conf
          python base_maker.py -t templates/base_template.py
          python base_maker.py -t base_template.py -c conf/marker.conf
          python base_maker.py -t base_template

4. model_trainer: Provides a basic framework for machine learning projects. It was used in my participation in the Kaggle competition.

5. task_manager: Schedules offline tasks and executes database tasks and user-defined tasks based on a Directed Acyclic Graph (DAG).

        Adding tasks
        python bin/add_task.py # Add a single task
        python bin/suite_example.py # Add a task suite

        Execute the added tasks
        python bin/task_manager.py

6. exp_manager: A service class for experiment management with support for elegant experiment management and custom log formatting.

        with ExpManager("Mock") as (exp, logger):
            from collections import OrderedDict
            user_info = OrderedDict(user_id=1, account_id=123, campaign_id=1234)
            if exp and exp.has_user(user_info):
                # Main logic
                print('user exists in exp')
                logger.debug('user_id[%d] account_id[%d] campaign_id[%d] participate exp' % tuple(user_info.values()))
            else:
                print('user not exists in exp')
                logger.debug('user_id[%d] account_id[%d] campaign_id[%d] dont participate exp' % tuple(user_info.values()))

7. custom_manager: A class for customized parameter settings, used for user-specific processing.

        CustomSettingManager.load(xml_filename, logger)
        user_setting_dict = CustomSettingManager.get_user_in_custom_setting(user_id, 'STATUS', logger)

8. task_monitor: Service monitoring that customizes actual monitoring by inheriting from MonitorTask.

        ./general_start.sh # Run the monitor once
        ./crontab_start.sh # Run the monitor according to the crontab time

9. offline_model_manager: Manages offline models and file reading.

        BasicModel: Basic offline model
        BasicModelManager: Manages offline models
        ModelReader: Reads offline models into the online policy system
        reporter: Provides visualization capabilities by using matplotlib to generate charts from DataFrame data and automatically outputs them as PDF files.

        python reporter.py # Outputs the result to output/test.pdf

10. interest_recommend: Constructs the base classes and methods for analyzing Hive data and applies them to interest recommendation.

        python interest_recommend_cf.py --train --no-train-reload --interests "ABC" --max_interest_num 10

11. pprint.py: Prints dictionaries, sourced from the scikit-learn library.

12. nlp_scel: Parses Sogou language corpus scel files (source code obtained from the internet).

13. nlp_lda
