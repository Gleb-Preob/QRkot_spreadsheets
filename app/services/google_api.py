from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings

# Константа с форматом строкового представления времени
FORMAT = "%Y/%m/%d %H:%M:%S"
LOCALE = 'ru_RU'


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    # Дата для заголовка документа
    now_date_time = datetime.now().strftime(FORMAT)

    service = await wrapper_services.discover('sheets', 'v4')

    spreadsheet_body = {
        'properties': {'title': f'Отчёт на {now_date_time}',
                       'locale': LOCALE},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист1',
                                   'gridProperties': {'rowCount': 50,
                                                      'columnCount': 3}}}]
    }

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheetid = response['spreadsheetId']
    return spreadsheetid


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheetid: str,
        closed_projects: list,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    # Тело таблицы
    table_values = [
        ['Отчёт от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    # Добавляются строчки с данными из запроса
    for project in closed_projects:
        new_row = [
            str(project.name),
            str(project.close_date - project.create_date),
            str(project.description)
        ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range='A1:C50',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
