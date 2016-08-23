# tools

这里保存了一些独立的项目和脚本，像项目名称所表示的，它们是用于提高工作效率而开发的，并且可能会在适当的时候被提取划分为独立的项目。

1. project_maker.sh ：快速生成python常用项目的基本目录结构
2. fabfile.py ：基于[fabric](http://www.fabfile.org/)，保存常用的操作，包括git命令和远程目录操作
3. template_maker ： 用于模板信息的快速填充，基础基于[Jinja2](http://jinja.pocoo.org/)，主要是在工作中常用的离线模型和数据监控脚本自动生成
4. model_trainer ：用于machine learning项目的基本框架，我在参加[Kaggle竞赛](https://www.kaggle.com/c/shelter-animal-outcomes)中使用了[它](https://github.com/linpingta/shelter-animal-outcome)
5. task_manager ： 用于离线任务的调度，基于DAG执行db任务和用户定义任务

