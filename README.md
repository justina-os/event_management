# Event Management API

A backend project built using FastAPI and MySQL to practice REST API development, JWT authentication, authorization, and business logic implementation.

## Project Overview

The application supports two types of users:

- Organizer
- Attendee

Organizers can create and manage events, while attendees can browse and register for published events.

## Features

### Authentication
- User Signup
- User Login
- JWT Authentication
- Password Hashing using bcrypt

### Organizer
- Create events
- Update own events
- Delete own events
- View all events

### Attendee
- View available events
- Register for events
- Cancel registrations

## Business Rules Implemented

- Only organizers can create events.
- Organizers can only update or delete their own events.
- Registration is allowed only for published events.
- Users cannot register twice for the same event.
- Registration is blocked after the registration deadline.
- Event capacity cannot become negative.
- Registration deadline must be less than or equal to the event date.
- Events with registrations can only have their status updated.
- JWT authentication is required for protected routes.

## Technologies Used

- Python
- FastAPI
- MySQL
- Pydantic
- JWT (python-jose)
- Passlib (bcrypt)

## API Endpoints

### Authentication
- POST `/signin`
- POST `/login`

### Events
- GET `/events`
- POST `/events`
- PATCH `/events/{event_id}`
- DELETE `/events/{event_id}`

### Registration
- POST `/events/{event_id}/register`
- DELETE `/events/{event_id}/register`

