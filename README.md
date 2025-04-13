# Flask Blogging Platform

A full-featured blogging platform with admin controls, user authentication, and image uploads.

##  Technologies Used
- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLAlchemy ORM
- **Image Processing**: Pillow

##  Key Features
- Admin dashboard for content management
- User authentication system
- Image uploads with automatic resizing
- Responsive design for all devices
- Post creation/editing with rich text
- Lightbox image viewer

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/flask-blog.git
   cd flask-blog
   ```
2. Install dependencies:
```
   pip install -r requirements.txt 
```
3. Run
```
   python app.py
```
4. Admin Access
   Default credentials:
   ```
   Username: admin
   Password: admin123
   ```
5. To update credentials:
Make a .env file with credentials guided in the terminal and an example is given in .envexample. <br>
Edit ADMIN_USERNAME and ADMIN_PASSWORD in a .env file <br>
Restart server - old credentials will be invalidated automatically<br>
