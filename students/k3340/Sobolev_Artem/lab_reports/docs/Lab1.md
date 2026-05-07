# Отчет по лабораторной работе №1. Реализация серверного приложения FastAPI

## Цели

Научится реализовывать полноценное серверное приложение с помощью фреймворка FastAPI с применением дополнительных средств и библиотек.

## Задание

Создать веб-приложение, которое позволит пользователям обмениваться книгами между собой. 
Это приложение должно облегчать процесс обмена книгами, позволяя пользователям находить книги, которые им интересны, 
и находить новых пользователей для обмена книгами. Функционал веб-приложения должен включать следующее:

- Создание профилей: Возможность пользователям создавать профили, указывать информацию о себе, своих навыках, опыте работы и предпочтениях по проектам. 
- Добавление книг в библиотеку: Пользователи могут добавлять книги, которыми они готовы поделиться, в свою виртуальную библиотеку на платформе. 
- Поиск и запросы на обмен: Функционал поиска книг в библиотеке других пользователей. Возможность отправлять запросы на обмен книгами другим пользователям. 
- Управление запросами и обменами: Возможность просмотра и управления запросами на обмен. Возможность подтверждения или отклонения запросов на обмен.

## Реализация

### Модели данных

#### 1. `Genre`

Поля и ограничения:

- `id: int` - первичный ключ
- `title: String(64)` - обязательное поле, `NOT NULL`
- `description: Text` - необязательное поле, `NULL`
- `slug: String(128)` - обязательное поле, `NOT NULL`, `UNIQUE`
- `created_by: UUID` - необязательное поле
- `updated_by: UUID` - необязательное поле
- `created_at: datetime` - обязательное поле, дата создания
- `updated_at: datetime` - обязательное поле, дата обновления

Назначение: хранение жанров книг.

#### 2. `Author`

Поля и ограничения:

- `id: int` - первичный ключ
- `name: String(80)` - обязательное поле, `NOT NULL`
- `slug: String(80)` - обязательное поле, `NOT NULL`, `UNIQUE`
- `created_at: datetime` - обязательное поле, дата создания
- `updated_at: datetime` - обязательное поле, дата обновления

Назначение: хранение информации об авторах книг.

#### 3. `Book`

Поля и ограничения:

- `id: int` - первичный ключ
- `title: String(128)` - обязательное поле, `NOT NULL`
- `description: Text` - необязательное поле
- `slug: String(128)` - обязательное поле, `NOT NULL`, `UNIQUE`
- `genre_id: int` - обязательное поле, `NOT NULL`, внешний ключ
- `created_at: datetime` - обязательное поле, дата создания
- `updated_at: datetime` - обязательное поле, дата обновления

Назначение: хранение информации о книгах.

#### 4. `User`

Поля и ограничения:

- `id: int` - первичный ключ
- `username: String(80)` - обязательное поле, `NOT NULL`, `UNIQUE`
- `password: String(255)` - обязательное поле, `NOT NULL`
- `email: String(255)` - необязательное поле, `NULL`, `UNIQUE`
- `role: String(16)` - обязательное поле, `NOT NULL`
- `active: Boolean` - обязательное поле, `NOT NULL`
- `created_at: datetime` - обязательное поле, дата создания
- `updated_at: datetime` - обязательное поле, дата обновления

Назначение: хранение учетных данных пользователя и информации для авторизации.

### 5. `Profile`

Поля и ограничения:

- `id: int` - первичный ключ
- `user_id: int` - обязательное поле, `NOT NULL`, `UNIQUE`, внешний ключ
- `full_name: String(120)` - необязательное поле
- `bio: Text` - необязательное поле
- `skills: Text` - необязательное поле
- `work_experience: Text` - необязательное поле
- `project_preferences: Text` - необязательное поле
- `created_at: datetime` - обязательное поле, дата создания
- `updated_at: datetime` - обязательное поле, дата обновления

Назначение: хранение данных публичного и расширенного профиля пользователя.

#### 6. `UserBook`

Поля и ограничения:

- `id: int` - первичный ключ
- `owner_id: int` - обязательное поле, `NOT NULL`, внешний ключ
- `book_id: int` - обязательное поле, `NOT NULL`, внешний ключ
- `is_available: Boolean` - обязательное поле, `NOT NULL`
- `created_at: datetime` - обязательное поле, дата создания

#### 7. `ExchangeRequest`

Поля и ограничения:

- `id: int` - первичный ключ
- `requester_id: int` - обязательное поле, `NOT NULL`, внешний ключ 
- `owner_id: int` - обязательное поле, `NOT NULL`, внешний ключ
- `user_book_id: int` - обязательное поле, `NOT NULL`, внешний ключ 
- `status: String(16)` - обязательное поле, `NOT NULL`
- `message: Text` - необязательное поле
- `created_at: datetime` - обязательное поле, дата создания
- `updated_at: datetime` - обязательное поле, дата обновления

Назначение: хранение заявок на обмен книгами между пользователями.

## Связи между моделями

- `Genre -> Book`: связь один-ко-многим
- `Book <-> Author`: связь многие-ко-многим через `book_authors`
- `User -> Profile`: связь один-к-одному
- `User -> UserBook`: связь один-ко-многим
- `UserBook -> ExchangeRequest`: связь один-ко-многим
- `ExchangeRequest` связывает владельца книги и пользователя, отправившего запрос на обмен

