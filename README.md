# Library API
## Description:
A RESTful API for a library using DRF. This API allows users to manage accounts, books, borrowings and receive telegram notifications.

## Features:
### User Functionality
* User registration with email and password.
* Users can retrieve and update their accounts.
* Authentication using JWT.
### Book Functionality:
* Everyone can view the books available in the library.
* Admin users can perform CRUD operations with books.
### Borrowing Functionality
* Authenticated users can create a borrowing with automatic book inventory reduction by 1.
* Authenticated users can see all their borrowings and retrieve specific ones with detailed book information.
* Authenticated users can filter their borrowings by their activity status.
* Admin users can filter borrowings by user_id.
* Authenticated users can return their borrowing with automatic book inventory increase by 1.
### Telegram Bot Functionality
* Users can link their library profile to telegram chat.
* After successful linking, they will receive detailed messages when a new borrowing is created.
### API Documentation:
* The API includes a Swagger interface with all endpoints.

## How to Run Using Docker
You need to have Docker installed.
- Copy .env.sample file & populate it with the necessary data.
- Run `docker-compose up --build`
- Create admin user:
```shell
docker ps # copy drf-library-api-library container ID
docker exec -it <container id> sh
python manage.py createsuperuser
```
