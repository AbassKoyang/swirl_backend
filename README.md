# Swirl Backend

A comprehensive Django REST Framework backend for a social media/blogging platform similar to Twitter/Medium. This backend provides APIs for user management, posts, comments, reactions, bookmarks, search, feeds, notifications, and more.

## 🚀 Feature

### Core Features
- **User Authentication & Management**
  - JWT-based authentication
  - User registration and profile management
  - Google OAuth integration
  - Password reset functionality

- **Blog/Post Management**
  - Create, read, update, and delete posts
  - Post categories and tags
  - Draft and published status
  - Post views tracking
  - Rich content support

- **Social Interactions**
  - Comments and replies (nested comments)
  - Reactions (upvote/downvote) on posts and comments
  - Bookmarks for saving posts
  - Follow/unfollow users
  - View counts for posts and comments

- **Search Functionality**
  - Search posts by title, content, author, category, tags
  - Search comments by content, user, post
  - Search user bookmarks
  - Advanced filtering and ordering

- **Feed System**
  - Personalized feed (posts from followed users)
  - Trending feed (popular posts by engagement)
  - Recent feed (latest posts)
  - Combined feed (personalized + trending)

- **Notifications**
  - In-app notifications
  - Email notifications (HTML templates)
  - Push notifications (Firebase Cloud Messaging)
  - Real-time notification tracking

- **Rate Limiting**
  - Per-endpoint throttling
  - Different limits for authenticated/anonymous users
  - Prevents API abuse

## 🛠️ Tech Stack

- **Framework**: Django 6.0
- **API**: Django REST Framework 3.16
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Push Notifications**: Firebase Admin SDK
- **CORS**: django-cors-headers
- **Environment Variables**: python-decouple

## 📋 Prerequisites

- Python 3.8+
- pip or pipenv
- Firebase account (for push notifications)
- SMTP server credentials (for email notifications)

## 🔧 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd swirl-backend
```

### 2. Create virtual environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using pipenv
pipenv install
pipenv shell
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
FRONTEND_URL=http://localhost:3000
```

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Run development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## ⚙️ Configuration

### Email Configuration

Update `config/settings.py` for production:

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"
DEFAULT_FROM_EMAIL = "noreply@swirl.com"
```

### Firebase Configuration (Push Notifications)

1. Download Firebase service account credentials JSON
2. Save to `config/firebase-credentials.json`
3. Add to `.gitignore`
4. Update `config/settings.py`:

```python
FIREBASE_CREDENTIALS_PATH = BASE_DIR / 'config' / 'firebase-credentials.json'
```

See `NOTIFICATION_SETUP.md` for detailed setup instructions.

## 📚 API Endpoints

### Authentication

```
POST   /api/auth/register/              - Register new user
POST   /api/auth/token/                 - Login (get JWT token)
POST   /api/auth/token/refresh/        - Refresh JWT token
POST   /api/auth/google_login/          - Google OAuth login
POST   /api/auth/password-reset/        - Request password reset
POST   /api/auth/password-reset/confirm/ - Confirm password reset
```

### Users

```
GET    /api/users/<id>/                 - Get user profile
PUT    /api/users/<id>/update/          - Update user profile
DELETE /api/users/<id>/delete/          - Delete user account
GET    /api/users/<id>/bookmarks/       - Get user bookmarks
POST   /api/users/<id>/follow/          - Follow user
DELETE /api/users/<id>/follow/         - Unfollow user
GET    /api/users/<id>/followers/      - Get user followers
GET    /api/users/<id>/following/      - Get users following
```

### Posts

```
GET    /api/posts/                      - List posts (with filters)
POST   /api/posts/                      - Create post
GET    /api/posts/<id>/                 - Get post details
PUT    /api/posts/<id>/update/          - Update post
DELETE /api/posts/<id>/delete/          - Delete post
GET    /api/posts/<id>/comments/         - Get post comments
POST   /api/posts/<id>/comments/         - Create comment
GET    /api/posts/<id>/reactions/       - Get post reactions
POST   /api/posts/<id>/reactions/       - React to post
POST   /api/posts/<id>/bookmark/        - Bookmark post
```

### Comments

```
GET    /api/comments/<id>/              - Get comment details
PUT    /api/comments/<id>/update/       - Update comment
DELETE /api/comments/<id>/delete/       - Delete comment
GET    /api/comments/<id>/replies/      - Get comment replies
POST   /api/comments/<id>/replies/      - Reply to comment
GET    /api/comments/<id>/reactions/    - Get comment reactions
POST   /api/comments/<id>/reactions/    - React to comment
```

### Search

```
GET    /api/search/posts/               - Search posts
       ?q=query&status=published&category=tech
GET    /api/search/comments/             - Search comments
       ?q=query&post=1&user=2
GET    /api/search/bookmarks/           - Search bookmarks
       ?q=query
