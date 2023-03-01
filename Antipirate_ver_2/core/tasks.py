# from celery import shared_task
# from celery.utils.log import get_task_logger
#
# from core.models import Core
#
# logger = get_task_logger(__name__)
#
#
# @shared_task
# def parsing_task():
#     """Empty task which runs every minute. Nothing really happens just printing text.
#     Execution depends on the Core object, if is_running = True, task prints text,
#      otherwise does nothing"""
#     core = Core.objects.first()
#     if core.is_running and core.parse_period == Core.PeriodChoices.EVERY_HOUR:
#         logger.info("The core is running and parsing is executed.")
#
#
# @shared_task
# def parsing_task_every_3_hours():
#     core = Core.objects.first()
#     if core.is_running and core.parse_period == Core.PeriodChoices.THREE_HOURS:
#         print(core.parse_period)
#         print(Core.PeriodChoices.THREE_HOURS)
#         logger.info("every three hours")
#
#
# @shared_task
# def parsing_task_every_6_hours():
#     core = Core.objects.first()
#     if core.is_running and core.parse_period == Core.PeriodChoices.SIX_HOURS:
#         logger.info("every six hours")
#
#
# @shared_task
# def parsing_task_once_a_day():
#     core = Core.objects.first()
#     if core.is_running and core.parse_period == Core.PeriodChoices.ONCE_A_DAY:
#         logger.info("once a day")
#
#
# @shared_task
# def parsing_task_once_a_week():
#     core = Core.objects.first()
#     if core.is_running and core.parse_period == Core.PeriodChoices.ONCE_A_WEEK:
#         logger.info("once a week")