## Эндпоинты

### Аутентификация и авторизация

- `POST /api/v1/auth/register` - регистрация пользователя
- `POST /api/v1/auth/login` - вход пользователя
- `POST /api/v1/auth/token` - получение JWT-токена
- `GET /api/v1/auth/users/me` - получение данных текущего пользователя
- `POST /api/v1/auth/refresh` - обновление access token

### Жанры

- `GET /api/v1/genres/` - получить список жанров
- `GET /api/v1/genres/{genre_id}` - получить жанр по идентификатору
- `POST /api/v1/genres/` - создать жанр
- `PATCH /api/v1/genres/{genre_id}` - обновить жанр
- `DELETE /api/v1/genres/{genre_id}` - удалить жанр

### Авторы

- `GET /api/v1/authors/` - получить список авторов
- `GET /api/v1/authors/{author_id}` - получить автора по идентификатору
- `GET /api/v1/authors/{slug}` - получить автора по slug
- `POST /api/v1/authors/` - создать автора
- `PATCH /api/v1/authors/{author_id}` - обновить автора
- `DELETE /api/v1/authors/{author_id}` - удалить автора

### Книги

- `GET /api/v1/books/` - получить список книг
- `GET /api/v1/books/{book_id}` - получить книгу по идентификатору
- `POST /api/v1/books/` - создать книгу
- `PATCH /api/v1/books/{book_id}` - обновить книгу
- `DELETE /api/v1/books/{book_id}` - удалить книгу

### Пользователи

- `GET /api/v1/users/` - получить список пользователей с возможностью поиска
- `GET /api/v1/users/me` - получить данные текущего пользователя и его профиля
- `PATCH /api/v1/users/me` - обновить данные аккаунта текущего пользователя
- `PATCH /api/v1/users/me/password` - изменить пароль текущего пользователя
- `GET /api/v1/users/{user_id}` - получить публичные данные пользователя

### Профили

- `GET /api/v1/profiles/me` - получить профиль текущего пользователя
- `PATCH /api/v1/profiles/me` - обновить профиль текущего пользователя
- `GET /api/v1/profiles/{user_id}` - получить профиль пользователя по идентификатору

### Библиотека пользователя

- `GET /api/v1/library/` - поиск по библиотеке пользователей
- `GET /api/v1/library/me` - получить свою библиотеку
- `GET /api/v1/library/{user_book_id}` - получить запись библиотеки по идентификатору
- `POST /api/v1/library/` - добавить книгу в свою библиотеку
- `PATCH /api/v1/library/{user_book_id}` - изменить доступность книги
- `DELETE /api/v1/library/{user_book_id}` - удалить книгу из своей библиотеки

### Заявки на обмен

- `GET /api/v1/exchange-requests/` - получить список заявок пользователя
- `GET /api/v1/exchange-requests/{request_id}` - получить детали заявки
- `POST /api/v1/exchange-requests/` - создать заявку на обмен
- `PATCH /api/v1/exchange-requests/{request_id}/status` - изменить статус заявки
- `DELETE /api/v1/exchange-requests/{request_id}` - удалить заявку

## Аутентификация

Аутентификация реализована на основе JWT. Реализовано:

- регистрация и вход пользователя
- создание `access token` и `refresh token`
- проверка типа токена
- получение текущего пользователя из токена
- проверка активности пользователя
- проверка роли администратора

## Код соединения с БД

Подключение к БД:

```python
class DatabaseHelper:
    def __init__(
        self,
        url: str,  # URL
        echo: bool = False,  # логирование SQL-запросов
        echo_pool: bool = False,  # логирование запросов к пулу соединений
        max_overflow: int = 10,  # Максимальное количество соединений, которое может быть создано сверх pool_size
        pool_size: int = 10,  # Размер пула соединений
    ):
        # Асинхронный движок SQLAlchemy для работы с базой данных
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            max_overflow=max_overflow,
            pool_size=pool_size,
        )
        
        # Фабрика сессий для асинхронного использования
        self.sessiong_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,  
            autoflush=False, 
            autocommit=False, 
            expire_on_commit=False, 
        )

    # Асинхронный метод для освобождения всех ресурсов движка
    async def dispose(self) -> None:
        await self.engine.dispose() 

    # Асинхронный генератор для получения сессии
    async def sessiong_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.sessiong_factory() as session:  
            yield session 

db_helper = DatabaseHelper(
    url=str(settings.db.url),  
    echo=settings.db.echo, 
    echo_pool=settings.db.echo_pool, 
    max_overflow=settings.db.max_overflow,  
    pool_size=settings.db.pool_size,
)
```

Конфигурация:`

```python
class DataBaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 50

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
```

## Ссылки на работы

- [Практика 1](https://github.com/Artsobol/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab1/students/k3340/Sobolev_Artem/Lr1/Practive1)
- [Практика 2](https://github.com/Artsobol/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab1/students/k3340/Sobolev_Artem/Lr1/Practive2)
- [Практика 3](https://github.com/Artsobol/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab1/students/k3340/Sobolev_Artem/Lr1/Practive3)
- [Лабораторная работа](https://github.com/Artsobol/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/lab1/students/k3340/Sobolev_Artem/Lr1/Lab1)