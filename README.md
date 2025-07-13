# Social-Platform-in-Django
SocialSphere — A Scalable Social Media Platform

A fully functional, visually modern **social media web app** built with Django. This platform supports everything from user profiles and direct messages to post likes, comments, and an admin moderation panel.

![Home Page](ScreenShots/home_page.png)

---

## 🚀 Features

### 👥 User System
- Profile creation and editing (bio, profile picture, email)
- Followers/Following system
- Clickable usernames linking to profiles
- Join date display
- Custom user model with extended fields

![Profile Page](ScreenShots/profile_page.png)

---

### 📝 Posts
- Create posts with text + optional image
- Displayed on feed, profile, and explore pages
- Like posts with ❤️ icon (real-time count)
- Inline comment system
- Edit/Delete own posts
- Humanized timestamps
- Post counts on profile

![Create Post](ScreenShots/create_post_page.png)

---

### 💬 Comments
- Add and display comments inline
- Humanized timestamps
- Graceful handling of no comments

![Comments](ScreenShots/comment_report.png)

---

### ❤️ Likes
- Like button on all posts
- Live like count via Django ORM
- Many-to-many relationship
- (Future: "Liked by you" UI badge)

---

### ✉️ Messaging
- DM system between users
- Threaded conversation view
- Time-stamped messages

![Messages](ScreenShots/chat_messages_page.png)

---

### 🛡️ Reporting & Moderation
- Report inappropriate posts
- Prevent duplicate reports
- Admin panel for resolving reports
- Status display & user feedback

![Admin Panel - Reports](ScreenShots/private-admin_reports.png)

---

### 🧑‍💼 Admin Dashboard
- View all reports
- Resolve with a single click
- Flash message confirmations
- Staff-only access protected

![Admin Dashboard](ScreenShots/private-admin_home.png)

---

### 🔐 Authentication & Access Control
- Secure Login / Logout
- Restriction based on roles (owner-only edit/delete, staff-only admin)
- CSRF protection on all POST forms

---

### 🎨 UX & Frontend
- Responsive layout with Tailwind CSS-inspired utility classes
- Clean modular templates
- Toast messages using Django’s `messages` framework
- Dynamic navbar, reusable footer

---

## 🧱 Project Structure

