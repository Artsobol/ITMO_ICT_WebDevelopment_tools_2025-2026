from pydantic import Field, HttpUrl

from api.api_v1.schemas.base import Base


class ParserRequest(Base):
    url: HttpUrl = Field(
        title="URL страницы книги",
        description="Адрес страницы, которую нужно передать сервису парсинга.",
    )


class ParserResponse(Base):
    message: str = Field(title="Сообщение", description="Статус выполнения парсинга.")
    title: str = Field(title="Название книги", description="Название книги, извлечённое парсером.")
    genre: str = Field(title="Жанр", description="Жанр книги, извлечённый парсером.")
    created: bool = Field(
        title="Книга создана",
        description="`true`, если книга была добавлена в базу впервые.",
    )


class ParserTaskAcceptedResponse(Base):
    task_id: str = Field(title="Идентификатор задачи", description="Идентификатор задачи Celery.")
    status: str = Field(title="Статус", description="Текущий статус задачи в очереди.")
    message: str = Field(title="Сообщение", description="Информация о постановке задачи в очередь.")


class ParserTaskStatusResponse(Base):
    task_id: str = Field(title="Идентификатор задачи", description="Идентификатор задачи Celery.")
    status: str = Field(title="Статус", description="Текущий статус задачи Celery.")
    ready: bool = Field(title="Готовность", description="Признак завершения задачи.")
    successful: bool = Field(title="Успешность", description="Признак успешного завершения задачи.")
    result: ParserResponse | None = Field(
        default=None,
        title="Результат",
        description="Результат парсинга, если задача успешно завершена.",
    )
    error: str | None = Field(
        default=None,
        title="Ошибка",
        description="Текст ошибки, если задача завершилась неуспешно.",
    )
