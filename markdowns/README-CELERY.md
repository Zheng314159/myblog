
# Celery 在 Linux 下才正式支持 prefork
celery -A app.celery_worker.celery_app worker --loglevel=info -Q email

# solo 模式运行 worker（适合开发环境）
celery -A app.celery_worker.celery_app worker --loglevel=info -Q email --pool=solo

# 改用 eventlet/gevent 池（需要额外安装库）
pip install eventlet
celery -A app.celery_worker.celery_app worker --loglevel=info -Q email --pool=eventlet

pip install gevent
celery -A app.celery_worker.celery_app worker --loglevel=info -Q email --pool=gevent



