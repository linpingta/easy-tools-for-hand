{% extends 'base_template.py' %}

{% block ext_import %}
basepath = os.path.abspath(os.path.dirname(sys.path[0]))
sys.path.append(os.path.join(basepath, 'lib'))

from sender.email_sender import EmailSender
from task.{{ lib_model_name }} import {{ lib_model_capital_name }}
{% endblock ext_import %}

{% block main %}
    email_sender = EmailSender(conf, '{{model_name}}')
    mt = {{ lib_model_capital_name }}(email_sender, 'campaign', 60, 1, '{{ lib_model_capital_name }}')
    mt.init(conf, logger)
    try:
    	now = time.localtime()
        mt.run(now, logger)
    except Exception as e:
        logger.exception(e)
    finally:
        mt.release(logger)
{% endblock main %}
