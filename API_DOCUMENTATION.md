# API Documentation

## Overview

The Django Blog Recommendation System provides a comprehensive RESTful API that allows developers to integrate blog functionality into their applications. The API is built using Django REST Framework and follows REST conventions.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. To access protected endpoints, you need to include the JWT token in the Authorization header.

### Getting a Token

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
    }
}
```

### Using the Token

Include the token in the Authorization header for all authenticated requests:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Endpoints

### Authentication Endpoints

#### Login
- **URL:** `/api/auth/login/`
- **Method:** `POST`
- **Description:** Authenticate user and get JWT tokens
- **Authentication:** Not required

#### Logout
- **URL:** `/api/auth/logout/`
- **Method:** `POST`
- **Description:** Logout user (invalidate token)
- **Authentication:** Required

#### Token Refresh
- **URL:** `/api/auth/token/refresh/`
- **Method:** `POST`
- **Description:** Refresh access token using refresh token
- **Authentication:** Not required

### Blog Posts

#### List Posts
- **URL:** `/api/posts/`
- **Method:** `GET`
- **Description:** Get list of all blog posts
- **Authentication:** Not required
- **Query Parameters:**
  - `category` - Filter by category ID
  - `tag` - Filter by tag name
  - `author` - Filter by author ID
  - `search` - Search in title and content
  - `ordering` - Sort by field (e.g., `-created_at`)

**Response:**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Sample Blog Post",
            "content": "This is a sample blog post content...",
            "author": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com"
            },
            "category": {
                "id": 1,
                "name": "Technology",
                "description": "Tech related posts"
            },
            "tags": [
                {
                    "id": 1,
                    "name": "django"
                }
            ],
            "created_at": "2025-06-11T20:00:00Z",
            "last_modified": "2025-06-11T20:00:00Z",
            "likes_count": 5,
            "comments_count": 3,
            "is_liked": false,
            "is_saved": false,
            "base64_image": "data:image/jpeg;base64,..."
        }
    ]
}
```

#### Create Post
- **URL:** `/api/posts/`
- **Method:** `POST`
- **Description:** Create a new blog post
- **Authentication:** Required

**Request:**
```json
{
    "title": "New Blog Post",
    "content": "Content of the new blog post...",
    "category": 1,
    "tags": [1, 2, 3],
    "post_picture": "base64_encoded_image_data"
}
```

#### Get Post
- **URL:** `/api/posts/{id}/`
- **Method:** `GET`
- **Description:** Get specific blog post by ID
- **Authentication:** Not required

#### Update Post
- **URL:** `/api/posts/{id}/`
- **Method:** `PUT` or `PATCH`
- **Description:** Update specific blog post
- **Authentication:** Required (only author or admin)

#### Delete Post
- **URL:** `/api/posts/{id}/`
- **Method:** `DELETE`
- **Description:** Delete specific blog post
- **Authentication:** Required (only author or admin)

#### Like Post
- **URL:** `/api/posts/{id}/like/`
- **Method:** `POST`
- **Description:** Like or unlike a blog post
- **Authentication:** Required

**Response:**
```json
{
    "liked": true,
    "likes_count": 6
}
```

#### Save Post
- **URL:** `/api/posts/{id}/save/`
- **Method:** `POST`
- **Description:** Save or unsave a blog post
- **Authentication:** Required

**Response:**
```json
{
    "saved": true
}
```

### Comments

#### List Comments
- **URL:** `/api/comments/`
- **Method:** `GET`
- **Description:** Get list of comments
- **Authentication:** Not required
- **Query Parameters:**
  - `post` - Filter by post ID

#### Create Comment
- **URL:** `/api/comments/`
- **Method:** `POST`
- **Description:** Create a new comment
- **Authentication:** Required

**Request:**
```json
{
    "post": 1,
    "content": "This is a great post!",
    "parent": null
}
```

