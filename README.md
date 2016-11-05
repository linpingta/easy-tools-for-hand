# tools

这里保存了一些独立的项目和脚本，像项目名称所表示的，它们是用于提高工作效率而开发的，并且可能会在适当的时候被提取划分为独立的项目。

1. project_maker ：快速生成python/scala常用项目的基本目录结构

    ./project_maker_py.sh -p test
    
    ./project_maker_scala.sh -p test
    
2. fabfile.py ：基于[fabric](http://www.fabfile.org/)，保存常用的操作命令，包括git命令和远程目录操作

    fab git_commit
    
    fab scp_from_remote / scp_to_remote
    
3. template_maker ： 用于模板代码的快速填充，基础基于[Jinja2](http://jinja.pocoo.org/)，主要用于生成工作中常用的离线模型和数据监控脚本

    usage: base_maker [-h] [-t TEMPLATES] [-c CONFPATH]

    template maker

    optional arguments:
      -h, --help            show this help message and exit
      -t TEMPLATES, --templates TEMPLATES
                            template names to make, should be defined as section
                            name in conf, and have related file in templates/
                            folder
      -c CONFPATH, --confpath CONFPATH
                            configuration path for template detail info

    example:
                        python base_maker.py -t base_template1.py,base_template2.py
                        python base_maker.py -t templates/base_template.py -c conf/marker.conf
                        python base_maker.py -t templates/base_template.py 
                        python base_maker.py -t base_template.py -c conf/marker.conf
                        python base_maker.py -t base_template

4. model_trainer ：用于machine learning项目的基本框架，我在参加[Kaggle竞赛](https://www.kaggle.com/c/shelter-animal-outcomes)中使用了[它](https://github.com/linpingta/shelter-animal-outcome)
5. task_manager ： 用于离线任务的调度，基于DAG执行db任务和用户定义任务
6. exp_manager ：服务中使用的实验嵌入
7. custom_mamager  : 服务中的参数配置
8. task_monitor： 服务监控
9. offline_model_manager: 离线模型和读取文件
10. reporter： 报表

