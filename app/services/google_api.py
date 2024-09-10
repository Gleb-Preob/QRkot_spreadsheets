from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings

# Константа с форматом строкового представления времени
FORMAT = "%Y/%m/%d %H:%M:%S"
LOCALE = 'ru_RU'
SHEET_TITLE = 'Отчёт от {}'

SHEET_WRITING_ZONE = [
    {'properties': {
        'sheetType': 'GRID',
        'sheetId': 0,
        'title': 'Лист1',
        'gridProperties': {'rowCount': 50, 'columnCount': 3}
    }}
]

PERMISSION_BODY = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.email
}

TABLE_VALUES_FROM_SECOND_ROW = [
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]

UPDATE_BODY = {
    'majorDimension': 'ROWS',
    'values': None
}


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    # Дата для заголовка документа
    now_date_time = datetime.now().strftime(FORMAT)

    service = await wrapper_services.discover('sheets', 'v4')

    spreadsheet_body = {
        'properties': {
            'title': SHEET_TITLE.format(now_date_time),
            'locale': LOCALE
        },
        'sheets': SHEET_WRITING_ZONE
    }

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover('drive', 'v3')

    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=PERMISSION_BODY,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        closed_projects: list,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    # Тело таблицы
    table_values = [['Отчёт от', now_date_time]] + TABLE_VALUES_FROM_SECOND_ROW
    # Добавляются строчки с данными из запроса
    for project in closed_projects:
        new_row = [
            str(project.name),
            str(project.close_date - project.create_date),
            str(project.description)
        ]
        table_values.append(new_row)

    UPDATE_BODY['values'] = table_values
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:C50',
            valueInputOption='USER_ENTERED',
            json=UPDATE_BODY
        )
    )
