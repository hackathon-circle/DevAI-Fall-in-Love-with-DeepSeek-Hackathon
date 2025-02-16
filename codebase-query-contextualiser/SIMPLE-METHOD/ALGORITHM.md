## Algorithm

### Methods
- file traversal
- reading: get relevant files
- file reading
- get relevant lines
- create query + context request body


## Example

Q: Change footer color to red.

```
file_traversal
sameple-codebase/
├── index.html
└── styles
    └── main.css
```

file_reading:

```
content:
sameple-codebase/index.html
42  <footer class="main-footer">
43      <p>&copy; 2024 Your Company. All rights reserved.</p>
4  </footer>
sample-codebase/styles/main.css
70  .main-footer {
71      background-color: #333;
72      color: white;
72      text-align: center;
72      padding: 1rem;
72      position: fixed;
72      bottom: 0;
72      width: 100%;
72  }
```

Final response:

```
<QUERY>
Change footer color to blue.
</QUERY>

<CODE_TO_CHANGE>
    <FILE_PATH>
        sample-codebase/index.html
    </FILE_PATH>
    <CODE>
        42  <footer class="main-footer">
        43      <p>&copy; 2024 Your Company. All rights reserved.</p>
        4  </footer>
    </CODE>

    <FILE_PATH>
        sample-codebase/styles/main.css
    </FILE_PATH>
    <CODE>
        70  .main-footer {
        71      background-color: red;
        72  }
    </CODE>
</CODE_TO_CHANGE>

<INSTRUCTION>
    Response like thie
    <DESCRIPTION>
    description here
    </DESCRIPTION>
    <CHANGE>
        <FILE_PATH>
        fine name here
        </FILE_PATH>
        42  <footer class="main-footer"> // UPDATE CODE HERE
    </CHANGE>
</INSTRUCTION>
```
