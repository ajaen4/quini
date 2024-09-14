from f_data_uploader.services import spreadsheets
from f_data_uploader.logger import logger


def create_tab(spreadsheet_id: str, matchday: str, data: list):
    requests = [{"addSheet": {"properties": {"title": matchday}}}]

    body = {"requests": requests}

    response = (
        spreadsheets.spreadsheets()
        .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )

    new_sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]
    logger.info(f"New Sheet ID: {new_sheet_id}")

    body = {"values": data}

    result = (
        spreadsheets.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=f"{matchday}!A1",
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )

    logger.info(f"{result.get('updatedCells')} cells updated")

    return new_sheet_id
