# P2P Book Exchange
This application facilitates peer-to-peer book exchanges. Users can create an account, build their book library, and request books from other users. Additionally, the platform includes a rating system for both users and books.

Designed to streamline the book exchange process, this application aims to make book sharing more engaging and inclusive.

# Setup
This project comprises both backend and frontend components. The backend is built using Flask, while the frontend is a React application. The database used is SQLite, and the application is hosted locally.

Requirements:
- Python 3.12.2
- npm 10.5.0

## Backend
The full API reference is available here: https://chellani.notion.site/P2P-Book-Exchange-API-Reference-0c6be3ff363940a1812191c0676a4bfd?pvs=4

To setup, navigate to the `backend/app` directory and run the following commands:
```
pip install -r requirements.txt
python app.py
```

## Frontend
To setup, navigate to the `frontend/p2p-book-exchange` directory and run the following commands:
```
npm install
npm start
```

## Setup Caveats
- The backend server runs on `http://localhost:5000` and the frontend runs on `http://localhost:3000`. During development, I used chrome in unsafe mode to allow CORS requests, and did not manage to fix this issue. It should be a straightforward fix, which I'll try debugging later on. But in the meanwhile, if you encounter CORS issues, please use chrome in unsafe mode, or try with a different browser.
    - https://medium.com/@dmadan86/run-chrome-browser-without-cors-by-disabling-web-security-d124ad4dd2cf
- The backend server uses an open API key, which I will share via email. 
    - This can be set to the system environment variable `OPEN_API_KEY` or hardcoded in the `recommendation_engine.py` file.
    - eg: `export OPEN_API_KEY=<your_key>` in the same directory as the `app.py` file.

- Also, if your backend server is running on a different port, please replace the harcoded port number in the frontend source files. I'll try put this in a config file in the future.

## Solution Approach and Design

Given that the 3 key pillars of the are:
- Easy Searching of Books
- Easy Listing of Books
- Easy Exchanging of Books

I prioritised features that encompass as much of these as possible, while still trying to achieve a minimum viable product in terms of usability and functionality.

As such, the key features of the application are:

## User Lifecycle

I recommend running this endpoint before testing out everything: https://chellani.notion.site/Example-Request-Body-for-Bulk-Add-Books-8e7df73bc14d485b9fe68ba546e121aa

Otherwise, you can also add books one by one in the frontend.

- Registration/Login
    - I kept this barebones, with just a username and password. I would have liked to add a proper auth system, but I prioritised other features for this POC, as registration/login is a solved problem and might not be the most essential in demonstrating the product-market fit.
- User Profile and Control Center
    Here, I took inspiration from existing successful P2P platforms such as Carousell, where the user's home page has a lot of information pertaining to the user's activity on the platform. This helps act as a control center for the user, and also helps in user engagement.
    - Users can view their profile, and see their ratings and books.
    - Users can also add books, and manage the lifecycle of their exchanges - accept, reject, or relist books.
    - Users can rate books that they currently have. They can also relist books that they have read.
    Generally, the user profile is where users can view manage a repository of their own books and ratings, abd view exchanges that they are part of.

## Book Lifecycle
- Books in the app are modelled to change hands, and thus exist in only two states - in the user's library, or in the process of being exchanged. Exchanges are modelled as a separate entity, and are created when a user requests a book from another user.
- There is a centralised book listing, where users can view and filter books, and add books to their wishlist or request to borrow the book. Presently, once the user requests a book, the book is instantly reserved to avoid a race condition and enters a pending transaction state. The user who owns the book can then accept or reject the request (while I implemented accept, reject is still pending)

## Recommendation System (AI-enabled feature)
- Recommendation system that uses OpenAI API to recommend available books to users based on their tastes. 
- I engineered the prompt to take in a list of books ordered by the user's preference, and match the remaining books available in the exchange to the user's preferences. This is a simple implementation, and can be improved by using more sophisticated models and data. 
    - The key point here is to increase listing-relevance on an individual level, and to increase user engagement by providing a more personalised experience.

## Ratings System
- Users can rate books and other users. As a community driven platform, prioritising listings by crowd opinion is, in the best case scenario, going to lead to higher levels of engagement and user satisfaction. As such, this feature is centered around prioritising listings by ratings. So far, this is a backend-only implementation, and I did not manage to integrate it into the frontend.

### User Journey
**Initial**
- A new user will sign up with a username and password. They will be assigned a unique user id which becomes their identity on the platform.
- The user can then add books to their library, and view books available for exchange. They can also add items in bulk to their library.
- The user can rate any number of items in their library.
- In the exchange, the user can view the list of available books, and request to borrow a book. The book is then reserved for the user, and the user can view the status of the exchange in their control center.

**Intermediate**
- The requested book is listed in the user's control center, and the user can view the status of the exchange.
- It is set to PENDING, as this represents the user physically going to the owner to borrow the book.
- The owner and user can then accept or reject the request. If accepted, the book is transferred to the user's library, and the exchange is marked as complete.
- The users can rate each other, and the book.

**Advanced**
- The user can read the book, and relist it in the exchange. The user can also rate the book.
- While looking for the new book, the user can explore recommendations that are dynamically generated based on the their preferences.
- Here, they can add books to their wishlist. 

## Future plans

The UI/UX of the application is still very basic, and can be improved. I would like to add more features to the frontend, such as a more interactive user profile, and a more intuitive book listing page, which overall lesser cognitive load on the user. However, I prioritised the backend features for this POC to demonstrate the core functionalities of the application.

Besides this, to make this a more robust and well-rounded platform, some features that can be added are:

1. An in-app notifications system
    - A Pub/Sub system that notifies users of new exchanges, ratings, and recommendations.
    - Can be built using Redis over Websockets. 
    - Each user is subscribed to a channel, and is notified of new events in real-time.
2. Location-based filtering and sorting
    - Taking inspiration from existing p2p apps again, location-based convenience is a key point of contention when it comes to user-adoption, and therefore is an essential feature.
3. More informative listings
    - Currently, the listings are barebones. Adding more information about the book, such as page length, genre, and a brief description, can help users make more informed decisions.
    - This can be done using the Google Books API, or equivalent. 
4. In-app book forums
    - Mirrors interest groups in real life. 
    - Given that we are trying to build a community of readers, and encourage people to pick up books, this can be a great feature, as it increases user engagement and over time might create a sense of belonging towards the platform.
5. More sophisticated AI features
    - Stuff such as summaries, better recommendations using larger prompts or more sophisticated models, and even a chatbot that can help users navigate the platform.
6. Proper Auth system
    - Currently, the auth system is barebones. A proper auth system with JWT tokens and refresh tokens can be implemented.



## Milestones

With the future work in mind, I would like to set the following milestones for the project:

1. **Milestone 1: Basic MVP**
    - A basic MVP that has the core functionalities of the application, and is usable by a small group of users.
    - This includes the user lifecycle, book lifecycle, and the recommendation system.
    - This milestone is already largely achieved.
    - Auth and user management would be a good value add here.
2. **Milestone 2: UI/UX Improvements**
    - A more intuitive and engaging UI/UX that reduces cognitive load on the user.
    - This includes a more interactive user profile, and a more informative book listing page.
3. **Milestone 3: Advanced Features**
    - The advanced features mentioned above, such as in-app notifications, location-based filtering, and in-app book forums.
    - This milestone is where the platform becomes more robust and well-rounded.
4. **Milestone 4: AI Improvements**
    - More sophisticated AI features, such as summaries, better recommendations, and a chatbot.
    - This milestone is where the platform becomes more intelligent and user-friendly.
