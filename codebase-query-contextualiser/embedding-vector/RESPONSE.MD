ase-query-contextualiser$ python camel/jina.py 
/home/neosoft/.cache/huggingface/modules/transformers_modules/jinaai/jina-bert-v2-qk-post-norm/3baf9e3ac750e76e8edd3019170176884695fb94/configuration_bert.py:29: UserWarning: optimum is not installed. To use OnnxConfig and BertOnnxConfig, make sure that `optimum` package is installed
  warnings.warn("optimum is not installed. To use OnnxConfig and BertOnnxConfig, make sure that `optimum` package is installed")
Processed: sameple-codebase/index.html
Processed: sameple-codebase/styles/main.css

=== Jina Code Search Demo ===


Query: Show me the navigation menu structure
/home/neosoft/test/codebase-query-contextualiser/camel/jina.py:181: DeprecationWarning: `search` method is deprecated and will be removed in the future. Use `query_points` instead.
  results = self.client.search(

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for nav ul

Code Preview: 

nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 2rem;
}...

2. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML body element and its contents

Code Preview: <body>
    <header class="main-header">
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href...

==================================================

Query: Find the contact form HTML

Top Results:

1. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML section element and its contents

Code Preview: <section id="contact">
            <h2>Contact Us</h2>
            <form id="contact-form">
                <input type="text" placeholder="Name" required>
                <input type="email" placehol...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for /* Form styles */
#contact-form

Code Preview: 

/* Form styles */
#contact-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 500px;
    margin: 0 auto;
}...

==================================================

Query: What's in the footer section?

Top Results:

1. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML footer element and its contents

Code Preview: <footer class="main-footer">
        <p>&copy; 2024 Your Company. All rights reserved.</p>
    </footer>...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for /* Footer styles */
.main-footer

Code Preview: 

/* Footer styles */
.main-footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 1rem;
    position: fixed;
    bottom: 0;
    width: 100%;
}...

==================================================

Query: How is the navigation styled?

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for nav a

Code Preview: 

nav a {
    color: white;
    text-decoration: none;
}...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for nav ul

Code Preview: 

nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 2rem;
}...

==================================================

Query: What are the form input styles?

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for input, textarea

Code Preview: 

input, textarea {
    padding: 0.5rem;
    border: 1px solid #ddd;
}...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for /* Form styles */
#contact-form

Code Preview: 

/* Form styles */
#contact-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 500px;
    margin: 0 auto;
}...

==================================================

Query: Show me all button styles

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for button

Code Preview: 

button {
    background-color: #333;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    cursor: pointer;
}...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for nav a

Code Preview: 

nav a {
    color: white;
    text-decoration: none;
}...

==================================================

Query: What's the color scheme?

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for button

Code Preview: 

button {
    background-color: #333;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    cursor: pointer;
}...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for nav a

Code Preview: 

nav a {
    color: white;
    text-decoration: none;
}...

==================================================

Query: How is the header implemented and styled?

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for /* Header styles */
.main-header

Code Preview: 

/* Header styles */
.main-header {
    background-color: #333;
    padding: 1rem;
}...

2. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML body element and its contents

Code Preview: <body>
    <header class="main-header">
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href...

==================================================

Query: Show me everything related to forms

Top Results:

1. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML section element and its contents

Code Preview: <section id="contact">
            <h2>Contact Us</h2>
            <form id="contact-form">
                <input type="text" placeholder="Name" required>
                <input type="email" placehol...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for /* Form styles */
#contact-form

Code Preview: 

/* Form styles */
#contact-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 500px;
    margin: 0 auto;
}...

==================================================

Query: Find responsive design related code

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for /* Main content styles */
main

Code Preview: 

/* Main content styles */
main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for *

Code Preview: * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}...

==================================================

Query: Where is user interaction handled?

Top Results:

1. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML section element and its contents

Code Preview: <section id="contact">
            <h2>Contact Us</h2>
            <form id="contact-form">
                <input type="text" placeholder="Name" required>
                <input type="email" placehol...

2. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML main element and its contents

Code Preview: <main>
        <section id="home">
            <h1 class="main-heading">Welcome to Our Website</h1>
            <p>This is a sample website to demonstrate code search functionality.</p>
        </sect...

==================================================

Query: Show me the main content area

Top Results:

1. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML main element and its contents

Code Preview: <main>
        <section id="home">
            <h1 class="main-heading">Welcome to Our Website</h1>
            <p>This is a sample website to demonstrate code search functionality.</p>
        </sect...

2. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML section element and its contents

Code Preview: <section id="about">
            <h2>About Us</h2>
            <p>We are a company dedicated to making code navigation easier</p>
        </section>...

==================================================

Query: Find code related to layout structure

Top Results:

1. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML section element and its contents

Code Preview: <section id="about">
            <h2>About Us</h2>
            <p>We are a company dedicated to making code navigation easier</p>
        </section>...

2. FILE: sameple-codebase/index.html
TYPE: html
CONTEXT: HTML main element and its contents

Code Preview: <main>
        <section id="home">
            <h1 class="main-heading">Welcome to Our Website</h1>
            <p>This is a sample website to demonstrate code search functionality.</p>
        </sect...

==================================================

Query: Find all flex layouts

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for /* Form styles */
#contact-form

Code Preview: 

/* Form styles */
#contact-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 500px;
    margin: 0 auto;
}...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for nav ul

Code Preview: 

nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 2rem;
}...

==================================================

Query: Show me media queries

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for nav ul

Code Preview: 

nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 2rem;
}...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for *

Code Preview: * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}...

==================================================

Query: List all CSS selectors for interactive elements

Top Results:

1. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for input, textarea

Code Preview: 

input, textarea {
    padding: 0.5rem;
    border: 1px solid #ddd;
}...

2. FILE: sameple-codebase/styles/main.css
TYPE: css
CONTEXT: CSS styles for *

Code Preview: * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}...

==================================================