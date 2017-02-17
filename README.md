# tools

这里保存了一些独立的项目和脚本，像项目名称所表示的，它们是用于提高工作效率而开发的，并且可能会在适当的时候被提取划分为独立的项目。

1. project_maker ：快速生成python/scala常用项目的基本目录结构

          ./project_maker_py.sh -p test
          ./project_maker_scala.sh -p test
    
2. fabfile.py ：基于[fabric](http://www.fabfile.org/)，保存常用的操作命令，包括git命令和远程目录操作

          fab git_commit  # 提交git
          fab scp_from_remote / scp_to_remote # 远程拷贝
    
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

			# 添加任务
			python bin/add_task.py # 添加单个任务
			python bin/suite_example.py # 添加任务组
		
			# 执行被添加的任务
			python bin/task_manager.py
		
6. exp_manager ：实验服务类，支持优雅的实验管理和日志定制

	        with ExpManager("Mock") as (exp, logger):
	   
           	    from collections import OrderedDict
           	    user_info = OrderedDict(user_id=1, account_id=123, campaign_id=1234)
           	    if exp and exp.has_user(user_info):
               		# main logic
               		print 'user exists in exp'
               		logger.debug('user_id[%d] account_id[%d] campaign_id[%d] participate exp' % tuple(user_info.values()))
		        else:
               		print 'user not exists in exp'
               		logger.debug('user_id[%d] account_id[%d] campaign_id[%d] dont participate exp' % tuple(user_info.values()))
	      
7. custom_mamager  : 参数定制类, 用于用户特殊处理

          	CustomSettingManager.load(xml_filename, logger)
           	user_setting_dict = CustomSettingManager.get_user_in_custom_setting(user_id,'STATUS', logger)
	  
8. task_monitor： 服务监控，继承MonitorTask定制实际的监控

	   	./general_start.sh # for monitor run once
	   	./crontab_start.sh # for monitor run in crontab time
	 
9. offline_model_manager: 离线模型和读取文件

		BasicModel: 基本离线模型
		BasicModelManager: 对离线模型的调用
		ModelReader：读取离线模型到在线策略系统
		
10. reporter： 可视化，将DataFrame数据通过matplotlib绘制成图表后，以pdf形式自动输出

		python reporter.py # 结果在output/test.pdf中输出

11. interest_recommend: 构建hive数据分析的基础类和方法 base_model,并将其应用于兴趣推荐上

        python interest_recommend_cf.py --train --no-train-reload --interests "ABC" --max_interest_num 10

12. pprint.py: 打印dict，来自scikit-learn源码
