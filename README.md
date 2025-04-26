
# 🍽️ Recipe App API

Welcome to the **Recipe App API**! This is a **RESTful API** built with **Django REST Framework** that allows users to manage and access recipes and ingredients. 🍲 The API supports functionalities like adding, updating, deleting, and fetching recipes and ingredients. 

## 🚀 Features

- **Recipes Management**: Add, update, and delete recipes. 🥘
- **Ingredients Management**: Add, update, and delete ingredients. 🧂
- **Recipe-Ingredient Mapping**: Recipes can have multiple ingredients, and each ingredient can have a specific quantity per recipe. 🍴
- **User Authentication**: User authentication is handled via **JWT tokens**. 🔐
- **Permissions**: Users can only access data based on their assigned permissions. ✅

## 🛠️ Technologies Used

- **Django**: A powerful Python web framework. 🐍
- **Django REST Framework**: A toolkit for building Web APIs. 🌐
- **JWT Authentication**: For user login and authentication. 🔑
- **PostgreSQL**: Database to store recipes, ingredients, and user data. 🗃️

## 📋 Installation

### Prerequisites

- Python 3.6+ 🐍
- PostgreSQL (or any other preferred database) 📦
- pip (Python package installer) 📲

### Clone the repository

```bash
git clone https://github.com/ChRaviTeja1901/recipe-app-api.git
cd recipe-app-api
```

### Create a virtual environment and activate it

For Linux/MacOS:

```bash
python3 -m venv env
source env/bin/activate
```

For Windows:

```bash
python -m venv env
.\env\Scripts ctivate
```

### Install the dependencies

```bash
pip install -r requirements.txt
```

### Set up the database

1. **Create a PostgreSQL database** (or configure another database if needed). 🗄️
2. Update the `DATABASES` setting in `recipe_project/settings.py` with your database credentials.

### Migrate the database

```bash
python manage.py migrate
```

### Create a superuser (for accessing Django admin)

```bash
python manage.py createsuperuser
```

### Run the development server

```bash
python manage.py runserver
```

The application will be running at `http://127.0.0.1:8000/`. 🌍

## 📡 API Endpoints

### Authentication

- **POST** `/api/token/` - Obtain JWT token by providing username and password. 🔑
- **POST** `/api/token/refresh/` - Refresh JWT token. 🔄

### Recipes

- **GET** `/api/recipes/` - List all recipes. 🍲
- **POST** `/api/recipes/` - Create a new recipe. ✍️
- **GET** `/api/recipes/{id}/` - Get details of a specific recipe. 📋
- **PUT** `/api/recipes/{id}/` - Update a specific recipe. ✏️
- **DELETE** `/api/recipes/{id}/` - Delete a specific recipe. 🗑️

### Ingredients

- **GET** `/api/ingredients/` - List all ingredients. 🍅
- **POST** `/api/ingredients/` - Create a new ingredient. 🍽️
- **GET** `/api/ingredients/{id}/` - Get details of a specific ingredient. 📝
- **PUT** `/api/ingredients/{id}/` - Update a specific ingredient. ✂️
- **DELETE** `/api/ingredients/{id}/` - Delete a specific ingredient. 🚮

### Recipe-Ingredient Mapping

- **POST** `/api/recipes/{recipe_id}/ingredients/` - Add ingredients to a specific recipe. 🧑‍🍳

## 🧪 Running Tests

To run the test suite for the project:

```bash
python manage.py test
```

## 🤝 Contributing

We welcome contributions! If you'd like to contribute to this project, please fork the repository and create a pull request with your changes.

### Steps to contribute

1. Fork the repository. 🍴
2. Create a feature branch: `git checkout -b feature/your-feature`. 🌱
3. Commit your changes: `git commit -am 'Add your feature'`. 📦
4. Push to the branch: `git push origin feature/your-feature`. ⬆️
5. Create a new Pull Request. 🔃

## 📜 License

This project is licensed under the MIT License ⚖️

## 💡 Acknowledgements

- **Django REST Framework** for making API development easier. 👨‍💻
- **JWT** for handling authentication securely. 🔒

