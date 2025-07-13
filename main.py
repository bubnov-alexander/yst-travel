import datetime as dt

import pytz
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.database.Migrations import migration
from app.handlers.callbacks.catamarans.addFSM import register_add_catamaran_handlers
from app.handlers.callbacks.catamarans.deleteFSM import register_delete_catamaran_handlers
from app.handlers.callbacks.catamarans.editFSM import register_edit_catamaran_handlers
from app.handlers.callbacks.logsCallback import register_callback_query_logs
from app.handlers.callbacks.settings import register_settings_handlers
from app.handlers.callbacks.sortByDate import register_selection_of_sorts_by_date
from app.handlers.callbacks.orders.findOrderByDateFSM import register_find_order_by_date_handlers
from app.handlers.callbacks.getSortsByDate import register_get_buttons_selection_of_sorts
from app.handlers.callbacks.orders.findOrderByIdFSM import register_find_order_by_id_handlers
from app.handlers.callbacks.getMonthCallback import register_callback_query_get_month_catamarans
from app.handlers.callbacks.getSortButtonsCallback import register_callback_query_get_sort_buttons_catamaran
from app.handlers.callbacks.orders.paginationCallback import register_callback_query_view_next_page_catamarans, \
    register_callback_query_view_back_page_catamarans
from app.handlers.callbacks.orders.searchFreeCallback import register_search_free_catamaran_handlers
from app.handlers.callbacks.orders.sortByDateCallback import register_callback_query_sort_by_date_catamaran, \
    register_callback_query_sort_by_month_catamaran
from app.handlers.callbacks.orders.viewCallback import register_callback_query_view_catamarans
from app.handlers.callbacks.closeCallback import register_callback_close_handlers, register_callback_query_close_button
from app.handlers.callbacks.excelCallback import register_callback_query_excel
from app.handlers.callbacks.orders.addFSM import register_add_order_handlers
from app.handlers.callbacks.orders.changeStatusFSM import register_change_status_catamaran_handlers
from app.handlers.callbacks.orders.deleteFSM import register_delete_order_handlers
from app.handlers.callbacks.orders.editFSM import register_edit_order_handlers
from app.handlers.callbacks.orders.serviceButtons import register_catamaran_callback, register_supboard_callback, \
    register_transfer_callback
from app.handlers.callbacks.route.SelectRoute import register_select_route_handler
from app.handlers.callbacks.route.addNewRoute import register_add_route_handlers
from app.handlers.callbacks.supboards.addFSM import register_add_supboard_handlers
from app.handlers.callbacks.supboards.deleteFSM import register_delete_supboard_handlers
from app.handlers.callbacks.supboards.editFSM import register_edit_supboard_handlers
from app.handlers.callbacks.transfers.addFSM import register_add_transfer_handlers
from app.handlers.callbacks.transfers.deleteFSM import register_delete_transfer_handlers
from app.handlers.callbacks.transfers.editFSM import register_edit_transfer_handlers
from app.handlers.callbacks.users.adminFSM import register_handle_add_admin, register_handle_delete_admin
from app.handlers.commands.getChatIdCommand import register_handlers_get_group_id
from app.handlers.commands.startCommand import register_handlers_start
from app.utils.logger import logger
from app.utils.middleware import CallbackLoggerMiddleware, MessageLoggerMiddleware
from config import TOKEN, TIMEZONE

# ============== Settings ==============
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

tz = pytz.timezone(TIMEZONE)


async def on_startup(_):
    await migration.db_start()
    TIME = dt.datetime.now(tz).strftime('%H:%M:%S')
    DATE = dt.datetime.now(tz).strftime('%d.%m')
    logger.info(f'Бот запущен: {TIME} {DATE}')


if __name__ == '__main__':
    register_handlers_start(dp)
    register_handlers_get_group_id(dp)

    register_callback_query_view_catamarans(dp)
    register_callback_query_view_next_page_catamarans(dp)
    register_callback_query_view_back_page_catamarans(dp)
    register_callback_query_sort_by_date_catamaran(dp)
    register_callback_query_get_month_catamarans(dp)
    register_callback_query_get_sort_buttons_catamaran(dp)
    register_callback_query_sort_by_month_catamaran(dp)
    register_callback_query_excel(dp)
    register_callback_close_handlers(dp, bot)
    register_select_route_handler(dp)

    register_catamaran_callback(dp)
    register_supboard_callback(dp)
    register_transfer_callback(dp)

    register_add_catamaran_handlers(dp)
    register_edit_catamaran_handlers(dp)

    register_add_order_handlers(dp, bot)
    register_delete_order_handlers(dp)

    register_add_supboard_handlers(dp)
    register_edit_supboard_handlers(dp)
    register_delete_supboard_handlers(dp)

    register_add_transfer_handlers(dp)
    register_edit_transfer_handlers(dp)
    register_delete_transfer_handlers(dp)

    register_get_buttons_selection_of_sorts(dp)
    register_selection_of_sorts_by_date(dp)

    register_edit_order_handlers(dp)
    register_delete_catamaran_handlers(dp)
    register_change_status_catamaran_handlers(dp, bot)
    register_search_free_catamaran_handlers(dp, bot)
    register_find_order_by_id_handlers(dp, bot)
    register_find_order_by_date_handlers(dp, bot)
    register_add_route_handlers(dp, bot)
    register_callback_query_close_button(dp)

    dp.middleware.setup(CallbackLoggerMiddleware())
    dp.middleware.setup(MessageLoggerMiddleware())

    register_handle_delete_admin(dp)
    register_handle_add_admin(dp)
    register_settings_handlers(dp)

    register_callback_query_logs(dp)

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
