<div align="center">
    <br>
    <img src="./assets/logo.jpeg" width="200" alt="Limbo" />
    <br>
    <br>
    <h2>🔮 Limbo nodes.</h2>
    <h4>JiT interpreted and compiled, node-based programming environment.</h4>
</div>

![App](https://raw.githubusercontent.com/7hebel/limbo/refs/heads/main/assets/ss-app.png)

<div align="center">
    <br>
    <h2>✨ Features</h2>
</div>

- 🏃 Just-in-time interpreted

- 🛠️ Compilable to .exe

- 📄 No-code programming.

- ⌨️ Intuitive keyboard shortcuts.

<div align="center">
    <br>
    <h2>🪲 Debugger</h2>
</div>

![App](https://raw.githubusercontent.com/7hebel/limbo/refs/heads/main/assets/ss-debugger.png)

<div align="center">
    <br>
    <h2>📦 Install</h2>
</div>

1. Ensure [Python](https://www.python.org/downloads/) is installed and added to PATH.

2. Clone repository:
   
   ```bash
   git clone https://github.com/7hebel/limbo.git
   ```
   
   or download as a ZIP.

3. Install required dependencies:
   
   Open shell and navigate to limbo's directory.
   
   ```bash
   pip install -r requirements.txt
   ```

4. Run limbo:
   
   ```bash
   py main.py  (replace py with python3 on linux)
   ```

<div align="center">
    <br>
    <h2>👁️ User Interface</h2>
</div>

### 1. Sidebar

Sidebar is located on the left side of the app and contains all the available nodes. It is used to spawn new instances of nodes to use in the program. 

##### 🧭 Navigation.

To access sidebar, press `tab`. Then, it should be focused.

Navigate through the nodes using `up/down arrows` and `ctrl + up/down` to skip entire collection. Fold collections with `left/right arrows` and spawn node with `enter` or `space`.

You can fold entire sidebar using `ctrl + b`

##### ✨ Icons.

Next to the node's title is located a **output-based icon**:

- `ƒ` - **Function node** - returns a value (color represents data type)

- `λ` - **Flow node** - doesn't return any value but provides a Flow output.

- ` ` - **Exit node** - if there is not icon, node does not provide any output and will end program's flow.

### 2. Viewport

It contains almost entire screen's space and is used to display and manage nodes. Here You can move, connect, delete and setup all nodes.

##### 🧭 Navigation.

You can move camera using `ctrl + arrow` or move individual, selected node with `alt + arrow`. To select node, shift focus from other nodes with `arrow`. The algorithm will choose the next closest node in given direction. **Selected node** outline in it's color and all wires connecting this node will be undimmed. 

##### 📝 Editing nodes.

Spawn new nodes from sidebar. To enter `EDIT NODE` mode press `enter`. Use `arrows` to shift focus between sources. To connect sources, press `space` on selected source and navigate to it's target source in other node. Choose destination source and press `space` again to connect endpoints. Remember that both sources must have same data type (color). To set a **constant value** press `c` on selected `input` source and type a correct value. Exit `EDIT MODE` with `esc`.

##### 🗃️ Workspace.

You can export current state using `ctrl + e` and import with `ctrl + i`. If there is no file associated with this workspace, You will be asked to provide name (path). Close current workspace with `ctrl + w`

##### 👟 Run program.

Press `F1` to run current program starting from a `START` node. You can also compile program to a `.exe` with `F2` (it should take ~30s). There is also a built-in debugger (start with `F12`) that will run the interpreted version of program but will also display current state of the interpreter. 

### 3. Status bar

Below the main viewport, You can see the status bar displaying either feedback from Your previous actions (like saving file or altering a node) or keyboard shortcuts available in the current mode.

<div align="center">
    <br>
    <h2>🔢 Data types</h2>
</div>

Data type describes type of data stored inside source. They can be distinguished by a color and name. There are 4 data types in Limbo.

- `TEXT` (yellow) - Represents standard text provided by user or set as a constant value.

- `NUMBER` (purple) - Represents number and is used for mathematical operations. (all numbers are treated as a floating-point)

- `BOOLEAN` (blue) - Logical value, either True or False.

- `FLOW` (red) - Special type not representing actual data but a runtime flow. It is used to point next node that should be executed without passing any input data to it.

##### 🔁 Cast types.

Use nodes from the `Cast` collection to switch data types. It is not always possible to cast text to a number, as text may contain invalid characters. Transformer will try to use all numbers and skip text characters but it still may fail, that's why You can provide `default` value that will be used instead. When conversion fails and the `default` value is not provide, program will crash with a `ERROR` status.

<div align="center">
    <br>
    <h2>🧠 Memory</h2>
</div>

There is entire collection of nodes called `Memory`. It adds variable-like storage to the program. At the start of the program, new **memory jar** is created. A memory jar provides key-value storage similar to JSON. The `RESTART` node has a `Save memory` boolean input that if set to True, will not flush current memory state but start program with current memory jar.

<div align="center">
    <br>
    <h2>⛔ Exit codes</h2>
</div>

Your program may exit with a different code just like all executables. All codes greater or equal 0 are considered as a `success` and negative codes means `fail`. The exit code defines reason of exit.

Default codes:

- `0` - OK

- `-1` - Runtime error.

- `-2` - Infinite recursion terminated.

- `-3` - Manual termination.

- `10` - Restart program

- `11` - Restart program and save memory

The `RESTART` node does the same thing as a `EXIT` with code set to either `10` or `11`.