```

### Feeds

```
GET    /api/feeds/personalized/          - Personalized feed (authenticated)
GET    /api/feeds/trending/              - Trending posts
       ?period=24h (1h, 24h, 7d, 30d)
GET    /api/feeds/recent/                - Recent posts
GET    /api/feeds/combined/              - Combined feed (authenticated)
```

### Notifications

```
GET    /api/notifications/               - List notifications
POST   /api/notifications/<id>/read/     - Mark notification as read
POST   /api/notifications/push-token/    - Register push token
DELETE /api/notifications/push-token/<token>/ - Unregister push token
```

### Categories

```
GET    /api/categories/                  - List categories
POST   /api/categories/                  - Create category
```

## 📁 Project Structure

```
swirl-backend/
├── apps/
│   ├── core/                    # User management, authentication
│   │   ├── models.py            # User, Follow models
│   │   ├── views.py             # Auth, user, follow views
│   │   ├── serializers.py       # User serializers
│   │   ├── throttles.py        # Rate limiting
│   │   └── urls.py
│   │
│   ├── blogs/                    # Posts, comments, reactions, bookmarks
│   │   ├── models.py            # Post, Comment, Reaction, Bookmark
│   │   ├── views.py             # CRUD operations
│   │   ├── serializers.py       # Serializers
│   │   ├── throttles.py         # Rate limiting
│   │   └── urls.py
│   │
│   ├── search/                   # Search functionality
│   │   ├── views.py             # Search views
│   │   ├── throttles.py         # Rate limiting
│   │   └── urls.py
│   │
│   ├── feeds/                    # Feed system
│   │   ├── views.py             # Feed views
│   │   ├── throttles.py         # Rate limiting
│   │   └── urls.py
│   │
│   └── notifications/            # Notifications
│       ├── models.py            # Notification, PushToken models
│       ├── views.py             # Notification views
│       ├── services.py          # Email & push services
│       ├── utils.py             # Notification helpers
│       ├── serializers.py       # Serializers
│       ├── throttles.py         # Rate limiting
│       └── urls.py
│
├── config/                       # Django settings
│   ├── settings.py              # Main settings
│   ├── urls.py                  # URL configuration
│   └── firebase_config.py       # Firebase setup
│
├── templates/                     # Email templates
│   └── notifications/
│       └── emails/
│
├── manage.py
├── requirements.txt
├── Pipfile
├── .env                          # Environment variables (create this)
└── README.md
```

## 🔐 Authentication

All protected endpoints require JWT authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your-access-token>
```

### Getting a Token

```bash
# Register
POST /api/auth/register/
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}

# Login
POST /api/auth/token/
{
  "email": "user@example.com",
  "password": "securepassword"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 📝 Usage Examples

### Create a Post

```bash
POST /api/posts/
Authorization: Bearer <token>
{
  "title": "My First Post",
  "content": "This is the content of my post",
  "category_id": 1,
  "status": "published"
}
```

### Follow a User

```bash
POST /api/users/2/follow/
Authorization: Bearer <token>
```

### Search Posts

```bash
GET /api/search/posts/?q=django&status=published&category=tech
```

### Get Personalized Feed

```bash
GET /api/feeds/personalized/
Authorization: Bearer <token>
```

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run specific app tests
python manage.py test apps.blogs
```

## 🚦 Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 3-5 requests/minute
- **Read operations**: 50-100 requests/minute
- **Write operations**: 10-60 requests/minute (varies by endpoint)
- **Search/Feed**: 20-60 requests/minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

## 📧 Notifications

Notifications are automatically created for:
- User follows
- Comments and replies
- Reactions
- Bookmarks
- User registration/login

See `NOTIFICATION_SETUP.md` for email and push notification configuration.

## 🔒 Security Features

- JWT authentication
- Password hashing
- CORS configuration
- Rate limiting
- Input validation
- SQL injection protection (Django ORM)
- XSS protection

## 📦 Dependencies

Key dependencies:
- Django 6.0
- djangorestframework 3.16
- djangorestframework-simplejwt 5.5
- django-cors-headers 4.9
- firebase-admin 7.1
- python-decouple 3.8

See `requirements.txt` for complete list.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database (development only)
python manage.py flush
python manage.py migrate
```

### Migration Issues
```bash
# Create new migrations
python manage.py makemigrations
python manage.py migrate
```

### Email Not Sending
- Check SMTP settings in `settings.py`
- Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
- Check spam folder
- Review console logs (if using console backend)

### Push Notifications Not Working
- Verify Firebase credentials file exists
- Check Firebase project configuration
- Ensure device token is registered
- Review Firebase Console for errors

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review `NOTIFICATION_SETUP.md` for notification setup

## 🎯 Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Advanced analytics and insights
- [ ] Content moderation features
- [ ] Image upload and storage
- [ ] Advanced search with Elasticsearch
- [ ] API documentation with Swagger/OpenAPI

## 🙏 Acknowledgments

- Django REST Framework team
- Firebase team
- All contributors

---

Made with ❤️ using Django