#### Like Comment
- **URL:** `/api/comments/{id}/like/`
- **Method:** `POST`
- **Description:** Like or unlike a comment
- **Authentication:** Required

### Users

#### List Users
- **URL:** `/api/users/`
- **Method:** `GET`
- **Description:** Get list of users
- **Authentication:** Required (admin only)

#### User Profile
- **URL:** `/api/users/profile/`
- **Method:** `GET`, `PUT`, `PATCH`
- **Description:** Get or update current user's profile
- **Authentication:** Required

**Response:**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "profile": {
        "bio": "I'm a blog admin",
        "location": "Ukraine",
        "birth_date": "1990-01-01",
        "avatar": "base64_encoded_image",
        "followers_count": 10,
        "following_count": 5
    }
}
```

#### Follow User
- **URL:** `/api/users/{id}/follow/`
- **Method:** `POST`
- **Description:** Follow or unfollow a user
- **Authentication:** Required

### Categories

#### List Categories
- **URL:** `/api/categories/`
- **Method:** `GET`
- **Description:** Get list of all categories
- **Authentication:** Not required

**Response:**
```json
[
    {
        "id": 1,
        "name": "Technology",
        "description": "Tech related posts",
        "posts_count": 15
    }
]
```

### Tags

#### List Tags
- **URL:** `/api/tags/`
- **Method:** `GET`
- **Description:** Get list of all tags
- **Authentication:** Not required

### Search

#### Search Posts
- **URL:** `/api/search/`
- **Method:** `GET`
- **Description:** Search across posts, comments, and users
- **Authentication:** Not required
- **Query Parameters:**
  - `q` - Search query
  - `type` - Search type (posts, users, comments)

### Recommendations

#### Get Recommendations
- **URL:** `/api/recommendations/`
- **Method:** `GET`
- **Description:** Get personalized post recommendations
- **Authentication:** Required

**Response:**
```json
{
    "recommendations": [
        {
            "post": {
                "id": 1,
                "title": "Recommended Post",
                "score": 0.95
            }
        }
    ]
}
```

### Analytics

#### User Analytics
- **URL:** `/api/analytics/`
- **Method:** `GET`
- **Description:** Get user analytics data
- **Authentication:** Required

**Response:**
```json
{
    "posts_count": 10,
    "comments_count": 25,
    "likes_received": 100,
    "followers_count": 50,
    "interactions_count": 200
}
```

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
    "error": "Not found",
    "message": "The requested post does not exist",
    "code": 404
}
```

### Common Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authenticated users:** 1000 requests per hour
- **Anonymous users:** 100 requests per hour

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1623456789
```

## Pagination

List endpoints support pagination:

```json
{
    "count": 100,
    "next": "http://localhost:8000/api/posts/?page=2",
    "previous": null,
    "results": [...]
}
```

## Filtering and Sorting

### Filtering

Use query parameters to filter results:

```
GET /api/posts/?category=1&tag=django&author=2
```

### Sorting

Use the `ordering` parameter:

```
GET /api/posts/?ordering=-created_at
GET /api/posts/?ordering=title,created_at
```

## Examples

### Python (requests)

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login/', {
    'username': 'admin',
    'password': 'admin'
})
token = response.json()['access']

# Get posts
headers = {'Authorization': f'Bearer {token}'}
posts = requests.get('http://localhost:8000/api/posts/', headers=headers)

# Like a post
like_response = requests.post(
    'http://localhost:8000/api/posts/1/like/',
    headers=headers
)
```

### JavaScript (fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'admin'
    })
});
const { access } = await loginResponse.json();

// Get posts
const postsResponse = await fetch('http://localhost:8000/api/posts/', {
    headers: {
        'Authorization': `Bearer ${access}`
    }
});
const posts = await postsResponse.json();
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Get posts with token
curl -X GET http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Like a post
curl -X POST http://localhost:8000/api/posts/1/like/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
