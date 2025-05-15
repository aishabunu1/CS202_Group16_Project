Project Structure: 
CS202_Group16_Project/
│
├── static/                           # Static files
│   ├── css/
│   │   ├── style.css                 # Main styles
│   │   └── responsive.css            # Mobile styles (optional)
│   │
│   ├── js/
│   │   ├── cart.js                   # Cart functionality
│   │   └── search.js                 # Live search (optional)
│   │
│   └── images/                       # Menu item images
│       ├── kebap1.jpg                # Sample images (add all 15+)
│       └── pizza1.jpg
│
├── templates/                        # All HTML templates
│   ├── auth/
│   │   ├── login.html                # DONE (provided)
│   │   └── register.html             # DONE (provided)
│   │
│   ├── customer/
│   │   ├── dashboard.html            # Restaurant listings
│   │   ├── restaurants.html          # Search results
│   │   ├── menu.html                 # Menu with add-to-cart
│   │   ├── cart.html                 # Order summary
│   │   ├── orders.html               # Order history
│   │   └── rate.html                 # Rating form
│   │
│   ├── manager/
│   │   ├── dashboard.html            # Restaurant overview
│   │   ├── menu.html                 # Menu management
│   │   ├── orders.html               # Order status
│   │   └── statistics.html           # Sales analytics
│   │
│   ├── base.html                     # DONE (provided)
│   └── 404.html                      # Error page (optional)
│
├── database/
│   ├── db_connection.py              # DONE (provided)
│   └── triggers.sql                  # Discount/rating validation
│
├── models/                           # Database operations
│   ├── user.py                       # DONE (provided)
│   ├── restaurant.py                 # DONE (provided)
│   ├── menu.py                       # DONE (provided)
│   ├── order.py                      # DONE (provided)
│   └── rating.py                     # DONE (provided)
│
├── utils/                            # Helper functions
│   ├── auth.py                       # DONE (provided)
│   └── helpers.py                    # DONE (provided)
│
├── requirements.txt                  # DONE (provided)
├── app.py                            # DONE (provided)
│
├── reports/                          # Project documentation
│   ├── Part1_Report.pdf              # Your submitted Part 1
│   └── Part2_Report.pdf              # New report with:
│       - Work division
│       - Screenshots
│       - Demo explanation
│
├── sql/                              # Database files
│   ├── OnlineFoodOrderingSystemDDL.sql  # DONE (provided)
│   └── OnlineFoodOrderingSystemDML.sql  # DONE (provided)
│
└── README.md                         # Setup instructions
